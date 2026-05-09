"""摸鱼助手 v2.0 — Streamlit 主入口。"""
import streamlit as st
from src.config import init_session_state, get_llm_config
from src.core.calculator import SalaryCalculator
from src.ui.settings import render_settings
from src.ui.dashboard import render_dashboard
from src.llm.client import get_client
from src.llm.guard import topic_guard
from src.llm.prompts import build_system_prompt, QUICK_QUESTIONS

st.set_page_config(
    page_title="摸鱼助手",
    page_icon="🐟",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_session_state()

# ── 配置面板 ──
render_settings()

# ── 仪表盘 ──
result = render_dashboard()

# ── AI 摸鱼助手 ──
st.divider()
st.subheader("🤖 AI 摸鱼助手")

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# 快捷提问
cols = st.columns(len(QUICK_QUESTIONS))
clicked = None
for col, q in zip(cols, QUICK_QUESTIONS):
    with col:
        if st.button(q, key=f"quick_{q}"):
            clicked = q

# 对话历史渲染（每条一个聊天气泡）
for msg in st.session_state["chat_history"]:
    role = "🧑" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 输入区
user_input = st.chat_input("问点摸鱼相关的事...")

if clicked:
    user_input = clicked

if user_input:
    # Guard 拦截
    blocked, reject_reply = topic_guard(user_input)
    if blocked:
        st.session_state["chat_history"].append({"role": "user", "content": user_input})
        st.session_state["chat_history"].append({"role": "assistant", "content": reject_reply})
        st.rerun()

    # 构建消息
    st.session_state["chat_history"].append({"role": "user", "content": user_input})

    type_label = "标准 (21.75天)" if st.session_state["workday_type"] == "std" else "浮动 (实际工作日)"
    sys_prompt = build_system_prompt(
        result, st.session_state["salary_month"],
        st.session_state["start_time"], st.session_state["end_time"],
        st.session_state["lunch_start"], st.session_state["lunch_end"],
        type_label, st.session_state.get("effective_mode", False),
        getattr(result, "holiday_count", 0),
    )

    messages = [
        {"role": "system", "content": sys_prompt},
    ] + [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state["chat_history"]
    ]

    llm_cfg = get_llm_config()
    client = get_client(llm_cfg["provider"], llm_cfg["api_key"], llm_cfg["base_url"])
    reply = client.chat(messages)
    st.session_state["chat_history"].append({"role": "assistant", "content": reply})
    st.rerun()
