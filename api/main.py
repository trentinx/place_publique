from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from backend.youtube import YouTubeCapture
from backend.scheduler import CaptureScheduler
from place_publique.config import Config

app = FastAPI(title="IHM YouTube Live Capture")

# Configure CORS to allow frontend (Flask on port 5000) to communicate with API (port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Get the absolute path to captures directory relative to the backend module
current_dir = Path(__file__).parent.parent.resolve()
config_path = current_dir / "config.json"
config = Config(str(config_path))
captures_dir = current_dir / "captures"
capture = YouTubeCapture(base_dir=str(captures_dir))
scheduler = CaptureScheduler(capture, config)

# Mount static files
if captures_dir.exists():
    app.mount("/images", StaticFiles(directory=str(captures_dir)), name="images")


@app.on_event("startup")
async def startup_event():
    """Start the capture scheduler when the app starts."""
    await scheduler.start()


@app.on_event("shutdown")
async def shutdown_event():
    """Stop the capture scheduler when the app shuts down."""
    await scheduler.stop()


@app.get("/api/channels")
async def get_channels():
    """Get list of available channels."""
    channels = capture.get_available_channels()
    return {"channels": channels}


@app.get("/api/images/{channel_name}")
async def get_channel_images(channel_name: str, limit: int = 10):
    """Get recent images for a channel."""
    images = capture.get_images(channel_name, limit=limit)
    if not images:
        raise HTTPException(status_code=404, detail=f"Channel {channel_name} not found or no images")
    return {"channel": channel_name, "images": images}


@app.get("/api/latest/{channel_name}")
async def get_latest_image(channel_name: str):
    """Get the latest image for a channel."""
    image = capture.get_latest_image(channel_name)
    if not image:
        raise HTTPException(status_code=404, detail=f"No images found for channel {channel_name}")
    return image


@app.post("/api/capture/{channel_name}")
async def capture_stream(channel_name: str, url: str):
    """Capture an image from a YouTube live stream."""
    result = await capture.capture_image_from_stream(url, channel_name)
    if result:
        return {"success": True, "path": result, "channel": channel_name}
    else:
        raise HTTPException(status_code=500, detail="Failed to capture image")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/api/config")
async def get_config():
    """Get current configuration."""
    return {
        "youtube_urls": config.youtube_urls,
        "scraping_interval": config.scraping_interval,
        "scheduler_running": scheduler.is_running
    }


@app.post("/api/config")
async def update_config(youtube_urls: list[str] = None, scraping_interval: int = None):
    """Update configuration and restart scheduler if needed."""
    updated = False

    if youtube_urls is not None:
        config.youtube_urls = youtube_urls
        updated = True

    if scraping_interval is not None and scraping_interval > 0:
        config.scraping_interval = scraping_interval
        scheduler.interval = scraping_interval
        updated = True

    if updated:
        # Save configuration to file
        config_data = {
            "youtube_urls": config.youtube_urls,
            "scraping_interval": config.scraping_interval
        }
        import json
        with open(config.CONFIG_FILE, "w") as f:
            json.dump(config_data, f, indent=2)

        # Restart scheduler if running
        if scheduler.is_running:
            await scheduler.stop()
            await scheduler.start()

        return {
            "success": True,
            "youtube_urls": config.youtube_urls,
            "scraping_interval": config.scraping_interval
        }
    else:
        raise HTTPException(status_code=400, detail="No valid configuration provided")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8082)
