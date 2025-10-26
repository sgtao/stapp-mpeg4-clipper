# ClipperControl.py
import streamlit as st

from functions.VideoClipper import VideoClipper


class ClipperControl:
    def __init__(self, uploaded_file):
        if "clip_timestamp" not in st.session_state:
            st.session_state.clip_timestamp = 1.0
        self.clipper = VideoClipper(uploaded_file)
        # self.clipper.load()
        self.meta = self.clipper.get_metadata()

    def format_time_mmss(self, timestamp: float) -> str:
        timestamp = int(timestamp)
        m = (timestamp % 3600) // 60
        s = timestamp % 60
        return f"{m:02d}-{s:02d}"

    def render_clipper_screenshot(self):
        st.video(self.clipper.get_screenshot_bytes())
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
            label="change Screenshot time stamp(sec.)",
            min_value=0,
            max_value=int(self.meta["duration"]),
            value=int(st.session_state.clip_timestamp),
            step=1,
            key="clip_control_number",
            on_change=self._on_change_number,
        )

    def render_single_screenshot(self, timestamp=0):
        if timestamp == 0:
            timestamp = st.session_state.clip_timestamp
        # Clip Screenshot
        img_bytes = self.clipper.get_screenshot_bytes(sec=timestamp)
        st.image(
            img_bytes,
            caption=f"📸 Screenshot at {timestamp} sec.",
        )

    def cleanup(self):
        if self.clipper is not None:
            try:
                self.clipper.cleanup()
            except Exception as e:
                st.warning(f"⚠️ cleanup中にエラー: {e}")

        self.clipper = None
        self.meta = {"duration": 0, "fps": 0, "size": []}

    def reset_clipper(self, uploaded_file):
        self.cleanup()
        self.clipper = VideoClipper(uploaded_file)
        self.meta = self.clipper.get_metadata()
