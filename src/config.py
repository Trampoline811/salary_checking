"""配置管理：URL 参数 > session_state > 默认值。"""
import os
import streamlit as st

DEFAULTS = {
    "salary_month": 15500.0,
    "start_time": "09:00",
    "end_time": "18:00",
    "lunch_start": "12:00",
    "lunch_end": "13:00",
    "workday_type": "std",
    "effective_mode": False,
    "llm_provider": "shanghai",
    "llm_api_key": "",
    "llm_base_url": "https://api.shlab.org.cn/v1",
}


def init_session_state():
    """确保 session_state 中所有配置键都存在。"""
    for key, default_val in DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = default_val

    # URL 参数覆盖
    params = st.query_params
    if "salary" in params:
        try:
            st.session_state["salary_month"] = float(params["salary"])
        except ValueError:
            pass
    if "type" in params and params["type"] in ("std", "flo"):
        st.session_state["workday_type"] = params["type"]


def get_llm_config() -> dict:
    """返回 LLM 客户端配置，优先级：env > session_state。"""
    return {
        "provider": os.getenv("LLM_PROVIDER", st.session_state.get("llm_provider", "shanghai")),
        "api_key": os.getenv("LLM_API_KEY", st.session_state.get("llm_api_key", "")),
        "base_url": os.getenv("LLM_BASE_URL", st.session_state.get("llm_base_url", "")),
    }
