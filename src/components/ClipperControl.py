# ClipperControl.py
import io
import os
import tempfile

import streamlit as st

from functions.VideoClipper import VideoClipper


class ClipperControl:
    def __init__(self, uploaded_file):
        if "clip_timestamp" not in st.session_state:
            st.session_state.clip_timestamp = 1.0
        if uploaded_file is None:
            raise ValueError("No file uploaded.")
        video_bytes = uploaded_file.read()
        self.clipper = VideoClipper(video_bytes)
        # self.clipper.load()
        self.filename = uploaded_file.name  # 元ファイル名を保持
        self.meta = self.clipper.get_metadata()

    def format_time_mmss(self, timestamp: float) -> str:
        timestamp = int(timestamp)
        m = (timestamp % 3600) // 60
        s = timestamp % 60
        return f"{m:02d}-{s:02d}"

    def get_duration(self):
        return f"{int(self.meta["duration"]):03d}"

    def render_clipper_video(self):
        st.video(self.clipper.get_video_path())
        # screen_image = self.clipper.get_screenshot_bytes()
        # st.image(screen_image)
        st.write(f"⏱ Duration: {self.meta['duration']:.2f}s")
        st.write(f"🎞 FPS: {self.meta['fps']:.2f}")
        st.write(f"📏 Size: {self.meta['size'][0]}x{self.meta['size'][1]}")

    def _on_change_slider(self):
        st.session_state.clip_timestamp = st.session_state.clip_control_slider

    def _on_change_number(self):
        st.session_state.clip_timestamp = st.session_state.clip_control_number

    def render_timestamp_slider(self):
        return st.slider(
            label="slide Screenshot time stamp(sec.)",
            min_value=0,
            max_value=int(self.meta["duration"]),
            value=int(st.session_state.clip_timestamp),
            step=1,
            key="clip_control_slider",
            on_change=self._on_change_slider,
            format="%03d sec.",
        )

    def render_timestamp_input(self):
        return st.number_input(
            label=f"input screen timecode(sec, max: {self.get_duration()})",
            min_value=0,
            max_value=int(self.meta["duration"]),
            value=int(st.session_state.clip_timestamp),
            step=1,
            key="clip_control_number",
            on_change=self._on_change_number,
        )

    def get_filename(self) -> str:
        """使ったファイル名（拡張子前まで）を返す"""
        return os.path.splitext(os.path.basename(self.filename))[0]

    def get_screenshot_image(self, timestamp=0, scale=1.0):
        if timestamp == 0:
            timestamp = st.session_state.clip_timestamp

        # image_obj, size = self.clipper.get_screenshot_bytes(sec=timestamp)
        # print(f"image size: {size}")
        image_byte = self.clipper.get_screenshot_bytes(
            sec=timestamp,
            scale=scale,
        )
        return image_byte

    def render_single_screenshot(self, timestamp=0):
        # Clip Screenshot
        img_bytes, width, height = self.get_screenshot_image(timestamp)

        st.image(
            img_bytes,
            caption=f"📸 Screenshot at {timestamp} sec.",
        )
        return img_bytes

    def clip_video_range(self, output_path, start_sec, end_sec):
        # サブクリップ作成（メモリ上で切り出し）
        subclip = self.clipper.subclipped(start_sec, end_sec)

        # 書き出し（必要に応じてcodecを指定）
        subclip.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile="temp-audio.m4a",
            remove_temp=True,
        )

    def download_clipped_mp4(self, start_sec, end_sec):
        """選択したスクリーンをMP4にして返す"""
        try:
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".mp4"
            ) as tmp_file:
                tmp_path = tmp_file.name

            # 動画を切り出して一時ファイルに出力
            self.clip_video_range(
                output_path=tmp_path,
                start_sec=start_sec,
                end_sec=end_sec,
            )

            # 一時ファイルから読み込んでBytesIOに格納
            with open(tmp_path, "rb") as f:
                mp4_bytes = f.read()

            # 一時ファイルを削除
            os.remove(tmp_path)

            # メモリ上に返す
            return io.BytesIO(mp4_bytes)
        except Exception as e:
            raise e

    def cleanup(self):
        if self.clipper is not None:
            try:
                self.clipper.cleanup()
            except Exception as e:
                st.warning(f"⚠️ cleanup中にエラー: {e}")

        self.clipper = None
        self.meta = {"duration": 0, "fps": 0, "size": []}
