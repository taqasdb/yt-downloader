from pathlib import Path
import subprocess
import sys
import re


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path("downloads")

VIDEO_DIR = BASE_DIR / "videos"
AUDIO_DIR = BASE_DIR / "audios"
PLAYLIST_DIR = BASE_DIR / "playlists"

ARCHIVE_DIR = BASE_DIR / ".archive"
LOG_DIR = BASE_DIR / "logs"

VIDEO_ARCHIVE = ARCHIVE_DIR / "videos.txt"
AUDIO_ARCHIVE = ARCHIVE_DIR / "audios.txt"

LOG_FILE = LOG_DIR / "download_errors.log"


# ============================================================
# YT-DLP CONFIG
# ============================================================

# Quan trọng:
# Client này đã được kiểm tra và hoạt động với YouTube
# trong trường hợp máy của bạn gặp HTTP 403.
YOUTUBE_EXTRACTOR_ARGS = [
    "--extractor-args",
    "youtube:player_client=web_embedded",
]


# ============================================================
# UTILS
# ============================================================

def ensure_directories():
    """
    Tạo các thư mục hệ thống cần thiết.
    """

    ARCHIVE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


def sanitize_filename(name: str) -> str:
    """
    Làm sạch tên thư mục/file để tránh ký tự
    không hợp lệ trên Windows.
    """

    # Ký tự không hợp lệ trên Windows
    name = re.sub(
        r'[<>:"/\\|?*]',
        "_",
        name,
    )

    # Xóa khoảng trắng/dấu chấm cuối
    name = name.rstrip(" .")

    # Windows không thích tên rỗng
    if not name:
        name = "Unknown Playlist"

    return name


def log_error(
    url: str,
    mode: str,
    error: str,
):
    """
    Ghi lỗi vào file log.
    """

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with LOG_FILE.open(
        "a",
        encoding="utf-8",
    ) as file:

        file.write(
            f"\n{'=' * 80}\n"
            f"MODE: {mode}\n"
            f"URL: {url}\n"
            f"ERROR:\n{error}\n"
        )


# ============================================================
# BUILD YT-DLP COMMAND
# ============================================================

def build_common_command(
    output_dir: Path,
    archive_file: Path,
):
    """
    Các option dùng chung cho video/audio/playlist.
    """

    return [
        sys.executable,
        "-m",
        "yt_dlp",

        # ----------------------------------------------------
        # YouTube client
        # ----------------------------------------------------

        # Đây là phần quan trọng nhất để tránh lỗi 403
        # đã gặp trên máy.
        *YOUTUBE_EXTRACTOR_ARGS,

        # ----------------------------------------------------
        # Download
        # ----------------------------------------------------

        "--continue",

        "--no-overwrites",

        # ----------------------------------------------------
        # Retry
        # ----------------------------------------------------

        "--retries",
        "10",

        "--fragment-retries",
        "10",

        "--file-access-retries",
        "5",

        "--retry-sleep",
        "linear=1::3",

        # ----------------------------------------------------
        # Playlist
        # ----------------------------------------------------

        # Nếu một video lỗi, tiếp tục video kế tiếp.
        "--ignore-errors",

        # Hiển thị tiến trình mỗi dòng.
        "--newline",

        # Khi URL chứa cả ?v=...&list=...
        # ưu tiên tải toàn bộ playlist.
        "--yes-playlist",

        # ----------------------------------------------------
        # Archive
        # ----------------------------------------------------

        "--download-archive",
        str(archive_file),

        # ----------------------------------------------------
        # Output
        # ----------------------------------------------------

        "-o",
        str(
            output_dir /
            "%(playlist_index)03d - %(title)s.%(ext)s"
        ),
    ]


# ============================================================
# DOWNLOAD VIDEO
# ============================================================

def download_video(
    url: str,
    output_dir: Path = VIDEO_DIR,
):
    """
    Tải video.

    output_dir có thể là:

        downloads/videos/

    hoặc:

        downloads/playlists/<playlist>/videos/
    """

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    command = build_common_command(
        output_dir=output_dir,
        archive_file=VIDEO_ARCHIVE,
    )

    command.extend([
        # ----------------------------------------------------
        # Format
        # ----------------------------------------------------

        " -f",
    ])

    # Sửa phần format riêng để tránh truyền " -f"
    command.pop()

    command.extend([
        "-f",
        "bv*+ba/b",

        "--merge-output-format",
        "mp4",

        url,
    ])

    print()
    print("=" * 70)
    print("VIDEO")
    print("=" * 70)
    print(f"URL        : {url}")
    print(f"Destination: {output_dir}")
    print()

    try:

        result = subprocess.run(
            command,
            check=False,
        )

        if result.returncode != 0:

            log_error(
                url,
                "video",
                f"yt-dlp exited with code {result.returncode}",
            )

            return False

        return True

    except Exception as error:

        log_error(
            url,
            "video",
            str(error),
        )

        return False


