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

    def __init__(self, video_bytes):
        # 一時ファイルとして保存（moviepyはファイルパスを要求するため）
        self.tmp_path = ""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(video_bytes)
            self.tmp_path = tmp.name
            # st.rerun()

        self.clip = VideoFileClip(self.tmp_path)

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

    def cleanup(self):
        """リソース解放"""
        if self.clip:
            self.clip.close()
        if self.tmp_path and os.path.exists(self.tmp_path):
            os.remove(self.tmp_path)

    def __enter__(self):
        """with構文で利用開始した際に呼ばれる"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """with構文を抜けた際に自動クリーンアップ"""
        self.cleanup()
        # 例外を握りつぶさず、通常の伝播に任せる
        return False