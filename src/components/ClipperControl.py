# ClipperControl.py
import streamlit as st

from functions.VideoClipper import VideoClipper


class ClipperControl:

    def __init__(self, clipper: VideoClipper):
        self.clipper = clipper
        self.meta = clipper.get_metadata()

    def render_clipper_video(self):
        st.video(self.clipper.get_video_bytes())
        st.write(f"⏱ Duration: {self.meta['duration']:.2f}s")
        st.write(f"🎞 FPS: {self.meta['fps']:.2f}")
        st.write(f"📏 Size: {self.meta['size'][0]}x{self.meta['size'][1]}")

    def render_single_screenshot(self):
        # Clip Screenshot
        timestamp_screen = st.slider(
            label="Screenshot time stamp(sec.)",
            min_value=0,
            max_value=int(self.meta["duration"]),
            value=1,
            step=1,
            format="%03d sec.",
        )
        img_bytes = self.clipper.get_screenshot_bytes(t=timestamp_screen)
        st.image(
            img_bytes,
            caption=f"📸 Screenshot at {timestamp_screen} sec.",
        )
