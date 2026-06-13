import yt_dlp
from pydub import AudioSegment
import os

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_youtube_audio(url: str) -> str:
    print(f"URL RECEIVED: {url}")

    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "noplaylist": True,
        "quiet": False,
        "extractor_args": {
            "youtube": {
                "player_client": ["android"]
            }
        },
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            filename = ydl.prepare_filename(info)

            filename = (
                filename.replace(".webm", ".wav")
                .replace(".m4a", ".wav")
                .replace(".mp4", ".wav")
            )

            return filename

    except Exception as e:
        raise Exception(
            f"YouTube download failed: {str(e)}\n"
            "Try uploading the audio/video file directly."
        )


def convert_to_wav(input_path: str) -> str:
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"

    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)

    audio.export(output_path, format="wav")

    return output_path


def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:
    audio = AudioSegment.from_wav(wav_path)

    chunk_ms = chunk_minutes * 60 * 1000

    chunks = []

    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start:start + chunk_ms]

        chunk_path = f"{wav_path}_chunk_{i}.wav"

        chunk.export(chunk_path, format="wav")

        chunks.append(chunk_path)

    return chunks


def process_input(source: str) -> list:

    print(f"SOURCE RECEIVED: {source}")

    if source.startswith("http://") or source.startswith("https://"):

        print("Detected YouTube URL. Downloading audio...")

        try:
            wav_path = download_youtube_audio(source)

        except Exception as e:
            raise Exception(
                f"{e}\n\n"
                "YouTube may block downloads on Streamlit Cloud.\n"
                "Please upload an audio/video file instead."
            )

    else:

        print("Detected local file. Converting to WAV...")

        wav_path = convert_to_wav(source)

    print("Chunking audio...")

    chunks = chunk_audio(wav_path)

    print(f"Audio ready — {len(chunks)} chunk(s) created.")

    return chunks