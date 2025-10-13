# 11_clip_single_screen.py
import hashlib

import streamlit as st

from functions.VideoClipper import VideoClipper

APP_TITLE = "Clip Single Screenshot App."


def file_hash(file_obj):
    """アップロードファイルのハッシュを生成（キャッシュ判定用）"""
    file_obj.seek(0)
    file_bytes = file_obj.read()
    file_obj.seek(0)
    return hashlib.md5(file_bytes).hexdigest()


def initialize_session_state():
    for key in ["mpeg_hash", "clipper"]:
        if key not in st.session_state:
            st.session_state[key] = None


def cleanup_clipper():
    """アップロード解除時に一時ファイルを削除"""
    clipper = st.session_state.get("clipper")
    if clipper:
        clipper.cleanup()
        st.session_state.clipper = None
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
        cleanup_clipper()  # 古いデータ削除
        clipper = VideoClipper(uploaded_file)
        clipper.load()
        st.session_state.mpeg_hash = current_hash
        st.session_state.clipper = clipper
    else:
        clipper = st.session_state.clipper
        st.info("キャッシュされた動画を再利用します。")

    # 動画再生 & メタ情報表示
    meta = clipper.get_metadata()
    with st.expander(f"File: {uploaded_file.name}", expanded=False):
        st.video(clipper.get_video_bytes())
        st.write(f"⏱ Duration: {meta['duration']:.2f}s")
        st.write(f"🎞 FPS: {meta['fps']:.2f}")
        st.write(f"📏 Size: {meta['size'][0]}x{meta['size'][1]}")

    # Screenshot
    timestamp_screen = st.slider(
        label="Screenshot time stamp(sec.)",
        min_value=0,
        max_value=int(meta['duration']),
        value=1,
        step=1,
        format=f"%03d sec.",
    )
    img_bytes = clipper.get_screenshot_bytes(t=timestamp_screen)
    st.image(
        img_bytes,
        caption=f"📸 Screenshot at {timestamp_screen} sec.",
    )


if __name__ == "__main__":
    initialize_session_state()
    main()
