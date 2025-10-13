# VideoClipper.py
import os
import tempfile
from io import BytesIO
from moviepy import VideoFileClip
from PIL import Image


class VideoClipper:
    """
    VideoClipper: UploadedFileから動画情報を取得し、
    指定時刻のフレームをスクリーンショットとして生成するユーティリティクラス。
    """

    def __init__(self, uploaded_file):
        self.uploaded_file = uploaded_file
        self.tmp_path = None
        self.clip = None

    def load(self):
        """アップロードファイルを一時保存し、VideoFileClipとして読み込む"""
        if self.uploaded_file is None:
            raise ValueError("No file uploaded.")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(self.uploaded_file.read())
            self.tmp_path = tmp.name

        self.clip = VideoFileClip(self.tmp_path)

    def get_metadata(self):
        """動画の基本情報を辞書で返す"""
        if not self.clip:
            raise RuntimeError("Clip not loaded. Call load() first.")

        return {
            "duration": self.clip.duration,
            "fps": self.clip.fps,
            "size": (self.clip.w, self.clip.h),
        }

    def get_video_bytes(self) -> bytes:
        """一時ファイルの動画データをバイト列として返す"""
        if not self.tmp_path:
            raise RuntimeError("Temporary video not available.")
        with open(self.tmp_path, "rb") as f:
            return f.read()

    def get_screenshot_bytes(self, t: float = 1.0) -> BytesIO:
        """指定時刻tのフレームをPIL画像として取得し、BytesIOに変換して返す"""
        if not self.clip:
            raise RuntimeError("Clip not loaded. Call load() first.")

        frame = self.clip.get_frame(t)
        image = Image.fromarray(frame)
        img_bytes = BytesIO()
        image.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        return img_bytes

    def cleanup(self):
        """一時ファイルを削除してリソースを解放"""
        if self.clip:
            self.clip.close()
        if self.tmp_path and os.path.exists(self.tmp_path):
            os.remove(self.tmp_path)
            self.tmp_path = None
