# 12_clip_multi_screenshots.py
import io

# import os
import time
import zipfile

import pandas as pd
import streamlit as st

from src.functions.VideoClipper import VideoClipper  # ✅ 追加

APP_TITLE = "Multi Screenshot Selector (60s Clip)"


def initialize_session_state():
    if "filename" not in st.session_state:
        st.session_state.filename = ""
    if "multi_shot" not in st.session_state:
        st.session_state.multi_shot = None
    if "selected_minute" not in st.session_state:
        st.session_state.selected_minute = 0
    if "generated_screens" not in st.session_state:
        st.session_state.generated_screens = []
    if "screenshot_list" not in st.session_state:
        st.session_state.screenshot_list = []


class MultiScreenshot:
    def __init__(self, uploaded_file):
        if uploaded_file is None:
            raise ValueError("No file uploaded.")
        video_bytes = uploaded_file.read()
        self.clipper = VideoClipper(video_bytes)
        # self.clipper.load()
        self.filename = uploaded_file.name  # 元ファイル名を保持
        st.session_state.filename = self.filename
        self.meta = self.clipper.get_metadata()

    def get_meta_info(self):
        """メタデータを取得"""
        return self.meta

    def extract_screenshots(self, start_minute=0, end_minute=0, step=1):
        # clip = VideoFileClip(self.tmp_path)
        screenshots = []
        start_time = start_minute * 60
        if end_minute > 0:
            end_time = min(end_minute * 60, self.meta["duration"])
        else:
            end_time = min(start_time + 60, self.meta["duration"])

        for sec in range(int(start_time), int(end_time), step):
            img_bytes = self.clipper.get_screenshot_bytes(sec)
            screenshots.append((sec, img_bytes))

        return screenshots

    def seconds_to_timecode(self, seconds: float) -> str:
        """秒数を mm:ss の形式に変換する"""
        return self.clipper.seconds_to_timecode(seconds)

    def cleanup(self):
        """VideoClipperのクリーンアップ"""
        self.clipper.cleanup()


def _on_change_file_ms():
    if st.session_state.multi_shot is not None:
        multi_shot = st.session_state.multi_shot
        multi_shot.cleanup()
        st.session_state.multi_shot = None
        st.session_state.generated_screens = []
        st.session_state.screenshot_list = []


def _on_change_minite_ms():
    st.session_state.generated_screens = []


def download_zip(selected_list):
    """選択したスクリーンショットをZIPにまとめて返す"""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for idx, item in enumerate(selected_list, start=1):
            # zipf.writestr(f"Slide_{idx:03d}.png", item["image"].getvalue())
            zipf.writestr(f"Slide_{idx}.png", item["image"].getvalue())
    zip_buffer.seek(0)
    return zip_buffer


@st.dialog(
    title="Screenshots in specified minute",
    width="medium",
)
def select_screenshots_dialog(start_minute):
    multi_shot = st.session_state.multi_shot
    screenshots = multi_shot.extract_screenshots(
        # video_bytes, start_minute=start_minute
        start_minute=start_minute
    )

    st.session_state.generated_screens = screenshots
    # st.success(
    #     f"{len(screenshots)} 枚のスクリーンショットを生成しました。"
    # )

    st.subheader(f"📷 Screenshots at {start_minute}m (1枚ごとにチェック可能)")
    selected_timestamps = []

    cols = st.columns(5)
    for i, (timestamp, img_bytes) in enumerate(screenshots):
        col = cols[i % 5]
        with col:
            time_str = multi_shot.seconds_to_timecode(timestamp)
            checked = st.checkbox(label=time_str, key=f"chk_{timestamp}")
            st.image(
                img_bytes,
                # use_container_width=True
            )
            if checked:
                selected_timestamps.append((time_str, img_bytes))

    st.write(f"✅ 選択枚数: {len(selected_timestamps)}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Add ScreenShots", type="primary"):
            for ts, img in selected_timestamps:
                item = {
                    "id": len(st.session_state.screenshot_list) + 1,
                    "timestamp": ts,
                    "image": img,
                }
                st.session_state.screenshot_list.append(item)
            st.success(
                body=f"{len(selected_timestamps)}枚を候補リストに追加しました！",
                icon="👍"
            )
    with col2:
        if st.button("Close"):
            st.info("モーダルを閉じます")
            time.sleep(2)
            st.rerun()


def main():
    st.set_page_config(page_title=APP_TITLE)
    st.page_link("main.py", label="Back to Home", icon="🏠")
    st.subheader(f"📹 {APP_TITLE}")

    uploaded_file = st.file_uploader(
        "🎞 Upload MP4 file",
        type=["mp4", "mpeg4"],
        key="file_uploader_mshot",
        on_change=_on_change_file_ms,
    )
    if not uploaded_file:
        st.info("動画ファイルをアップロードしてください。")
        return

    if st.session_state.multi_shot is None:
        st.session_state.multi_shot = MultiScreenshot(uploaded_file)

    # 動画再生 & メタ情報表示
    multi_shot = st.session_state.multi_shot
    meta = multi_shot.get_meta_info()
    # st.json(meta)

    minute_shots = multi_shot.extract_screenshots(
        start_minute=0,
        end_minute=999,
        step=60,
    )
    if len(minute_shots) > 0:
        st.subheader(f"📷 Screenshots Each Minutes ({len(minute_shots)})")

        cols = st.columns(5)
        for i, (timestamp, img_bytes) in enumerate(minute_shots):
            col = cols[i % 5]
            with col:
                time_str = multi_shot.seconds_to_timecode(timestamp)
                st.image(
                    img_bytes,
                )
                if st.button(time_str):
                    st.session_state.selected_minute = timestamp // 60
                    select_screenshots_dialog(
                        start_minute=st.session_state.selected_minute,
                    )

    start_minute = st.number_input(
        f"Scraped Minite（0 = start, max_value={int(meta['duration']/60)})",
        min_value=0,
        max_value=int(meta["duration"] / 60),
        step=1,
        value=st.session_state.selected_minute,
        on_change=_on_change_minite_ms,
    )

    if st.button("🖼 Generate 60 Screenshots"):
        st.info("スクリーンショットを生成中です。少々お待ちください…")
        st.session_state.generated_screens = []
        screenshots = multi_shot.extract_screenshots(
            # video_bytes, start_minute=start_minute
            start_minute=start_minute
        )

        st.session_state.generated_screens = screenshots
        st.success(
            f"{len(screenshots)} 枚のスクリーンショットを生成しました。"
        )

    if len(st.session_state.screenshot_list) > 0:
        st.divider()
        st.subheader("📦 ダウンロード候補リスト")

        # 表示用に必要な列だけ抽出（id と timestamp）
        # for item in st.session_state.screenshot_list:
        #     st.text(f"Slide_{item['id']}  |  {item['timestamp']}")
        # DataFrameに変換
        df = pd.DataFrame(st.session_state.screenshot_list)
        df_display = df[["id", "timestamp"]].rename(
            columns={"id": "Slide ID", "timestamp": "Timestamp"}
        )

        # 表形式で表示
        st.dataframe(df_display, use_container_width=True)

        if st.button("⬇️ Download Screen Shots (ZIP)"):
            zip_buffer = download_zip(st.session_state.screenshot_list)
            st.download_button(
                label="📦 Download ZIP",
                data=zip_buffer,
                file_name="Selected_Screenshots.zip",
                mime="application/zip",
            )


if __name__ == "__main__":
    initialize_session_state()
    main()
