import streamlit as st

# ページ設定
st.set_page_config(
    page_title="stapp-mpeg4-clipper", page_icon="🎬", layout="centered"
)


def main():
    # ---- ヘッダー ----
    st.title("🎬 stapp-mpeg4-clipper")
    st.markdown(
        """
    **MP4動画からスクリーンショットを抽出するツール集。**
    AI動画生成・素材編集・研究用データ整理など、幅広く活用できます。
    """
    )
    st.divider()

    # ---- カードレイアウト ----
    st.markdown("### 🧩 機能メニュー")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        with st.container(border=True):
            st.markdown("#### 📸 Clip Single Screenshot")
            st.write("任意の時刻から1枚画像を抽出。動画のサムネ作成に最適。")
            st.page_link(
                "pages/11_clip_single_screen.py",
                label="Go to App!",
                icon="➡️",
            )

        with st.container(border=True):
            st.markdown("#### ✂️ Clip Partial Video Downloader")
            st.write(
                "開始・終了時間の指定から部分切り出し。短尺素材作成に便利。"
            )
            st.page_link(
                "pages/13_clip_partial_video.py",
                label="Go to App!",
                icon="➡️",
            )

    with col2:
        with st.container(border=True):
            st.markdown("#### 📹 Multi Screenshot Selector")
            st.write("複数キャプチャを生成。クリックやSV指定で抽出可能。")
            st.page_link(
                "pages/12_clip_multi_screenshots.py",
                label="Go to App!",
                icon="➡️",
            )

        with st.container(border=True):
            st.markdown("#### 📄 Log Viewer")
            st.write(
                "ダウンロード履歴をブラウザで確認。トレースや動作検証に。"
            )
            st.page_link(
                "pages/21_logs_viewer.py",
                label="Go to App!",
                icon="➡️",
            )

    st.divider()

    # ---- フッター ----
    st.markdown(
        """
    💡 **開発者向け:**
    このアプリは [moviepy](https://zulko.github.io/moviepy/) と
      [Streamlit](https://streamlit.io/) により構築されています。
    各処理をモジュール化しており、業務利用にも対応可能です。
    """
    )


if __name__ == "__main__":
    main()
