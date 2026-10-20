# Goomys HLS

A pure Python library for downloading HLS (`.m3u8`) streams and social media videos (YouTube, TikTok, Instagram, etc.). It automatically converts streams to `.mp4` using FFmpeg and provides real-time progress callbacks.

## Features

- **HLS Downloader**: Downloads `.m3u8` streams and merges `.ts` segments into `.mp4` using FFmpeg.
- **Social Media Support**: Automatically detects and downloads videos from YouTube, TikTok, Instagram, X (Twitter), and more using `yt-dlp`.
- **Progress Callback**: Real-time download progress (percentage) for both HLS and social media.
- **Hybrid Engine**: Automatically switches between FFmpeg and yt-dlp based on the URL.

## Prerequisites

You **must** have `ffmpeg` and `python` (with `pip`) installed on your system. Here is how to install them for each OS:

### Termux (Android)

```bash
pkg update && pkg upgrade -y
pkg install ffmpeg python -y
```

### Ubuntu / Debian / Linux Mint

```bash
sudo apt update
sudo apt install ffmpeg python3 python3-pip -y
```

### Arch Linux / Manjaro

```bash
sudo pacman -S ffmpeg python python-pip
```

### macOS (via Homebrew)

```bash
brew install ffmpeg python
```

### Windows

1. Install Python from [python.org](https://www.python.org/downloads/) and make sure to check **"Add Python to PATH"** during installation.
2. Download an FFmpeg build from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) or [BtbN](https://github.com/BtbN/FFmpeg-Builds/releases).
3. Extract the FFmpeg ZIP file, then add the `bin` folder (the one containing `ffmpeg.exe`) to your system `PATH` environment variable.
4. Open a new terminal and verify the installation:

   ```bash
   ffmpeg -version
   ```

## Installation

Clone this repository and install it locally:

```bash
git clone https://github.com/geoffreyoner/goomys-hls.git
cd goomys-hls
pip install .
```

## Usage

```python
import asyncio
from goomys_hls import Client, DownloadConfigHLS

async def main():
    client = Client()
    # Use any .m3u8 URL or social media URL
    video = await client.get_video("https://www.tiktok.com/@user/video/12345")

    def progress(pct):
        print(f"Downloading: {pct}%")

    config = DownloadConfigHLS(path="./downloads")
    output_file = await config.download(video, on_progress=progress)
    print(f"Saved to: {output_file}")

if __name__ == "__main__":
    asyncio.run(main())
```

## API Server (FastAPI)

This library includes an example API server built with FastAPI in the `examples/` folder. You can run it as a local web server.

### 1. Install server dependencies

```bash
pip install fastapi uvicorn
```

### 2. Run the server

Run the following command from the project root folder:

```bash
uvicorn examples.api_server:app --host 0.0.0.0 --port 8000
```

### 3. Endpoints

#### Start a download

- **URL**: `http://127.0.0.1:8000/download`
- **Method**: `POST`
- **Body** (JSON):

  ```json
  {
      "url": "https://www.instagram.com/reel/C1234567890/",
      "path": "./downloads"
  }
  ```

- **Response**:

  ```json
  {
      "job_id": "a1b2c3d4"
  }
  ```

#### Check status and progress

- **URL**: `http://127.0.0.1:8000/status/{job_id}` (e.g. `http://127.0.0.1:8000/status/a1b2c3d4`)
- **Method**: `GET`
- **Response** (while downloading):

  ```json
  {
      "job_id": "a1b2c3d4",
      "status": "downloading",
      "progress": 45.5,
      "title": "Social Media Video",
      "output": null,
      "error": null
  }
  ```

- **Response** (when finished):

  ```json
  {
      "job_id": "a1b2c3d4",
      "status": "done",
      "progress": 100.0,
      "title": "Social Media Video",
      "output": "./downloads/Social Media Video.mp4",
      "error": null
  }
  ```

## License

Distributed under the [MIT License](LICENSE).

---

<div align="center">

Made with ❤️ by **Goomys**

</div>
