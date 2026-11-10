
import streamlit as st
import subprocess
import imageio_ffmpeg
import tempfile
import os
import re
import zipfile
import io

st.set_page_config(
    page_title="RIIF Clipper AI",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 RIIF CLIPPER AI")
st.caption("Turn long videos into short videos")

st.markdown("""
Upload video panjang kamu dan buat beberapa klip
pendek untuk TikTok, Reels, dan YouTube Shorts.
""")

video = st.file_uploader(
    "📁 Upload video",
    type=["mp4", "mov", "mkv"]
)

jumlah = st.selectbox(
    "Jumlah klip",
    [1, 2, 3, 5],
    index=2
)

durasi = st.slider(
    "Durasi setiap klip (detik)",
    15, 60, 30
)

if st.button("🚀 GENERATE CLIPS", type="primary"):

    if video is None:
        st.error("Upload video terlebih dahulu!")

    else:
        with st.spinner("Sedang memproses video..."):

            try:
                ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

                with tempfile.TemporaryDirectory() as tmp:

                    input_path = os.path.join(
                        tmp, "input.mp4"
                    )

                    with open(input_path, "wb") as f:
                        f.write(video.getvalue())

                    # Membaca durasi video
                    probe = subprocess.run(
                        [ffmpeg, "-i", input_path],
                        capture_output=True,
                        text=True
                    )

                    match = re.search(
                        r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)",
                        probe.stderr
                    )

                    if not match:
                        st.error("Durasi video tidak terbaca.")
                        st.stop()

                    h, m, s = match.groups()

                    total = (
                        int(h) * 3600
                        + int(m) * 60
                        + float(s)
                    )

                    if total < 5:
                        st.error("Video terlalu pendek.")
                        st.stop()

                    clip_length = min(durasi, total)

                    max_start = max(
                        0, total - clip_length
                    )

                    starts = [
                        max_start * i / max(1, jumlah - 1)
                        for i in range(jumlah)
                    ]

                    zip_buffer = io.BytesIO()
                    berhasil = 0

                    with zipfile.ZipFile(
                        zip_buffer, "w",
                        zipfile.ZIP_DEFLATED
                    ) as archive:

                        for i, start in enumerate(
                            starts, 1
                        ):
                            output = os.path.join(
                                tmp, f"riif_clip_{i}.mp4"
                            )

                            command = [
                                ffmpeg, "-y",
                                "-ss", str(start),
                                "-i", input_path,
                                "-t", str(clip_length),
                                "-vf",
                                "scale=720:1280:"
                                "force_original_aspect_ratio=increase,"
                                "crop=720:1280",
                                "-c:v", "libx264",
                                "-preset", "ultrafast",
                                "-crf", "28",
                                "-c:a", "aac",
                                "-movflags", "+faststart",
                                output
                            ]

                            result = subprocess.run(
                                command,
                                capture_output=True,
                                text=True
                            )

                            if (
                                result.returncode == 0
                                and os.path.exists(output)
                            ):
                                archive.write(
                                    output,
                                    f"RIIF_Clip_{i}.mp4"
                                )
                                berhasil += 1

                    if berhasil:
                        st.success(
                            f"Berhasil membuat {berhasil} klip!"
                        )

                        st.download_button(
                            "⬇️ DOWNLOAD SEMUA KLIP",
                            data=zip_buffer.getvalue(),
                            file_name="RIIF_Clips.zip",
                            mime="application/zip"
                        )
                    else:
                        st.error(
                            "Gagal memproses video. "
                            "Coba video MP4 lain."
                        )

            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")

st.divider()
st.caption("RIIF CLIPPER AI | Version 1.0")
                  
