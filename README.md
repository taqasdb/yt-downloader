# yt-downloader

A simple command-line YouTube downloader written in Python using `yt-dlp`.

The program supports:

- Downloading a single YouTube video
- Downloading audio as MP3
- Downloading both video and audio
- Downloading YouTube playlists
- Keeping separate download archives to avoid downloading the same item again
- Retrying failed downloads
- Logging download errors
- Converting existing `.webm` audio files to `.mp3` using FFmpeg

> **Note:** Use this project only for content you have permission to download and in accordance with YouTube's terms and applicable laws.

---

## 1. Requirements

You need the following software:

- Python 3
- FFmpeg
- Git (optional, if you clone the project from GitHub)

### Install with `winget`

Open **PowerShell** or **Windows Terminal**:

```powershell
winget install Python.Python.3.13
winget install Gyan.FFmpeg
winget install Git.Git
```

After installation, restart your terminal and verify:

```powershell
python --version
ffmpeg -version
git --version
```

If `python` is not recognized, try:

```powershell
py --version
```

---

## 2. Get the project

If the repository is already on GitHub, clone it with:

```powershell
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd yt-downloader
```

Or download the project as a ZIP and extract it.

---

## 3. Install Python dependency

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Install the required Python package:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If `requirements.txt` is not available, install `yt-dlp` directly:

```powershell
pip install yt-dlp
```

---

## 4. Basic command format

The general command is:

```powershell
python yt_downloader.py "<URL>"
```

The `--mode` option controls what is downloaded:

| Mode | Description |
|---|---|
| `video` | Download video |
| `audio` | Download audio as MP3 |
| `both` | Download both video and audio |

For a playlist, add:

```text
--playlist
```

---

# 5. Download a single video

Example video URL:

```text
https://www.youtube.com/watch?v=2qkZDQvL3P8
```

### Download video

```powershell
python yt_downloader.py "https://www.youtube.com/watch?v=2qkZDQvL3P8"
```

This uses the default mode:

```text
video
```

The downloaded video is stored under:

```text
downloads/videos/
```

### Download audio as MP3

```powershell
python yt_downloader.py "https://www.youtube.com/watch?v=2qkZDQvL3P8" --mode audio
```

Output:

```text
downloads/audios/
```

### Download both video and audio

```powershell
python yt_downloader.py "https://www.youtube.com/watch?v=2qkZDQvL3P8" --mode both
```

---

# 6. Download a playlist

Example playlist URL:

```text
https://www.youtube.com/watch?v=142pY1HU_t0&list=PLqhc5zHe8K2fRMPN-ans7hOAPFCQrBTzd
```

Because the URL contains `&`, keep the entire URL inside quotes when using PowerShell.

### Download playlist videos

```powershell
python yt_downloader.py "https://www.youtube.com/watch?v=142pY1HU_t0&list=PLqhc5zHe8K2fRMPN-ans7hOAPFCQrBTzd" --playlist --mode video
```

The program creates a playlist directory similar to:

```text
downloads/
└── playlists/
    └── <Playlist Name>/
        ├── 001 - <Video Title>.mp4
        ├── 002 - <Video Title>.mp4
        └── ...
```

### Download playlist audio as MP3

```powershell
python yt_downloader.py "https://www.youtube.com/watch?v=142pY1HU_t0&list=PLqhc5zHe8K2fRMPN-ans7hOAPFCQrBTzd" --playlist --mode audio
```

Output:

```text
downloads/
└── playlists/
    └── <Playlist Name>/
        ├── 001 - <Video Title>.mp3
        ├── 002 - <Video Title>.mp3
        └── ...
```

### Download both video and audio from a playlist

```powershell
python yt_downloader.py "https://www.youtube.com/watch?v=142pY1HU_t0&list=PLqhc5zHe8K2fRMPN-ans7hOAPFCQrBTzd" --playlist --mode both
```

Output:

```text
downloads/
└── playlists/
    └── <Playlist Name>/
        ├── videos/
        │   ├── 001 - <Video Title>.mp4
        │   ├── 002 - <Video Title>.mp4
        │   └── ...
        └── audios/
            ├── 001 - <Video Title>.mp3
            ├── 002 - <Video Title>.mp3
            └── ...
```

---

# 7. Command reference

## Single video

```powershell
python yt_downloader.py "<URL>"
```

Equivalent to:

```powershell
python yt_downloader.py "<URL>" --mode video
```

## Single video → MP3

```powershell
python yt_downloader.py "<URL>" --mode audio
```

