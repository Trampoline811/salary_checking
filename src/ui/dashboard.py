"""仪表盘：KPI 卡片、进度条、累计收入、明细表。"""
import streamlit as st
from src.core.calculator import SalaryCalculator
from src.ui.components import kpi_row, progress_bar, salary_table, effective_badge


def render_dashboard():
    """根据 session_state 中的配置计算并渲染整个仪表盘。"""
    calc = SalaryCalculator(
        salary_month=st.session_state["salary_month"],
        start_time=st.session_state["start_time"],
        end_time=st.session_state["end_time"],
        lunch_start=st.session_state["lunch_start"],
        lunch_end=st.session_state["lunch_end"],
        workday_type=st.session_state["workday_type"],
        effective_mode=st.session_state.get("effective_mode", False),
    )
    result = calc.compute()

    # 标题
    st.header(f"🐟 摸鱼助手")

    # 月信息
    type_label = "标准 (21.75天/月)" if result.workday_type == "std" else "浮动 (实际工作日)"
    st.caption(f"📅 {type_label} | 已工作 {result.worked_days:.1f} 天 | 法定假日 {result.holiday_count} 天")

    if not result.is_workday:
        st.info("🎉 今天是休息日，请好好享受吧~")
        return

    # KPI 卡片：优先 日薪 + 时薪
    cards = [
        ("📆 日薪", f"¥{result.nominal_daily:.2f}"),
        ("💰 时薪", f"¥{result.nominal_hourly:.4f}"),
    ]
    # 宽屏补充分薪和秒薪
    kpi_row(cards)

    # 分薪和秒薪（额外行，始终显示但较小）
    c1, c2 = st.columns(2)
    with c1:
        st.metric("⚡ 分薪", f"¥{result.nominal_per_minute:.4f}")
    with c2:
        st.metric("⏱️ 秒薪", f"¥{result.nominal_per_second:.6f}")

    # 有效时薪
    if result.effective_mode:
        color = effective_badge(result.effective_hourly, result.nominal_hourly)
        delta = result.effective_hourly - result.nominal_hourly
        st.metric(
            "🎯 有效时薪",
            f"¥{result.effective_hourly:.4f}",
            delta=f"{delta:+.4f}",
        )
        if color == "#e94560":
            st.caption("🔴 加班中，时薪被稀释了...")
        elif color == "#22c55e":
            st.caption("🟢 早退/请假，时薪反而涨了！")

    # 进度条
    st.divider()
    progress_bar(
        result.progress_pct,
        f"今日已工作 {result.worked_str} ｜ 下班倒计时 {result.remaining_str}",
    )

    # 累计收入
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.metric("📅 今日已赚", f"¥{result.today_earned:.2f}")
    with c2:
        st.metric("📆 本月累计", f"¥{result.month_earned:.2f}")

    # 明细表
    st.divider()
    st.subheader("📋 薪资明细（日→时→分→秒）")
    salary_table(result)

    return result
