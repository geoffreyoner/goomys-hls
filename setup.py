from setuptools import setup, find_packages

setup(
    name="goomys_hls",
    version="0.2.0",
    license="MIT",
    description="Downloader for HLS streams and social media videos",
    author="Goomys",
    packages=find_packages(),
    install_requires=[
        "yt-dlp",
    ],
    python_requires=">=3.7",
)