## Single video → video + MP3

```powershell
python yt_downloader.py "<URL>" --mode both
```

## Playlist → video

```powershell
python yt_downloader.py "<PLAYLIST_URL>" --playlist --mode video
```

## Playlist → MP3

```powershell
python yt_downloader.py "<PLAYLIST_URL>" --playlist --mode audio
```

## Playlist → video + MP3

```powershell
python yt_downloader.py "<PLAYLIST_URL>" --playlist --mode both
```

---

# 8. Download folders

The application automatically creates the required directories.

```text
downloads/
├── videos/
├── audios/
├── playlists/
├── .archive/
│   ├── videos.txt
│   └── audios.txt
└── logs/
    └── download_errors.log
```

### `videos/`

Contains downloaded single videos.

### `audios/`

Contains downloaded single-video MP3 files.

### `playlists/`

Contains playlist downloads. Each playlist gets its own directory.

### `.archive/`

Contains download archive files.

The archive allows `yt-dlp` to remember previously downloaded items and helps prevent downloading the same item again.

### `logs/`

Contains download error information:

```text
downloads/logs/download_errors.log
```

---

# 9. Retry and download behavior

The downloader is configured to:

- Continue interrupted downloads
- Avoid overwriting existing files
- Retry failed downloads
- Retry failed fragments
- Retry file-access operations
- Ignore individual playlist item errors and continue with other items
- Display download progress line by line
- Use a download archive

If one item in a playlist fails, the program can continue processing the remaining items.

---

# 10. YouTube client configuration

The project uses the following `yt-dlp` extractor configuration:

```text
youtube:player_client=web_embedded
```

This configuration is included to help with YouTube extraction problems such as HTTP 403 errors that may occur in some environments.

YouTube extraction behavior can change over time, so a configuration that works today may require updating later.

---

# 11. Converting existing WebM files to MP3

The project also supports converting existing `.webm` files to `.mp3` using FFmpeg.

This conversion does **not** make a request to YouTube.

The conversion process:

1. Finds `.webm` files in the target folder.
2. Converts them to `.mp3`.
3. Keeps the original `.webm` file until the MP3 conversion succeeds.
4. Deletes the `.webm` file only after a successful conversion.
5. Skips conversion when the corresponding MP3 already exists and removes the existing WebM.

FFmpeg must be installed and available in your system `PATH`.

---

# 12. Troubleshooting

## `No module named yt_dlp`

Install the dependency:

```powershell
pip install yt-dlp
```

Or:

```powershell
python -m pip install yt-dlp
```

---

## `ffmpeg is not recognized`

Check:

```powershell
ffmpeg -version
```

If it fails, install FFmpeg:

```powershell
winget install Gyan.FFmpeg
```

Then restart PowerShell/Windows Terminal.

---

## Python is not recognized

Try:

```powershell
py --version
```

If `py` works, you can use:

```powershell
py -m pip install yt-dlp
py yt_downloader.py "<URL>"
```

If neither command works, reinstall Python:

```powershell
winget install Python.Python.3.13
```

---

## Playlist URL does not work correctly in PowerShell

Always put the URL in double quotes:

```powershell
python yt_downloader.py "https://www.youtube.com/watch?v=142pY1HU_t0&list=PLqhc5zHe8K2fRMPN-ans7hOAPFCQrBTzd" --playlist --mode audio
```

Do not remove the `&list=...` portion.

---

## A download fails

Check:

```text
downloads/logs/download_errors.log
```

The program records the URL, mode, and error information there.

---

# 13. Recommended workflow

For a new installation:

```powershell
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd yt-downloader

python -m venv .venv
.venv\Scripts\activate

python -m pip install --upgrade pip
pip install -r requirements.txt
```

Then test with the example video:

```powershell
python yt_downloader.py "https://www.youtube.com/watch?v=2qkZDQvL3P8"
```

Test MP3:

```powershell
python yt_downloader.py "https://www.youtube.com/watch?v=2qkZDQvL3P8" --mode audio
```

Then test the example playlist:

```powershell
python yt_downloader.py "https://www.youtube.com/watch?v=142pY1HU_t0&list=PLqhc5zHe8K2fRMPN-ans7hOAPFCQrBTzd" --playlist --mode audio
```

---

## License

Add your preferred license here if you intend to distribute the project publicly.

## Disclaimer

This project is provided for educational and personal-use purposes. You are responsible for ensuring that your use of the downloader complies with the rights of content owners, YouTube's terms, and applicable laws.
