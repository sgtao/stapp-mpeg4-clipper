# 11_clip_single_screen.py
import os
import tempfile

import streamlit as st
from moviepy import VideoFileClip

from functions.VideoClipper import VideoClipper

APP_TITLE = "Clip Single Screenshot App."


def initialize_session_state():
    if "mpeg_filename" not in st.session_state:
        st.session_state.mpeg_filename = ""
    if "video_bytes" not in st.session_state:
        st.session_state.video_bytes = None
    if "tmp_path" not in st.session_state:
        st.session_state.tmp_path = None
    if "clipper" not in st.session_state:
        st.session_state.clipper = None


def cleanup_tempfile():
    """アップロード解除時に一時ファイルを削除"""
    tmp_path = st.session_state.get("tmp_path")
    if tmp_path and os.path.exists(tmp_path):
        os.remove(tmp_path)
        st.info(f"🧹 一時ファイルを削除しました: {tmp_path}")
    st.session_state.video_bytes = None
    st.session_state.tmp_path = None
    st.session_state.mpeg_filename = None


def main():
    st.page_link("main.py", label="Back to Home", icon="🏠")

    st.subheader(f"📸 {APP_TITLE}")

    # upload mpeg-4 file
    uploaded_file = st.file_uploader(
        label="Upload mpeg-4 data",
        accept_multiple_files=False,
        type=["mp4", "mpeg4"],
    )

    if uploaded_file is None:
        # ファイル削除を検知
        if st.session_state.mpeg_filename is not None:
            cleanup_tempfile()
        # early return
        return

    # キャッシュ or 新規読み込み
    clipper = st.session_state.clipper
    if uploaded_file.name != st.session_state.mpeg_filename:
        
        clipper = VideoClipper(uploaded_file)
        clipper.load()

        # 新しいファイル → 一時ファイル作成
        st.session_state.mpeg_filename = uploaded_file.name
        # st.info(f"💾 新しい一時ファイルを作成しました: {tmp.name}")
    else:
        st.info("キャッシュされた動画を再利用します。")

    with st.expander(
        label=f"File: {st.session_state.mpeg_filename}",
        expanded=False,
    ):
        st.video(
            # data=uploaded_file,
            data=clipper.get_tmp_path(),
        )
        meta = clipper.get_metadata()
        st.write(f"⏱ Duration: {meta['duration']:.2f}s")
        st.write(f"🎞 FPS: {meta['fps']:.2f}")
        st.write(f"📏 Size: {meta['size'][0]}x{meta['size'][1]}")

    # Screenshot at 2 seconds
    img_bytes = clipper.get_screenshot_bytes(t=2.0)
    st.image(img_bytes, caption="📸 2秒目のスクリーンショット")

    clipper.cleanup()


if __name__ == "__main__":
    initialize_session_state()
    main()
