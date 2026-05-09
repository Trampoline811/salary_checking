"""可复用 Streamlit 组件：KPI 卡片、进度条。"""
import streamlit as st


def kpi_card(label: str, value: str, delta: str | None = None, color: str = "#e94560"):
    """单个 KPI 指标卡片，用 st.metric 实现。"""
    st.metric(label=label, value=value, delta=delta)


def kpi_row(cards: list[tuple[str, str, str | None]]):
    """一行 KPI 卡片，自动按列数分配。

    cards: [(label, value, delta_or_None), ...]
    """
    cols = st.columns(len(cards))
    for col, (label, value, delta) in zip(cols, cards):
        with col:
            kpi_card(label, value, delta)


def progress_bar(pct: float, text: str):
    """带文字的进度条。"""
    st.caption(text)
    st.progress(min(pct / 100, 1.0))


def salary_table(result):
    """薪资明细表：日→时→分→秒（大→小）。"""
    import pandas as pd

    data = {
        "单位": ["日", "小时", "分钟", "秒"],
        "名义薪资 ¥": [
            f"{result.nominal_daily:.2f}",
            f"{result.nominal_hourly:.4f}",
            f"{result.nominal_per_minute:.4f}",
            f"{result.nominal_per_second:.6f}",
        ],
    }
    df = pd.DataFrame(data)
    st.dataframe(df, hide_index=True, use_container_width=True)


def effective_badge(effective: float, nominal: float) -> str:
    """有效时薪 vs 名义时薪 的颜色标签。

    Returns HTML color: red=稀释, green=提升, gray=持平。
    """
    if abs(effective - nominal) < 0.001:
        return "gray"
    return "#22c55e" if effective > nominal else "#e94560"
