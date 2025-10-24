# video_to_audio_app.py
import streamlit as st
from yt_dlp import YoutubeDL
import tempfile
import os
import shutil
from pathlib import Path
import imageio_ffmpeg as ffmpeg

st.set_page_config(page_title="Video ➜ Audio", page_icon="🎧")

st.title("🎬 ➜ 🎵 Video to Audio (MP3)")
st.write("Paste a video URL (YouTube, Vimeo, etc.), click Convert, then download the MP3.")

url = st.text_input("Video URL", placeholder="https://www.youtube.com/watch?v=...")
bitrate = st.selectbox("Output bitrate", ["192k", "128k", "320k"], index=0)
filename_prefix = st.text_input("Save as (prefix)", value="audio")

if st.button("Convert to MP3"):
    if not url.strip():
        st.error("Please paste a valid video URL.")
    else:
        with st.spinner("Downloading and converting..."):
            try:
                temp_dir = Path(tempfile.mkdtemp(prefix="v2a_"))
                out_template = str(temp_dir / f"{filename_prefix}.%(ext)s")

                # ✅ Get path to the bundled ffmpeg binary
                ffmpeg_path = ffmpeg.get_ffmpeg_exe()

                ydl_opts = {
                    "format": "bestaudio/best",
                    "outtmpl": out_template,
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": bitrate.replace("k", "")
                    }],
                    "postprocessor_args": ["-ar", "44100"],
                    "quiet": True,
                    "no_warnings": True,
                    # 🔽 Tell yt-dlp where ffmpeg is
                    "ffmpeg_location": ffmpeg_path
                }

                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    out_path = temp_dir / f"{filename_prefix}.mp3"

                    # Some sites may rename file — check for any .mp3
                    if not out_path.exists():
                        mp3_files = list(temp_dir.glob("*.mp3"))
                        if mp3_files:
                            out_path = mp3_files[0]
                        else:
                            raise FileNotFoundError("Converted MP3 not found.")

                # ✅ Serve audio
                audio_bytes = out_path.read_bytes()
                title = info.get("title") or filename_prefix
                st.success("Conversion complete ✅")
                st.audio(audio_bytes, format="audio/mp3")
                st.download_button(
                    label="⬇️ Download MP3",
                    data=audio_bytes,
                    file_name=f"{title}.mp3",
                    mime="audio/mpeg"
                )

            except Exception as e:
                st.error(f"Conversion failed: {e}")
            finally:
                try:
                    shutil.rmtree(str(temp_dir))
                except Exception:
                    pass

st.markdown("""
---
**No FFmpeg installation required 🎉**
- This app uses the lightweight `imageio-ffmpeg` package to include FFmpeg automatically.
- Works with most video sites supported by `yt-dlp`.
""")
