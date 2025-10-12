# 11_clip_single_screen.py
import os
import tempfile

import streamlit as st
from moviepy import VideoFileClip

APP_TITLE = "Clip Single Screenshot App."


def initialize_session_state():
    if "mpeg_filename" not in st.session_state:
        st.session_state.mpeg_filename = ""


def main():
    st.page_link("main.py", label="Back to Home", icon="🏠")

    st.subheader(f"📸 {APP_TITLE}")

    # upload mpeg-4 file
    uploaded_file = st.file_uploader(
        label="Upload mpeg-4 data",
        accept_multiple_files=False,
        type=["mp4", "mpeg4"],
    )

    if uploaded_file is not None:
        with st.expander(
            label=f"File: {uploaded_file.name}",
            expanded=False,
        ):
            st.video(
                data=uploaded_file,
            )

        # 🔹 一時ファイルとして保存
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name  # MoviePyが読み取れる実ファイルパス

        # 🔹 動画情報の取得とスクリーンショット生成
        with VideoFileClip(tmp_path) as clip:
            st.code(f"動画の長さ: {clip.duration:.2f} 秒")
            st.code(f"フレームレート: {clip.fps:.2f} fps")
            st.code(f"サイズ: {clip.w}x{clip.h} ピクセル")

            # 2秒地点のフレームを保存
            screenshot_path = os.path.join(
                os.path.dirname(tmp_path), "screenshot.png"
            )
            clip.save_frame(screenshot_path, t=2.0)
            st.image(screenshot_path, caption="📸 2秒目のスクリーンショット")

        # 一時ファイルを削除
        os.remove(tmp_path)


if __name__ == "__main__":
    initialize_session_state()
    main()
