from datetime import date, datetime
from src.core.calculator import SalaryCalculator, SalaryResult
import pytest


def test_salary_result_defaults():
    r = SalaryResult()
    assert r.nominal_hourly == 0.0
    assert r.nominal_daily == 0.0
    assert r.effective_hourly == 0.0


def test_calculator_basic():
    calc = SalaryCalculator(
        salary_month=15500,
        start_time="09:00",
        end_time="18:00",
        lunch_start="12:00",
        lunch_end="13:00",
        workday_type="std",
        date_str="2026-05-08",
        current_time="14:30:00",
        effective_mode=False,
    )
    result = calc.compute()
    assert result.nominal_daily == pytest.approx(15500 / 21.75, rel=0.01)
    assert result.nominal_hourly == pytest.approx(result.nominal_daily / 8, rel=0.01)
    assert result.nominal_per_minute == pytest.approx(result.nominal_hourly / 60, rel=0.01)
    assert result.nominal_per_second == pytest.approx(result.nominal_hourly / 3600, rel=0.01)
    assert result.worked_seconds > 0
    assert result.remaining_seconds > 0
    assert result.progress_pct > 0
    assert result.today_earned > 0
    assert result.month_earned > 0


def test_calculator_effective_overtime():
    calc = SalaryCalculator(
        salary_month=480 * 21.75,  # ~10440, gives daily ~480
        start_time="09:00",
        end_time="18:00",
        lunch_start="12:00",
        lunch_end="13:00",
        workday_type="std",
        date_str="2026-05-08",
        current_time="20:00:00",  # 加班 2h
        effective_mode=True,
    )
    result = calc.compute()
    # 标准 8h, 加班 2h → 实际工时 10h, 有效时薪降低
    assert result.effective_hourly < result.nominal_hourly
    assert result.effective_hourly == pytest.approx(result.nominal_daily / 10, rel=0.01)


def test_calculator_effective_early_leave():
    calc = SalaryCalculator(
        salary_month=480 * 21.75,
        start_time="09:00",
        end_time="18:00",
        lunch_start="12:00",
        lunch_end="13:00",
        workday_type="std",
        date_str="2026-05-08",
        current_time="15:00:00",  # 早退 3h
        effective_mode=True,
    )
    result = calc.compute()
    # 实际工时 5h, 有效时薪升高
    assert result.effective_hourly > result.nominal_hourly
    assert result.effective_hourly == pytest.approx(result.nominal_daily / 5, rel=0.01)


def test_calculator_before_work():
    calc = SalaryCalculator(
        salary_month=15500, start_time="09:00", end_time="18:00",
        lunch_start="12:00", lunch_end="13:00",
        current_time="07:00:00",
    )
    result = calc.compute()
    assert result.worked_seconds == 0
    assert result.today_earned == 0


def test_calculator_during_lunch():
    calc = SalaryCalculator(
        salary_month=15500, start_time="09:00", end_time="18:00",
        lunch_start="12:00", lunch_end="13:00",
        current_time="12:30:00",
    )
    result = calc.compute()
    # During lunch, worked time should be capped at lunch_start - start_time
    assert result.worked_seconds == 3 * 3600  # 09:00-12:00


def test_calculator_flo_workday():
    calc = SalaryCalculator(
        salary_month=15500, start_time="09:00", end_time="18:00",
        lunch_start="12:00", lunch_end="13:00",
        workday_type="flo", date_str="2026-05-08",
        current_time="14:30:00",
    )
    result = calc.compute()
    assert result.total_workdays != 21.75
