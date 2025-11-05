import streamlit as st

"""
# Welcome to Streamlit!

Edit `/src` and `/tests` to customize this app to your heart's desire :heart:.
"""

# サイドバーのページに移動
# st.page_link("pages/example_app.py", label="Go to Example App")
# st.page_link("pages/01_example_app.py", label="Go to Example App", icon="🚀")
st.page_link(
    "pages/11_clip_single_screen.py",
    label="Go to Clip Single Screenshot App",
    icon="📸",
)
st.page_link(
    "pages/12_clip_multi_screenshots.py",
    label="Go to Multi Screenshot Selector App",
    icon="📹",
)
st.page_link(
    "pages/13_clip_partial_video.py",
    label="Go to Clip Partial Video Downloader App",
    icon="✂️",
)
# ログ表示ページへのリンク
st.page_link("pages/21_logs_viewer.py", label="View Logs", icon="📄")
