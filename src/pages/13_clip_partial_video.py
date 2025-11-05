# 13_clip_partial_video.py
# import io
import hashlib

import streamlit as st

from components.ClipperControl import ClipperControl
from functions.AppLogger import AppLogger

APP_TITLE = "Clip Partial Video Downloader"


def file_hash(file_obj):
    file_obj.seek(0)
    file_bytes = file_obj.read()
    file_obj.seek(0)
    return hashlib.md5(file_bytes).hexdigest()


def initialize_session_state():
    if "mpeg_hash" not in st.session_state:
        st.session_state.mpeg_hash = None
    if "clipper_control" not in st.session_state:
        st.session_state.clipper_control = None

    if "app_logger" not in st.session_state:
        app_logger = AppLogger(APP_TITLE)
        app_logger.app_start()
        st.session_state.app_logger = app_logger
    elif st.session_state.app_logger.name != APP_TITLE:
        app_logger = AppLogger(APP_TITLE)
        app_logger.app_start()
        st.session_state.app_logger = app_logger


def cleanup_clipper():
    clipper_control = st.session_state.get("clipper_control")
    if clipper_control:
        clipper_control.cleanup()
        st.session_state.mpeg_hash = None
        st.toast("🧹 一時ファイルを削除しました。")


def log_download_filename(filename):
    app_logger = st.session_state.app_logger
    app_logger.info_log(f"download as {filename}")


def main():
    st.set_page_config(page_title=APP_TITLE)
    st.page_link("main.py", label="🏠 Back to Home")
    st.subheader(f"✂️ {APP_TITLE}")

    uploaded_file = st.file_uploader(
        "🎞 Upload MP4 file",
        type=["mp4", "mpeg4"],
    )

    if uploaded_file is None:
        if st.session_state.mpeg_hash is not None:
            cleanup_clipper()
        return

    # ファイルのキャッシュ判定
    current_hash = file_hash(uploaded_file)
    if st.session_state.mpeg_hash != current_hash:
        cleanup_clipper()
        st.session_state.clipper_control = ClipperControl(uploaded_file)
        st.session_state.mpeg_hash = current_hash
        st.info("✅ 動画を読み込みました。")
    else:
        st.info("📁 既存キャッシュを使用中。")

    clipper_control = st.session_state.clipper_control
    clipper_control.render_clipper_video()

    duration = float(clipper_control.meta["duration"])

    st.divider()
    st.write("🎬 切り出したい動画範囲を指定してください")

    start_sec, end_sec = st.slider(
        "Select clip range (sec)", 0.0, duration, (0.0, duration / 2)
    )

    if start_sec >= end_sec:
        st.warning("⏱️ 開始時間は終了時間より小さくしてください。")
        return

    st.write(f"✂️ {start_sec:.1f}s ～ {end_sec:.1f}s の動画を切り出します。")

    if st.button("🎥 Generate and Download Clip", type="primary"):
        st.info("動画を切り出しています... しばらくお待ちください。")
        try:
            # 一時ファイル作成
            with st.spinner():
                clipped_mp4_buffer = clipper_control.download_clipped_mp4(
                    start_sec=start_sec,
                    end_sec=end_sec,
                )
                st.success("✅ 切り出しが完了しました！")

            # Download
            mp4_filename = (
                f"{clipper_control.get_filename()}_"
                + f"{int(start_sec)}s_to_{int(end_sec)}s.mp4"
            )
            st.download_button(
                label="📥 Download MP4",
                data=clipped_mp4_buffer,
                file_name=mp4_filename,
                mime="application/mpeg",
                on_click=log_download_filename,
                args=[mp4_filename],
            )

        except Exception as e:
            st.error(f"❌ エラーが起きました！ {e}")


if __name__ == "__main__":
    initialize_session_state()
    main()
