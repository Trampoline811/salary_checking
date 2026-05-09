from datetime import date, timedelta
import chinese_calendar as cc

STD_WORKDAYS_PER_MONTH = 21.75


def get_month_workdays(d: date, workday_type: str = "std") -> tuple[int, int, int]:
    """Return (total_workdays, worked_days_so_far, holiday_count) for the month containing `d`.

    - std: total_workdays = 21.75 (fixed)
    - flo: total_workdays = actual Chinese workdays in the month
    """
    start_date = d.replace(day=1)
    next_month = d.replace(day=28) + timedelta(days=4)
    end_date = next_month.replace(day=1) - timedelta(days=1)

    actual_workdays = cc.get_workdays(start_date, end_date)
    holiday_count = sum(1 for day in actual_workdays if cc.is_holiday(day))

    if workday_type == "std":
        total = STD_WORKDAYS_PER_MONTH
    elif workday_type == "flo":
        total = len(actual_workdays)
    else:
        raise ValueError(f"Unknown workday_type: {workday_type}")

    worked = sum(1 for wd in actual_workdays if d > wd)
    return total, worked, holiday_count
