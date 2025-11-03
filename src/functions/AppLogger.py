# AppLogger.py
import logging
import os

LOG_DIR = "logs"
DEFAULT_LOG_FILE = os.path.join("logs", "api_request.log")


class AppLogger:
    def __init__(self, name, log_file=DEFAULT_LOG_FILE, level=logging.DEBUG):
        """
        ロガーを設定するクラス
        :param name: ロガー名
        :param log_file: ログファイルのパス
        :param level: ログレベル (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.name = name
        self.log_file = log_file
        self.log_level = level
        # ログ格納ディレクトリをクラス変数として保持
        self.log_dirname = LOG_DIR

        # ログディレクトリの作成
        if not os.path.exists(self.log_dirname):
            os.makedirs(self.log_dirname)

        self.logger = logging.getLogger(name)
        self.setup_logger()

    def setup_logger(self):
        # 既存のハンドラーを削除
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        self.logger.setLevel(self.log_level)

        # ファイルハンドラー
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(self.log_level)

        # フォーマッター
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)

        # ハンドラー追加
        self.logger.addHandler(file_handler)

    def app_start(self):
        self.logger.info(f"Start App: {self.name}")

    def api_start_log(self, url, method, headers=None, body=None):
        self.logger.info(f"Starting request: {method} {url}")
        if headers:
            self.logger.debug(f"Request headers: {headers}")
        if body:
            self.logger.debug(f"Request body: {body}")

    def api_success_log(self, response):
        # メソッド終了時のログ
        self.logger.info(f"Request completed with {response.status_code}")
        self.logger.debug(f"Response headers: {response.headers}")
        self.logger.debug(f"Response body: {response.text}")

    def error_log(self, message):
        # メソッド終了時のログ
        self.logger.error(message)

    def info_log(self, message):
        # 任意タイミングのログ
        self.logger.info(message)

    def debug_log(self, message):
        # 任意タイミングのログ
        self.logger.debug(message)

    def get_logfile_name(self):
        return self.log_file

    def get_log_dir(self):
        return self.log_dirname

    def get_log_filelist(self):
        # return self.log_dirname
        log_files = []
        for f in os.listdir(self.log_dirname):
            if os.path.isfile(
                os.path.join(self.log_dirname, f)
            ) and f.endswith(".log"):
                log_files.append(os.path.join(self.log_dirname, f))
        return log_files
