import asyncio
import os
import re
import yt_dlp

class VideoObject:
    def __init__(self, url: str):
        self.url = url
        self.title = url.split("/")[-1].split("?")[0] or "video_hls"

class Client:
    async def get_video(self, url: str) -> VideoObject:
        return VideoObject(url)

class DownloadConfigHLS:
    def __init__(self, quality: str = "best", path: str = "./"):
        self.quality = quality
        self.path = path

    def _is_social_media(self, url: str) -> bool:
        social_domains = ["tiktok.com", "instagram.com", "youtube.com", "youtu.be", "twitter.com", "x.com", "facebook.com"]
        return any(domain in url for domain in social_domains)

    async def download(self, video: VideoObject, on_progress=None) -> str:
        os.makedirs(self.path, exist_ok=True)
        
        if self._is_social_media(video.url):
            return await self._download_social_media(video, on_progress)
        else:
            return await self._download_hls(video, on_progress)

    async def _download_social_media(self, video: VideoObject, on_progress=None) -> str:
        def run_ytdlp():
            def hook(d):
                if d['status'] == 'downloading':
                    total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                    downloaded = d.get('downloaded_bytes', 0)
                    if total > 0 and on_progress:
                        on_progress(round((downloaded / total) * 100, 1))
                elif d['status'] == 'finished':
                    if on_progress: on_progress(100.0)

            ydl_opts = {
                'outtmpl': os.path.join(self.path, '%(title)s.%(ext)s'),
                'progress_hooks': [hook],
                'quiet': True,
                'nocheckcertificate': True,
            }

            if self.quality == "audio":
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}]
            elif self.quality != "best":
                height = self.quality.replace("p", "")
                ydl_opts['format'] = f'bestvideo[height<={height}]+bestaudio/best[height<={height}]'
            else:
                ydl_opts['format'] = 'bestvideo+bestaudio/best'

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video.url, download=False)
                video.title = info.get('title', 'Social Media Video')
                ydl.download([video.url])
            
            return os.path.join(self.path, f"{video.title}.mp4")

        return await asyncio.to_thread(run_ytdlp)

    async def _download_hls(self, video: VideoObject, on_progress=None) -> str:
        safe_title = re.sub(r'[\\/*?:"<>|]', "", video.title)
        output_file = os.path.join(self.path, f"{safe_title}.mp4")

        cmd = [
            "ffmpeg", "-y", "-i", video.url,
            "-c", "copy", "-bsf:a", "aac_adtstoasc",
            output_file
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        total_duration = 0.0

        while True:
            line = await process.stderr.readline()
            if not line: break
            line_str = line.decode('utf-8', errors='ignore')

            if "Duration:" in line_str and total_duration == 0:
                match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", line_str)
                if match:
                    h, m, s = match.groups()
                    total_duration = int(h) * 3600 + int(m) * 60 + float(s)

            if "time=" in line_str and total_duration > 0:
                match = re.search(r"time=(\d+):(\d+):(\d+\.\d+)", line_str)
                if match:
                    h, m, s = match.groups()
                    current_time = int(h) * 3600 + int(m) * 60 + float(s)
                    percent = (current_time / total_duration) * 100
                    if on_progress:
                        on_progress(min(round(percent, 1), 99.9))

        await process.wait()
        if process.returncode != 0:
            raise Exception("FFmpeg process failed.")
        if on_progress:
            on_progress(100.0)
        return output_file