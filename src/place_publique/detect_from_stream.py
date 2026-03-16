from ultralytics import YOLO
from typing import List, Optional
import cv2
import os


class FishDetector:
    def __init__(self, model_path: str, conf: float = 0.4, iou: float = 0.7, max_det: int = 20):
        """Initialize the Fish Detector with a YOLO model."""
        self.model = YOLO(model_path)
        self.conf = conf
        self.iou = iou
        self.max_det = max_det
    
    def detect_single_image(self, image_path: str, output_path: str = "output.jpg"):
        """Run detection on a single image without tracking."""
        results = self.model.predict(
            image_path,
            conf=self.conf,
            iou=self.iou,
            max_det=self.max_det,
        )
        
        for r in results:
            r.save(filename=output_path)
            
            if r.boxes is not None:
                print("\n--- DETECTIONS ---")
                for box in r.boxes:
                    cls_id = int(box.cls.item())
                    class_name = self.model.names[cls_id]
                    confidence = float(box.conf.item())
                    
                    print(
                        f"class: {class_name} | "
                        f"confidence: {confidence:.2f}"
                    )
        
        return results
    
    def _create_video_from_images(self, image_paths: List[str], output_video: str = "temp_tracking_video.mp4", fps: int = 5):
        """Create a video from a list of images."""
        # Read the first image to get dimensions
        first_image = cv2.imread(image_paths[0])
        if first_image is None:
            raise ValueError(f"Could not read image: {image_paths[0]}")
        
        height, width, _ = first_image.shape
        
        # Define codec and create VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
        
        print(f"\nCreating video from {len(image_paths)} images...")
        for img_path in image_paths:
            img = cv2.imread(img_path)
            if img is None:
                print(f"Warning: Could not read {img_path}, skipping...")
                continue
            
            # Resize if necessary
            if img.shape[:2] != (height, width):
                img = cv2.resize(img, (width, height))
            
            video_writer.write(img)
        
        video_writer.release()
        print(f"Video created: {output_video}")
        return output_video
    
    def detect_image_stream(self, image_paths: List[str], save_outputs: bool = True, create_video: bool = False, video_fps: int = 5):
        """Run tracking across multiple images.
        
        Args:
            image_paths: List of image file paths
            save_outputs: Whether to save annotated outputs
            create_video: If True, creates a video from images and tracks on that
            video_fps: Frames per second for created video (only used if create_video=True)
        """
        if create_video:
            # Create video from images
            video_path = "temp_tracking_video.mp4"
            self._create_video_from_images(image_paths, video_path, fps=video_fps)
            
            # Run tracking on the video
            results = self.model.track(
                video_path,
                conf=self.conf,
                iou=self.iou,
                max_det=self.max_det,
                
            )
            
            # Process results
            for idx, r in enumerate(results):
                if idx < len(image_paths):
                    print(f"\n=== FRAME {idx + 1} (from {image_paths[idx]}) ===")
                else:
                    print(f"\n=== FRAME {idx + 1} ===")
                
                if save_outputs:
                    r.save(filename=f"output_{idx + 1}.jpg")
                
                if r.boxes is not None:
                    print("--- DETECTIONS ---")
                    for box in r.boxes:
                        cls_id = int(box.cls.item())
                        class_name = self.model.names[cls_id]
                        confidence = float(box.conf.item())
                        track_id = int(box.id.item()) if box.id is not None else None
                        
                        print(
                            f"class: {class_name} | "
                            f"confidence: {confidence:.2f} | "
                            f"track_id: {track_id}"
                        )
        else:
            # Original behavior: track directly on image list
            results = self.model.track(
                image_paths,
                conf=self.conf,
                iou=self.iou,
                max_det=self.max_det,
                show_trajectories=True
            )
            
            for idx, r in enumerate(results):
                print(f"\n=== IMAGE {idx + 1}: {image_paths[idx]} ===")
                
                if save_outputs:
                    r.save(filename=f"output_{idx + 1}.jpg")
                
                if r.boxes is not None:
                    print("--- DETECTIONS ---")
                    for box in r.boxes:
                        cls_id = int(box.cls.item())
                        class_name = self.model.names[cls_id]
                        confidence = float(box.conf.item())
                        track_id = int(box.id.item()) if box.id is not None else None
                        
                        print(
                            f"class: {class_name} | "
                            f"confidence: {confidence:.2f} | "
                            f"track_id: {track_id}"
                        )
        
        return results


if __name__ == "__main__":
    # Initialize detector
    detector = FishDetector(
        model_path="/Users/julienrm/Workspace/formation/test_vision/runs/detect/train10/weights/best.pt",
        conf=0.2,
        iou=0.7,
        max_det=20
    )
    
    image_paths = [
            "our_aquarium_images/aquarium_20260213-141102_000000.jpg",
            "our_aquarium_images/aquarium_20260213-141102_000001.jpg",
            "our_aquarium_images/aquarium_20260213-141102_000002.jpg",
            "our_aquarium_images/aquarium_20260213-141102_000003.jpg",
            "our_aquarium_images/aquarium_20260213-141102_000004.jpg",
            "our_aquarium_images/aquarium_20260213-141102_000005.jpg",
            "our_aquarium_images/aquarium_20260213-141102_000006.jpg",
            "our_aquarium_images/aquarium_20260213-141102_000007.jpg",
            "our_aquarium_images/aquarium_20260213-141102_000008.jpg",
            "our_aquarium_images/aquarium_20260213-141102_000009.jpg",
            "our_aquarium_images/aquarium_20260213-141102_000010.jpg",
            "our_aquarium_images/aquarium_20260213-141102_000011.jpg",
            "our_aquarium_images/aquarium_20260213-141102_000012.jpg",
            "our_aquarium_images/aquarium_20260213-141102_000013.jpg",
            "our_aquarium_images/aquarium_20260213-141102_000014.jpg",
            "our_aquarium_images/aquarium_20260213-141102_000015.jpg",
            "our_aquarium_images/aquarium_20260213-141103_000016.jpg",
            "our_aquarium_images/aquarium_20260213-141103_000017.jpg",
            "our_aquarium_images/aquarium_20260213-141103_000018.jpg",
            "our_aquarium_images/aquarium_20260213-141103_000019.jpg",
        ]
    
    print("Testing image stream detection with video creation and tracking...")
    detector.detect_image_stream(image_paths, create_video=True, video_fps=5)