# MultiScreenshot.py
import streamlit as st

from src.functions.VideoClipper import VideoClipper  # ✅ 追加
from functions.AppLogger import AppLogger

APP_TITLE = "Multi Screenshot Component"


class MultiScreenshot:
    def __init__(self, uploaded_file, app_title=APP_TITLE):
        if "app_logger" not in st.session_state:
            self.app_logger = AppLogger(app_title)
            self.app_logger.app_start()
            st.session_state.app_logger = self.app_logger
        else:
            self.app_logger = st.session_state.app_logger

        if uploaded_file is None:
            raise ValueError("No file uploaded.")
        video_bytes = uploaded_file.read()

        self.clipper = VideoClipper(video_bytes)
        self.filename = uploaded_file.name  # 元ファイル名を保持
        self.meta = self.clipper.get_metadata()
        self.app_logger.info_log(f"Load vide data : {self.filename}")
        st.session_state.filename = self.filename

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
            img_bytes, _, _ = self.clipper.get_screenshot_bytes(sec)
            screenshots.append((sec, img_bytes))

        return screenshots

    def seconds_to_timecode(self, seconds: float) -> str:
        """秒数を mm:ss の形式に変換する"""
        return self.clipper.seconds_to_timecode(seconds)

    def cleanup(self):
        """VideoClipperのクリーンアップ"""
        self.clipper.cleanup()
