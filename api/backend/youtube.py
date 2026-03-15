import os
import asyncio
from pathlib import Path
from datetime import datetime
import yt_dlp
from PIL import Image
import logging
import cv2
import requests
import tempfile
from ultralytics import YOLO

logger = logging.getLogger(__name__)


class YouTubeCapture:
    def __init__(self, base_dir: str = "captures"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        self.model = YOLO("/home/user/model/yolo.pt")

    def _create_folder(self, channel_name: str) -> Path:
        """Create a folder for a specific channel if it doesn't exist."""
        folder = self.base_dir / channel_name
        folder.mkdir(exist_ok=True)
        return folder

    def _extract_last_frame_from_video(self, video_path: str) -> Image.Image | None:
        """
        Extract the last frame from a video file.
        Returns a PIL Image or None if extraction failed.
        """
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logger.error(f"Failed to open video: {video_path}")
                return None

            # Get the total number of frames
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            if frame_count == 0:
                logger.error(f"No frames in video: {video_path}")
                cap.release()
                return None

            # Go to the last frame
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count - 1)
            ret, frame = cap.read()
            cap.release()

            if not ret:
                logger.error(f"Failed to read last frame from video: {video_path}")
                return None

            # Convert BGR to RGB (OpenCV uses BGR by default)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convert to PIL Image
            pil_image = Image.fromarray(frame_rgb)
            return pil_image

        except Exception as e:
            logger.error(f"Error extracting last frame from {video_path}: {e}")
            return None

    def _is_hls_url(self, url: str) -> bool:
        """Check if URL is an HLS/M3U8 stream."""
        return '.m3u8' in url.lower() or url.endswith('=m3u8_native')

    def _parse_m3u8(self, m3u8_url: str) -> list[str]:
        """
        Parse M3U8 playlist and extract segment URLs.
        Returns a list of segment URLs.
        """
        try:
            response = requests.get(m3u8_url, timeout=10)
            response.raise_for_status()

            segments = []
            base_url = m3u8_url.rsplit('/', 1)[0]

            for line in response.text.split('\n'):
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                # Parse segment URL
                if line.endswith('.ts') or line.endswith('.m4s'):
                    # Handle relative URLs
                    if line.startswith('http'):
                        segments.append(line)
                    else:
                        segments.append(f"{base_url}/{line}")

            return segments
        except Exception as e:
            logger.error(f"Error parsing M3U8: {e}")
            return []

    def _download_video_segment(self, url: str, temp_path: str) -> bool:
        """
        Download a video segment from the given URL to a temporary file.
        Handles both regular MP4 URLs and HLS segments.
        Returns True if successful, False otherwise.
        """
        try:
            headers = {'Range': 'bytes=0-10485760'}  # First 10MB
            response = requests.get(url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()

            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            return True
        except Exception as e:
            logger.error(f"Error downloading video segment: {e}")
            return False

    async def _capture_from_hls_stream(self, hls_url: str) -> Image.Image | None:
        """
        Extract a frame from an HLS/M3U8 stream.
        Returns a PIL Image or None if extraction failed.
        """
        try:
            # Parse the M3U8 playlist
            segments = await asyncio.to_thread(self._parse_m3u8, hls_url)

            if not segments:
                logger.error(f"No segments found in HLS stream: {hls_url}")
                return None

            # Try to get a frame from the last segment
            with tempfile.NamedTemporaryFile(suffix='.ts', delete=False) as tmp_file:
                temp_path = tmp_file.name

            try:
                # Download the last segment
                success = await asyncio.to_thread(
                    self._download_video_segment,
                    segments[-1],
                    temp_path
                )

                if not success:
                    logger.error("Failed to download HLS segment")
                    return None

                # Try to extract frame from the segment
                pil_image = await asyncio.to_thread(
                    self._extract_last_frame_from_video,
                    temp_path
                )

                return pil_image

            finally:
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except Exception as e:
                        logger.warning(f"Failed to clean up HLS segment {temp_path}: {e}")

        except Exception as e:
            logger.error(f"Error capturing from HLS stream: {e}")
            return None

    async def capture_image_from_stream(self, url: str, channel_name: str) -> str | None:
        """
        Capture the latest frame from a YouTube live stream.
        Returns the path to the saved image or None if failed.
        """
        try:
            folder = self._create_folder(channel_name)

            ydl_opts = {
                'format': 'best',
                'quiet': True,
                'no_warnings': True,
                'socket_timeout': 10,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, url, download=False)

                if not info:
                    return None

                # Generate filename based on current timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}.jpg"
                filepath = folder / filename

                # Save the info for reference
                with open(folder / f"{timestamp}.txt", "w") as f:
                    f.write(f"URL: {url}\n")
                    f.write(f"Title: {info.get('title', 'Unknown')}\n")
                    f.write(f"Timestamp: {datetime.now().isoformat()}\n")

                # Try to extract frame from stream
                pil_image = None

                # Check for HLS/M3U8 URL
                hls_url = None
                if 'url' in info:
                    if self._is_hls_url(info['url']):
                        hls_url = info['url']

                # If no direct HLS URL, check formats
                if not hls_url and 'formats' in info:
                    for fmt in reversed(info['formats']):  # Start from highest quality
                        if 'url' in fmt and self._is_hls_url(fmt['url']):
                            hls_url = fmt['url']
                            break
                        elif 'manifest_url' in fmt and self._is_hls_url(fmt['manifest_url']):
                            hls_url = fmt['manifest_url']
                            break

                # Capture from HLS stream
                if hls_url:
                    logger.info(f"Detected HLS stream: {hls_url}")
                    pil_image = await self._capture_from_hls_stream(hls_url)

                # Fallback: try to get regular video URL
                if pil_image is None:
                    video_url = None

                    if 'url' in info and not self._is_hls_url(info['url']):
                        video_url = info['url']
                    elif 'formats' in info and len(info['formats']) > 0:
                        # Try to get MP4 format first, then any format
                        for fmt in reversed(info['formats']):
                            if fmt.get('ext') == 'mp4' and 'url' in fmt:
                                video_url = fmt['url']
                                break

                        if not video_url and 'url' in info['formats'][-1]:
                            video_url = info['formats'][-1]['url']

                    if video_url:
                        logger.info(f"Using regular video URL: {video_url[:80]}...")

                        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_file:
                            temp_path = tmp_file.name

                        try:
                            # Download video segment
                            success = await asyncio.to_thread(
                                self._download_video_segment,
                                video_url,
                                temp_path
                            )

                            if success:
                                # Extract the frame from the downloaded video
                                pil_image = await asyncio.to_thread(
                                    self._extract_last_frame_from_video,
                                    temp_path
                                )

                        finally:
                            # Clean up temporary file
                            if os.path.exists(temp_path):
                                try:
                                    os.remove(temp_path)
                                except Exception as e:
                                    logger.warning(f"Failed to clean up temporary file {temp_path}: {e}")

                if pil_image is None:
                    logger.error("Failed to extract frame from stream")
                    return None

                # Save the extracted frame
                pil_image.save(filepath, 'JPEG', quality=95)
                inference = self.model.predict(filepath, conf=0.95)
                inference[0].save(filepath)

                files = sorted(os.listdir(folder), reverse=True)
                if len(files) > 20:
                    for f in files[20:]:
                        os.remove(folder / f)
                return str(filepath)

        except Exception as e:
            logger.error(f"Error capturing image from {url}: {e}")
            return None

    def get_available_channels(self) -> list[str]:
        """Get list of all available channels (subdirectories)."""
        if not self.base_dir.exists():
            return []
        return sorted([d.name for d in self.base_dir.iterdir() if d.is_dir()])

    def get_images(self, channel_name: str, limit: int = 10) -> list[dict]:
        """
        Get the most recent images for a channel.
        Returns a list of dictionaries with image info.
        """
        folder = self.base_dir / channel_name
        if not folder.exists():
            return []

        images = []
        image_files = sorted(
            folder.glob("*.jpg"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        for img_file in image_files[:limit]:
            timestamp_str = img_file.stem
            try:
                timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
            except ValueError:
                timestamp = datetime.fromtimestamp(img_file.stat().st_mtime)

            images.append({
                "path": str(img_file),
                "filename": img_file.name,
                "timestamp": timestamp.isoformat(),
                "url": f"/images/{channel_name}/{img_file.name}"
            })

        return images

    def get_latest_image(self, channel_name: str) -> dict | None:
        """Get the latest image for a channel."""
        images = self.get_images(channel_name, limit=1)
        return images[0] if images else None


