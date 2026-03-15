"""
Scheduler for automatic YouTube stream capturing.
"""

import asyncio
from datetime import datetime
from typing import Optional
from backend.youtube import YouTubeCapture
from place_publique.config import Config
import logging

logger = logging.getLogger(__name__)


class CaptureScheduler:
    """Scheduler for periodic YouTube capture."""

    def __init__(self, capture: YouTubeCapture, config: Config):
        self.capture = capture
        self.config = config 
        self.is_running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the scheduler."""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return

        # Initialize channel directories based on configuration
        await self._initialize_channels()

        self.is_running = True
        self._task = asyncio.create_task(self._run())
        logger.info(f"🚀 Capture scheduler started with {len(self.config.youtube_urls)} URLs")

    async def stop(self):
        """Stop the scheduler."""
        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("⏹️  Capture scheduler stopped")

    async def _initialize_channels(self):
        """Initialize channel directories for all configured URLs."""
        if not self.config.youtube_urls:
            logger.warning("No YouTube URLs configured")
            return

        initialized_channels = []
        for url in self.config.youtube_urls:
            channel_name = self._get_channel_name(url)
            try:
                # Create the channel directory if it doesn't exist
                self.capture._create_folder(channel_name)
                initialized_channels.append(channel_name)
                logger.info(f"✅ Initialized channel: {channel_name}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize channel {channel_name}: {e}")

        if initialized_channels:
            logger.info(f"✅ Initialized {len(initialized_channels)} channels: {', '.join(initialized_channels)}")

    async def _run(self):
        """Main scheduler loop."""
        while self.is_running:
            try:
                await self._capture_all()
                await asyncio.sleep(self.config.scraping_interval)
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(self.config.scraping_interval)

    async def _capture_all(self):
        """Capture images from all configured URLs in parallel."""
        if not self.config.youtube_urls:
            return

        tasks = []
        for url in self.config.youtube_urls:
            # Extract channel name from URL or use a default naming
            channel_name = self._get_channel_name(url)
            tasks.append(self.capture.capture_image_from_stream(url, channel_name))

        # Run all captures in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful = sum(1 for r in results if isinstance(r, str))
        failed = len(results) - successful
        timestamp = datetime.now().strftime("%H:%M:%S")
        logger.info(f"[{timestamp}] Captured {successful} images, {failed} failed")

    @staticmethod
    def _get_channel_name(url: str) -> str:
        """Extract or generate a channel name from URL."""
        # Try to extract video ID from URL
        if "watch?v=" in url:
            video_id = url.split("watch?v=")[1].split("&")[0]
            return f"Channel-{video_id[:12]}"  # Shortened to 12 chars for readability
        elif "/c/" in url:
            return url.split("/c/")[1].split("/")[0]
        elif "/user/" in url:
            return url.split("/user/")[1].split("/")[0]
        elif "/@" in url:
            return url.split("/@")[1].split("/")[0]
        else:
            return "default_channel"
