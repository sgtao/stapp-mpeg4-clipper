# 11_clip_single_screen.py
import hashlib

import streamlit as st

from components.ClipperControl import ClipperControl

APP_TITLE = "Clip Single Screenshot App."


def file_hash(file_obj):
    """アップロードファイルのハッシュを生成（キャッシュ判定用）"""
    file_obj.seek(0)
    file_bytes = file_obj.read()
    file_obj.seek(0)
    return hashlib.md5(file_bytes).hexdigest()


def initialize_session_state():
    if "mpeg_hash" not in st.session_state:
        st.session_state.mpeg_hash = None
    if "clipper_control" not in st.session_state:
        st.session_state.clipper_control = None


def cleanup_clipper():
    """アップロード解除時に一時ファイルを削除"""
    clipper_control = st.session_state.get("clipper_control")
    if clipper_control:
        clipper_control.cleanup()
        st.session_state.mpeg_hash = None
        st.toast("🧹 一時ファイルを削除しました。")


def main():
    st.page_link("main.py", label="Back to Home", icon="🏠")
    st.subheader(f"📸 {APP_TITLE}")

    uploaded_file = st.file_uploader(
        label="Upload mpeg-4 data",
        accept_multiple_files=False,
        type=["mp4", "mpeg4"],
    )

    if uploaded_file is None:
        # ファイル削除検知
        if st.session_state.mpeg_hash is not None:
            cleanup_clipper()
        return

    # ハッシュ比較で再アップロード判定
    current_hash = file_hash(uploaded_file)
    if st.session_state.mpeg_hash != current_hash:
        cleanup_clipper()
        st.session_state.clipper_control = ClipperControl(uploaded_file)
        st.session_state.mpeg_hash = current_hash
        st.info("Loaded Video data into cache.")
    else:
        st.info("Reload Video data from cache.")

    # 動画再生 & メタ情報表示
    clipper_control = st.session_state.clipper_control
    with st.expander(f"File: {uploaded_file.name}", expanded=False):
        clipper_control.render_clipper_screenshot()

    # select timestamp
    timestamp = clipper_control.render_timestamp_slider()

    clipper_control.render_timestamp_input()

    # Clip Screenshot
    clipper_control.render_single_screenshot(timestamp)

    # ダウンロードボタン
    screenshot_bytes = clipper_control.clipper.get_screenshot_bytes(
        sec=timestamp
    )
    time_str = clipper_control.format_time_mmss(timestamp)
    st.write("timestamp:")
    st.code(time_str.replace("-", ":"))
    download_filename = f"{clipper_control.get_filename()}_{time_str}.png"

    st.download_button(
        label="📥 Download Screenshot",
        data=screenshot_bytes,
        file_name=download_filename,
        mime="image/png",
    )


if __name__ == "__main__":
    initialize_session_state()
    main()
