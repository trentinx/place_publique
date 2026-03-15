"""
Configuration for YouTube Live Viewer.
"""

import json
from pathlib import Path
from typing import List


class Config:
    """Load and manage application configuration."""

    def __init__(self, config_path:str):
        self.youtube_urls: List[str] = []
        self.scraping_interval: int = 10  # Default: 10 seconds
        self._load_config(config_path)

    def _load_config(self , config_path: str):
        """Load configuration from config.json file."""
        if Path(config_path).exists():
            try:
                with open(config_path, "r") as f:
                    data = json.load(f)
                    self.youtube_urls = data.get("youtube_urls", [])
                    self.scraping_interval = data.get("scraping_interval", 10)
                print(f"✅ Configuration loaded from {config_path}")
            except Exception as e:
                print(f"⚠️  Error loading configuration: {e}")
