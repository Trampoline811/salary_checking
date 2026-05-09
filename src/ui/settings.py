"""配置面板：顶部展开式，点击按钮切换显示。"""
import streamlit as st


def render_settings():
    """渲染可展开的配置面板，直接读写 st.session_state。"""
    if "show_settings" not in st.session_state:
        st.session_state["show_settings"] = False

    col1, col2 = st.columns([6, 1])
    with col2:
        label = "⚙ 收起" if st.session_state["show_settings"] else "⚙ 配置"
        if st.button(label, key="toggle_settings"):
            st.session_state["show_settings"] = not st.session_state["show_settings"]
            st.rerun()

    if not st.session_state["show_settings"]:
        return

    with st.container(border=True):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.session_state["salary_month"] = st.number_input(
                "月薪 ¥", min_value=0.0, value=st.session_state["salary_month"], step=500.0
            )
        with c2:
            st.session_state["start_time"] = st.text_input("上班", value=st.session_state["start_time"])
            st.session_state["end_time"] = st.text_input("下班", value=st.session_state["end_time"])
        with c3:
            st.session_state["lunch_start"] = st.text_input("午休开始", value=st.session_state["lunch_start"])
            st.session_state["lunch_end"] = st.text_input("午休结束", value=st.session_state["lunch_end"])
        with c4:
            st.session_state["workday_type"] = st.selectbox(
                "工作日算法",
                options=["std", "flo"],
                format_func=lambda x: "标准 (21.75天)" if x == "std" else "浮动 (实际工作日)",
                index=0 if st.session_state["workday_type"] == "std" else 1,
            )
            st.session_state["effective_mode"] = st.toggle(
                "有效时薪", value=st.session_state["effective_mode"],
                help="加班稀释时薪（红），早退提升时薪（绿）"
            )

        with st.expander("🔒 隐私说明"):
            st.markdown("""
**你的薪资数据从未离开你的控制。**

| 数据去向 | 说明 |
|----------|------|
| **浏览器** | 只接收渲染好的 HTML 页面，薪资数字不存 localStorage / Cookie |
| **服务端** | 仅当前会话内存中 (`st.session_state`)，关闭页面即销毁，不上传任何服务器 |
| **AI 对话** | 系统提示词（含薪资数据）发送到书生浦语 API 辅助回答，但不会被 API 方持久化存储 |
| **数据库** | 本项目**没有任何持久化逻辑**，不存在数据库 |

总结：关闭网页后，一切清零。你的薪资数据只有你自己看得到。
""")
