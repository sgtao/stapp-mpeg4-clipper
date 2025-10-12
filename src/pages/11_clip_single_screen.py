# 11_clip_single_screen.py
import os
import tempfile

import streamlit as st
from moviepy import VideoFileClip

APP_TITLE = "Clip Single Screenshot App."


def initialize_session_state():
    if "mpeg_filename" not in st.session_state:
        st.session_state.mpeg_filename = ""
    if "video_bytes" not in st.session_state:
        st.session_state.video_bytes = None
    if "tmp_path" not in st.session_state:
        st.session_state.tmp_path = None

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

    if st.session_state.mpeg_filename == "":
        st.session_state.mpeg_filename = uploaded_file.name
    if st.session_state.video_bytes is None:
        st.session_state.video_bytes = uploaded_file.read()

    with st.expander(
        label=f"File: {st.session_state.mpeg_filename}",
        expanded=False,
    ):
        st.video(
            # data=uploaded_file,
            data=uploaded_file,
        )

    # キャッシュ or 新規読み込み
    if uploaded_file.name != st.session_state.mpeg_filename:
        # 新しいファイル → 一時ファイル作成
        video_bytes = uploaded_file.read()
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        tmp.write(video_bytes)
        tmp.close()
        st.session_state.video_bytes = video_bytes
        st.session_state.tmp_path = tmp.name
        st.session_state.mpeg_filename = uploaded_file.name
        st.info(f"💾 新しい一時ファイルを作成しました: {tmp.name}")
    else:
        st.info("キャッシュされた動画を再利用します。")

    tmp_path = st.session_state.tmp_path

    # 動画情報とスクリーンショット
    with VideoFileClip(tmp_path) as clip:
        st.code(f"動画の長さ: {clip.duration:.2f} 秒")
        st.code(f"フレームレート: {clip.fps:.2f} fps")
        st.code(f"サイズ: {clip.w}x{clip.h} ピクセル")

        screenshot_path = os.path.join(os.path.dirname(tmp_path), "screenshot.png")
        clip.save_frame(screenshot_path, t=2.0)
        st.image(screenshot_path, caption="📸 2秒目のスクリーンショット")


if __name__ == "__main__":
    initialize_session_state()
    main()
