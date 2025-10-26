# VideoClipper.py
import os
import tempfile
from io import BytesIO
from moviepy import VideoFileClip
from PIL import Image


class VideoClipper:
    """
    VideoClipper:
    StreamlitのFileオブジェクトから動画情報を扱うユーティリティクラス。
    - メタデータ取得
    - 任意時刻でのスクリーンショット生成
    """

    def __init__(self, uploaded_file):
        if uploaded_file is None:
            raise ValueError("No file uploaded.")

        # 一時ファイルとして保存（moviepyはファイルパスを要求するため）
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(uploaded_file.read())
            self.tmp_path = tmp.name

        self.clip = VideoFileClip(self.tmp_path)
        self.filename = uploaded_file.name  # 元ファイル名を保持

    def get_metadata(self):
        """動画のメタ情報を返す"""
        return {
            "duration": self.clip.duration,
            "fps": self.clip.fps,
            "size": (self.clip.w, self.clip.h),
        }

    def get_screenshot_bytes(self, sec: float = 1.0) -> BytesIO:
        """指定秒数でスクリーンショットを取得しBytesIOで返す"""
        if sec < 0 or sec > self.clip.duration:
            raise ValueError("指定時間が動画の範囲外です。")

        frame = self.clip.get_frame(sec)
        image = Image.fromarray(frame)
        img_bytes = BytesIO()
        image.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        return img_bytes

    def seconds_to_timecode(self, seconds: float) -> str:
        """秒数を mm:ss 形式へ変換"""
        # h = int(seconds // 3600)
        # m = int((seconds % 3600) // 60)
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{m:02}:{s:02}"

    def get_screenshot_filename(self, sec: float) -> str:
        """指定秒数の時刻を使ったファイル名を返す"""
        timecode = self.seconds_to_timecode(sec)
        base, _ = os.path.splitext(self.filename)
        return f"{base}_{timecode}.png"

    def cleanup(self):
        """リソース解放"""
        if self.clip:
            self.clip.close()
        if self.tmp_path and os.path.exists(self.tmp_path):
            os.remove(self.tmp_path)