# ============================================================
# DOWNLOAD AUDIO
# ============================================================

def download_audio(
    url: str,
    output_dir: Path = AUDIO_DIR,
):
    """
    Tải audio và chuyển thành MP3.
    """

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    command = build_common_command(
        output_dir=output_dir,
        archive_file=AUDIO_ARCHIVE,
    )

    command.extend([
        # ----------------------------------------------------
        # Extract audio
        # ----------------------------------------------------

        "-x",

        "--audio-format",
        "mp3",

        "--audio-quality",
        "0",

        url,
    ])

    print()
    print("=" * 70)
    print("AUDIO")
    print("=" * 70)
    print(f"URL        : {url}")
    print(f"Destination: {output_dir}")
    print()

    try:

        result = subprocess.run(
            command,
            check=False,
        )

        if result.returncode != 0:

            log_error(
                url,
                "audio",
                f"yt-dlp exited with code {result.returncode}",
            )

            return False

        return True

    except Exception as error:

        log_error(
            url,
            "audio",
            str(error),
        )

        return False


# ============================================================
# GET PLAYLIST NAME
# ============================================================

def get_playlist_name(url: str) -> str:
    """
    Lấy tên playlist.

    Sử dụng cùng YouTube client web_embedded
    để tránh lỗi 403 khi truy vấn YouTube.
    """

    command = [
        sys.executable,
        "-m",
        "yt_dlp",

        # Quan trọng:
        # get_playlist_name() cũng phải dùng client này.
        *YOUTUBE_EXTRACTOR_ARGS,

        "--flat-playlist",

        "--print",
        "%(playlist_title)s",

        "--playlist-items",
        "1",

        url,
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )

    playlist_name = result.stdout.strip()

    if not playlist_name:

        raise ValueError(
            "Không thể lấy tên playlist."
        )

    # Đôi khi output có nhiều dòng
    playlist_name = playlist_name.splitlines()[0]

    return sanitize_filename(
        playlist_name
    )


# ============================================================
# DOWNLOAD PLAYLIST
# ============================================================

def download_playlist(
    url: str,
    mode: str = "video",
):
    """
    Tải playlist.

    mode:

        video
            downloads/playlists/<playlist>/
                001 - video1.mp4
                002 - video2.mp4

        audio
            downloads/playlists/<playlist>/
                001 - video1.mp3
                002 - video2.mp3

        both
            downloads/playlists/<playlist>/
                videos/
                    001 - video1.mp4
                    002 - video2.mp4

                audios/
                    001 - video1.mp3
                    002 - video2.mp3
    """

    valid_modes = {
        "video",
        "audio",
        "both",
    }

    if mode not in valid_modes:

        raise ValueError(
            f"Mode không hợp lệ: {mode}. "
            f"Chỉ chấp nhận: video, audio, both."
        )

    ensure_directories()

    print()
    print("=" * 70)
    print("PLAYLIST")
    print("=" * 70)
    print(f"URL : {url}")
    print(f"MODE: {mode}")
    print()

    # --------------------------------------------------------
    # Get playlist name
    # --------------------------------------------------------

    try:

        playlist_name = get_playlist_name(url)

    except subprocess.CalledProcessError as error:

        log_error(
            url,
            "playlist",
            f"Không lấy được tên playlist: {error}",
        )

        raise

    playlist_dir = (
        PLAYLIST_DIR / playlist_name
    )

    # ========================================================
    # VIDEO
    # ========================================================

    if mode == "video":

        print(
            f"📁 Destination: {playlist_dir}"
        )

        return download_video(
            url,
            playlist_dir,
        )

    # ========================================================
    # AUDIO
    # ========================================================

    if mode == "audio":

        print(
            f"📁 Destination: {playlist_dir}"
        )

        return download_audio(
            url,
            playlist_dir,
        )

    # ========================================================
    # BOTH
    # ========================================================

    if mode == "both":

        video_dir = (
            playlist_dir / "videos"
        )

        audio_dir = (
            playlist_dir / "audios"
        )

        print(
            f"📁 Video: {video_dir}"
        )

        print(
            f"📁 Audio: {audio_dir}"
        )

        video_success = download_video(
            url,
            video_dir,
        )

        audio_success = download_audio(
            url,
            audio_dir,
        )

        return (
            video_success
            and audio_success
        )


