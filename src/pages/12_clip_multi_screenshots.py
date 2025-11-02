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

    def get_filename(self):
        """選択ファイルを取得"""
        return self.filename

    def get_meta_info(self):
        """メタデータを取得"""
        return self.meta

    def extract_screenshots(self, start_minute=0, period_sec=0, step=1):
        # clip = VideoFileClip(self.tmp_path)
        screenshots = []
        start_time = start_minute * 60
        if period_sec > 0:
            end_time = min(start_minute + period_sec, self.meta["duration"])
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
        # st.session_state.multi_shot = None
        # st.session_state.screenshot_list = []
        st.session_state.clear()


def download_zip(selected_list):
    """選択したスクリーンショットをZIPにまとめて返す"""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for idx, item in enumerate(selected_list, start=1):
            # zipf.writestr(f"Slide_{idx:03d}.png", item["image"].getvalue())
            zipf.writestr(f"Slide_{idx}.png", item["image"].getvalue())
    zip_buffer.seek(0)
    return zip_buffer


def generate_screen_cache_key(minute):
    return f"screens_{minute}"


@st.dialog(
    title="Screenshots in specified minute",
    width="medium",
)
def select_screenshots_dialog(start_minute):
    multi_shot = st.session_state.multi_shot
    selected_minute = st.session_state.selected_minute
    video_meta = multi_shot.get_meta_info()
    if selected_minute == start_minute:
        cache_key = generate_screen_cache_key(start_minute)
    else:
        cache_key = generate_screen_cache_key(selected_minute)

    st.subheader(
        f"📷 Screenshots on {selected_minute}m (`Add`でチェック画像を取得）"
    )
    st.write(f"start minute: {start_minute}")

    screenshots = None
    selected_timestamps = []
    if cache_key not in st.session_state:
        st.info("📸 スクリーンショットを生成中...")
        screenshots = multi_shot.extract_screenshots(selected_minute)
        st.session_state[cache_key] = screenshots
    else:
        screenshots = st.session_state[cache_key]

    cols = st.columns(5)
    for i, (timestamp, img_bytes) in enumerate(screenshots):
        col = cols[i % 5]
        with col:
            st.image(img_bytes)
            time_str = multi_shot.seconds_to_timecode(timestamp)
            checked = st.checkbox(
                label=time_str, key=f"chk_{start_minute}_{timestamp}"
            )
            if checked:
                selected_timestamps.append((time_str, img_bytes))

    st.write(f"✅ 選択枚数: {len(selected_timestamps)}")

    col_l, col_r = st.columns(2)
    with col_l:
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
                icon="👍",
            )
    with col_r:
        r1, r2, r3 = st.columns(3)
        with r1:
            if st.button(label="", icon="⏪", disabled=(selected_minute <= 0)):
                st.session_state.selected_minute -= 1
                st.rerun(scope="fragment")
        with r2:
            next_tail_sec = (selected_minute + 1) * 60
            if st.button(
                label="",
                icon="⏩",
                disabled=(next_tail_sec > video_meta["duration"]),
            ):
                st.session_state.selected_minute += 1
                st.rerun(scope="fragment")
        with r3:
            if st.button("Close"):
                st.info("Closing...")
                time.sleep(1)
                st.rerun(scope="app")


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
    # meta = multi_shot.get_meta_info()
    # st.json(meta)

    minute_shots = multi_shot.extract_screenshots(
        start_minute=0,
        period_sec=9999,
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
                    select_screenshots_dialog(timestamp // 60)

    if len(st.session_state.screenshot_list) > 0:
        st.divider()
        st.subheader("📦 ダウンロード候補リスト")

        # 表示用に必要な列だけ抽出（id と timestamp）
        df = pd.DataFrame(st.session_state.screenshot_list)
        df_display = df[["id", "timestamp"]].rename(
            columns={"id": "Slide ID", "timestamp": "Timestamp"}
        )

        # 表形式で表示
        st.dataframe(data=df_display, width="stretch")

        # ---------------------------
        # ダウンロード機能
        # ---------------------------
        col1, col2, col3 = st.columns(3)
        with col1:
            # TimeStamp(CSV) ダウンロード機能
            csv_buffer = io.StringIO()
            df_display.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            csv_filename = (
                f"Selected_Timestamps_{multi_shot.get_filename()}.csv"
            )
            st.download_button(
                label="📄 Download Timestamp List (CSV)",
                data=csv_data,
                file_name=csv_filename,
                mime="text/csv",
            )
        with col2:
            pass
        with col3:
            # Snapshots(ZIP, png) ダウンロード機能
            if st.button("⬇️ Download Screen Shots (ZIP)"):
                zip_buffer = download_zip(st.session_state.screenshot_list)
                zip_filename = f"Screenshots_{multi_shot.get_filename()}.zip"
                st.download_button(
                    label="📦 Download ZIP",
                    data=zip_buffer,
                    file_name=zip_filename,
                    mime="application/zip",
                )


if __name__ == "__main__":
    initialize_session_state()
    main()
