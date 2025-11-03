# logs_viewer.py
from datetime import datetime
import os
import time

import streamlit as st

from functions.AppLogger import AppLogger

# APP_TITLE = "APIクライアントアプリ"
APP_TITLE = "Log Viewer"
DEFAULT_LOG_FILE = os.path.join("logs", "api_request.log")


def render_log_selector(app_logger):
    # ログファイルを選択
    log_files = app_logger.get_log_filelist()
    st.session_state.disable_rotate = False

    def _on_change_select():
        st.session_state.disable_rotate = (
            st.session_state.log_selector != DEFAULT_LOG_FILE
        )

    index_log_file = log_files.index(DEFAULT_LOG_FILE)
    return st.selectbox(
        label="Select log file",
        options=log_files,
        key="log_selector",
        index=index_log_file,
        on_change=_on_change_select,
    )


# ログファイル表示関数
def display_log(log_file_path):
    try:
        with open(log_file_path, "r") as f:
            log_contents = f.read()
        st.text(log_contents)
    except FileNotFoundError:
        st.error(f"Log file not found: {log_file_path}")
    except Exception as e:
        st.error(f"An error occurred: {e}")


def rotate_log_file(log_file_path, app_logger):
    """
    ログファイルをリネームする関数
    """
    new_log_file_path = None
    try:
        # 新しいファイル名を生成
        now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        new_log_file_path = f"{log_file_path.replace('.log', '')}_{now}.log"

        app_logger.info_log(f"rotate log file to {new_log_file_path}.")
        # ファイルをリネーム
        os.rename(log_file_path, new_log_file_path)

        st.success(f"Log file rotated to {new_log_file_path}")
        time.sleep(1)
        return new_log_file_path
    except FileNotFoundError:
        st.error(f"Log file not found: {log_file_path}")
    except Exception as e:
        st.error(f"An error occurred: {e}")


def render_viewer_controller(app_logger):
    log_file_path = app_logger.get_logfile_name()
    col1, col2 = st.columns(2)
    with col1:
        if st.button(
            label="Log Rotate",
            help="rotate api_request.log file",
            disabled=st.session_state.disable_rotate,
            icon="🔃",
        ):
            rotated_filename = rotate_log_file(log_file_path, app_logger)
            if rotate_log_file is not None:
                # app_logger.logger.removeHandler()
                # app_logger.setup_logger(APP_TITLE)
                app_logger = AppLogger(APP_TITLE)
                app_logger.info_log(
                    f"previous log renamed to {rotated_filename}."
                )
                st.rerun()
    with col2:
        if st.button("Rerun (`R`)", icon="🏃"):
            st.rerun()


# メイン関数
def main():
    app_logger = AppLogger(APP_TITLE)
    app_logger.app_start()

    st.page_link("main.py", label="Back to Home", icon="🏠")

    st.title("🗒️ Log Viewer")
    # ログファイルを選択
    selected_log_file = render_log_selector(app_logger)

    # display log
    with st.expander("display selected log"):
        display_log(selected_log_file)

    # ログファイルリネームボタン
    render_viewer_controller(app_logger)


if __name__ == "__main__":
    main()