# ============================================================
# CONVERT WEBM -> MP3
# ============================================================

def convert_existing_webm_to_mp3(
    folder: Path,
):
    """
    Tìm các file .webm đã có sẵn trong folder,
    chuyển sang .mp3 bằng FFmpeg rồi xóa file .webm.

    Không gửi request tới YouTube.
    """

    webm_files = list(
        folder.glob("*.webm")
    )

    if not webm_files:

        print(
            "Không tìm thấy file .webm có sẵn."
        )

        return

    print(
        f"Tìm thấy {len(webm_files)} file .webm."
    )

    print(
        "Bắt đầu chuyển sang MP3...\n"
    )

    for webm_file in webm_files:

        mp3_file = webm_file.with_suffix(
            ".mp3"
        )

        # ----------------------------------------------------
        # MP3 đã tồn tại
        # ----------------------------------------------------

        if mp3_file.exists():

            print(
                f"✓ Đã có MP3: {mp3_file.name}"
            )

            webm_file.unlink()

            continue

        print(
            f"→ Đang chuyển: {webm_file.name}"
        )

        command = [
            "ffmpeg",

            "-y",

            "-i",
            str(webm_file),

            "-vn",

            "-codec:a",
            "libmp3lame",

            "-q:a",
            "0",

            str(mp3_file),
        ]

        result = subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        if (
            result.returncode == 0
            and mp3_file.exists()
        ):

            print(
                f"  ✓ MP3: {mp3_file.name}"
            )

            # Chỉ xóa WebM sau khi MP3
            # được tạo thành công.
            webm_file.unlink()

            print(
                "  ✓ Đã xóa file .webm"
            )

        else:

            print(
                f"  ✗ Không thể chuyển: "
                f"{webm_file.name}"
            )

            print(
                result.stderr
            )


# ============================================================
# MAIN
# ============================================================

def main():

    import argparse

    parser = argparse.ArgumentParser(
        description="YouTube Downloader"
    )

    parser.add_argument(
        "url",
        help="URL YouTube",
    )

    parser.add_argument(
        "-m",
        "--mode",
        choices=[
            "video",
            "audio",
            "both",
        ],
        default="video",
        help=(
            "video = video, "
            "audio = audio, "
            "both = cả hai"
        ),
    )

    parser.add_argument(
        "-p",
        "--playlist",
        action="store_true",
        help="URL là playlist",
    )

    args = parser.parse_args()

    ensure_directories()

    try:

        # ====================================================
        # PLAYLIST
        # ====================================================

        if args.playlist:

            # ------------------------------------------------
            # Lấy tên playlist
            # ------------------------------------------------

            playlist_name = get_playlist_name(
                args.url
            )

            playlist_dir = (
                PLAYLIST_DIR /
                playlist_name
            )

            playlist_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            # ------------------------------------------------
            # Chuyển WebM cũ -> MP3
            # ------------------------------------------------

            if args.mode in (
                "audio",
                "both",
            ):

                if args.mode == "audio":

                    convert_existing_webm_to_mp3(
                        playlist_dir
                    )

                elif args.mode == "both":

                    audio_dir = (
                        playlist_dir /
                        "audios"
                    )

                    convert_existing_webm_to_mp3(
                        audio_dir
                    )

            # ------------------------------------------------
            # Download
            # ------------------------------------------------

            success = download_playlist(
                args.url,
                args.mode,
            )

        # ====================================================
        # SINGLE VIDEO
        # ====================================================

        elif args.mode == "video":

            success = download_video(
                args.url
            )

        # ====================================================
        # SINGLE AUDIO
        # ====================================================

        elif args.mode == "audio":

            success = download_audio(
                args.url
            )

        # ====================================================
        # BOTH
        # ====================================================

        elif args.mode == "both":

            print(
                "Đang tải video..."
            )

            video_success = download_video(
                args.url
            )

            print(
                "Đang tải audio..."
            )

            audio_success = download_audio(
                args.url
            )

            success = (
                video_success
                and audio_success
            )

        # ====================================================
        # RESULT
        # ====================================================

        if success:

            print()
            print("=" * 70)
            print("✓ HOÀN TẤT")
            print("=" * 70)

        else:

            print()
            print("=" * 70)
            print("⚠ HOÀN TẤT NHƯNG CÓ LỖI")
            print("=" * 70)

            print(
                f"Chi tiết lỗi: {LOG_FILE}"
            )

    except KeyboardInterrupt:

        print()
        print(
            "Đã hủy bởi người dùng."
        )

    except Exception as error:

        print()
        print("=" * 70)
        print("✗ ERROR")
        print("=" * 70)
        print(error)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
