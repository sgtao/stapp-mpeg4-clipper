# 12_clip_multi_screenshots.py
import io
import os
import zipfile
import tempfile
from io import BytesIO
from moviepy import VideoFileClip
from PIL import Image
import streamlit as st


APP_TITLE = "📸 Multi Screenshot Selector (60s Clip)"


def initialize_session_state():
    if "screenshot_list" not in st.session_state:
        st.session_state.screenshot_list = []


def extract_screenshots(video_bytes, start_minute=0):
    """指定した分(start_minute)から60秒分のフレームを抽出"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(video_bytes)
        tmp_path = tmp.name

    clip = VideoFileClip(tmp_path)

    screenshots = []
    start_time = start_minute * 60
    end_time = min(start_time + 60, clip.duration)

    for i in range(int(start_time), int(end_time)):
        frame = clip.get_frame(i)
        image = Image.fromarray(frame)
        img_bytes = BytesIO()
        image.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        screenshots.append((i, img_bytes))

    clip.close()
    os.remove(tmp_path)
    return screenshots


def download_zip(selected_list):
    """選択したスクリーンショットをZIPにまとめて返す"""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for idx, item in enumerate(selected_list, start=1):
            zipf.writestr(f"Slide_{idx:03d}.png", item["image"].getvalue())
    zip_buffer.seek(0)
    return zip_buffer


def main():
    st.set_page_config(page_title=APP_TITLE)
    st.title(APP_TITLE)
    initialize_session_state()

    uploaded_file = st.file_uploader(
        "🎞 Upload MP4 file", type=["mp4", "mpeg4"]
    )
    if not uploaded_file:
        st.info("動画ファイルをアップロードしてください。")
        return

    video_bytes = uploaded_file.read()

    # ▼ スタート分指定
    start_minute = st.number_input(
        "開始分（0 = 冒頭から）", min_value=0, step=1, value=0
    )

    if st.button("🖼 Generate 60 Screenshots"):
        st.info("スクリーンショットを生成中です。少々お待ちください…")
        screenshots = extract_screenshots(
            video_bytes, start_minute=start_minute
        )

        st.session_state.generated_screens = screenshots
        st.success(
            f"{len(screenshots)} 枚のスクリーンショットを生成しました。"
        )

    if "generated_screens" not in st.session_state:
        return

    screenshots = st.session_state.generated_screens

    st.subheader("📷 Screenshots (1枚ごとにチェック可能)")
    selected_timestamps = []

    cols = st.columns(5)
    for i, (timestamp, img_bytes) in enumerate(screenshots):
        col = cols[i % 5]
        with col:
            checked = st.checkbox(f"{timestamp}s", key=f"chk_{timestamp}")
            st.image(
                img_bytes,
                # use_container_width=True
            )
            if checked:
                selected_timestamps.append((timestamp, img_bytes))

    st.write(f"✅ 選択枚数: {len(selected_timestamps)}")

    if st.button("Add ScreenShots"):
        for ts, img in selected_timestamps:
            item = {
                "id": len(st.session_state.screenshot_list) + 1,
                "timestamp": ts,
                "image": img,
            }
            st.session_state.screenshot_list.append(item)
        st.success(f"{len(selected_timestamps)}枚を候補リストに追加しました！")

    if len(st.session_state.screenshot_list) > 0:
        st.divider()
        st.subheader("📦 ダウンロード候補リスト")

        for item in st.session_state.screenshot_list:
            st.text(f"Slide_{item['id']:03d}  |  {item['timestamp']}s")

        if st.button("⬇️ Download Screen Shots (ZIP)"):
            zip_buffer = download_zip(st.session_state.screenshot_list)
            st.download_button(
                label="📦 Download ZIP",
                data=zip_buffer,
                file_name="Selected_Screenshots.zip",
                mime="application/zip",
            )


if __name__ == "__main__":
    main()
