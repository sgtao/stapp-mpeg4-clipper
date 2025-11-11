# 12_clip_multi_screenshots.py
import io

# import os
import time
import zipfile

import pandas as pd
import streamlit as st

from components.MultiScreenshot import MultiScreenshot
from functions.AppLogger import AppLogger

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

    if "csv_loaded" not in st.session_state:
        st.session_state.csv_loaded = False
        st.session_state.csv_df = None

    if "app_logger" not in st.session_state:
        app_logger = AppLogger(APP_TITLE)
        app_logger.app_start()
        st.session_state.app_logger = app_logger
    elif st.session_state.app_logger.name != APP_TITLE:
        app_logger = AppLogger(APP_TITLE)
        app_logger.app_start()
        st.session_state.app_logger = app_logger


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


def timestamp_to_sec(timestamp):
    m, s = timestamp.split(":")
    return int(m) * 60 + int(s)


def generate_screen_cache_key(minute):
    return f"screens_{minute}"


def has_selected_image(timestamp):
    for item in st.session_state.screenshot_list:
        if item["timestamp"] == timestamp:
            return True
    return False


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
        f"📷 Screenshots on {selected_minute}m "
        + "(`Add`でチェック画像を取得）"
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
            # 既に選択済み（screenshot_listに存在する）か判定
            already_selected = has_selected_image(time_str)

            # 既存選択はチェック済み＋編集不可
            if already_selected:
                st.checkbox(
                    label=f"{time_str} ✅",
                    key=f"chk_{start_minute}_{timestamp}",
                    value=True,
                    disabled=True,
                    help="この画像はすでにリストに含まれています",
                )
            else:
                # 新規選択のみ操作可能
                checked = st.checkbox(
                    label=time_str,
                    key=f"chk_{start_minute}_{timestamp}",
                    value=False,
                )
                if checked:
                    selected_timestamps.append((time_str, img_bytes))

    st.write(f"✅ 選択枚数: {len(selected_timestamps)}")

    col_l, col_r = st.columns(2)
    with col_l:
        disable_add_images = len(selected_timestamps) == 0
        if st.button(
            label="Add ScreenShots",
            type="primary",
            disabled=disable_add_images,
        ):
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


def log_download_filename(filename):
    app_logger = st.session_state.app_logger
    app_logger.info_log(f"download as {filename}")


def extract_first_valid_value(row, candidate_cols, cast_func=str):
    """
    候補列の中から最初に有効な値を抽出する。

    Parameters
    ----------
    row : pandas.Series
        CSVの1行
    candidate_cols : list[str]
        候補となる列名のリスト
    cast_func : callable, optional
        値をキャストする関数（例: str, int, float）

    Returns
    -------
    any or ""
        最初に見つかった有効な値。なければ Blank(`""`)
    """
    if cast_func == "int" or "float":
        return next(
            (
                cast_func(row[col])
                for col in candidate_cols
                if col in row
                and pd.notna(row[col])
                and str(row[col]).strip() != ""
            ),
            "",
        )
    else:
        return next(
            (
                cast_func(str(row[col]).strip())
                for col in candidate_cols
                if col in row
                and pd.notna(row[col])
                and str(row[col]).strip() != ""
            ),
            "",
        )


def main():
    st.set_page_config(page_title=APP_TITLE)
    st.page_link("main.py", label="Back to Home", icon="🏠")
    st.subheader(f"📹 {APP_TITLE}")

    # ------------------------
    # ① 動画アップロード
    # ------------------------
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

    st.divider()
    # ------------------------
    # ②-1 minuteごとのボタン
    # ------------------------
    with st.spinner():
        minute_shots = multi_shot.extract_screenshots(
            start_minute=0,
            period_sec=9999,
            step=60,
        )
    if len(minute_shots) > 0:
        st.subheader(f"📷 Screenshots Each Minutes ({len(minute_shots)})")
        st.write(
            "Select images and `Add` from each minute button,"
            + " or upload CSV file with Timestamp at bellow."
        )

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

    # ------------------------
    # ②-2 CSVアップロード（スナップショット指定用）
    # ------------------------

    if (
        not st.session_state.csv_loaded
        and len(st.session_state.screenshot_list) == 0
    ):
        st.subheader("📄 Load Screenshot List from CSV")
        st.info(
            "✅ CSVファイルをアップロードして、一括でスナップショットを抽出できます"
        )
        csv_file = st.file_uploader(
            "📁 Upload CSV file (with Timestamp column)",
            type=["csv"],
            key="file_uploader_csv",
        )
        if csv_file is not None:
            df_csv = pd.read_csv(csv_file)
            st.session_state.csv_df = df_csv
            st.dataframe(df_csv, width="content")

            if st.button("🪄 Generate from CSV file", type="primary"):
                if "Timestamp" not in df_csv.columns:
                    st.error("CSVファイルに 'Timestamp' 列が見つかりません。")
                else:
                    st.session_state.screenshot_list = []
                    for i, row in df_csv.iterrows():
                        id_cols = ["ID", "Id", "NO", "No"]
                        ts_id = extract_first_valid_value(row, id_cols, int)
                        # ts_str = str(row["Timestamp"]).strip()
                        ts_cols = [
                            "Timestamp",
                            "TimeStamp",
                            "timestamp",
                            "timeStamp",
                        ]
                        ts_str = extract_first_valid_value(row, ts_cols)

                        if ts_id == "" or pd.isna(ts_str) or ts_str == "":
                            continue
                        # mm:ss → 秒数に変換
                        try:
                            sec = timestamp_to_sec(ts_str)
                            img_bytes, _, _ = (
                                multi_shot.clipper.get_screenshot_bytes(sec)
                            )
                            item = {
                                "id": ts_id,
                                "timestamp": ts_str,
                                "image": img_bytes,
                            }
                            st.session_state.screenshot_list.append(item)
                        except Exception as e:
                            st.warning(
                                f"タイムスタンプ {ts_str} の処理に失敗しました: {e}"
                            )
                    st.success(
                        "✅ CSV内容からスクリーンショットを生成しました！"
                    )
                    st.session_state.csv_loaded = True

    # ------------------------
    # ③ スクリーンショットリストの表示 + DL
    # ------------------------
    if len(st.session_state.screenshot_list) > 0:
        st.divider()
        st.subheader("📦 ダウンロード候補リスト")

        # 表示用に必要な列だけ抽出（id と timestamp）
        df = pd.DataFrame(st.session_state.screenshot_list)
        df_display = df[["id", "timestamp"]].rename(
            columns={"id": "ID", "timestamp": "Timestamp"}
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
                on_click=log_download_filename,
                args=[csv_filename],
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
                    on_click=log_download_filename,
                    args=[zip_filename],
                )


if __name__ == "__main__":
    initialize_session_state()
    main()
