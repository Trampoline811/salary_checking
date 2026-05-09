"""薪资计算引擎 — 纯函数，无 UI 依赖，返回 dataclass。"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta

from chinese_calendar import is_workday

from .workday import get_month_workdays


def _str2datetime(time_data: str, date_data: date) -> datetime:
    if len(time_data) == 8:
        t = datetime.strptime(time_data, "%H:%M:%S").time()
    elif len(time_data) == 5:
        t = datetime.strptime(time_data, "%H:%M").time()
    else:
        raise ValueError(f"Invalid time format: {time_data}")
    return datetime.combine(date_data, t)


@dataclass
class SalaryResult:
    """所有计算结果的容器。"""
    # 输入
    salary_month: float = 0.0
    total_workdays: float = 0.0
    worked_days: int = 0
    holiday_count: int = 0
    workday_type: str = "std"
    is_workday: bool = True
    effective_mode: bool = False

    # 名义薪资（按标准工时）
    nominal_daily: float = 0.0
    nominal_hourly: float = 0.0
    nominal_per_minute: float = 0.0
    nominal_per_second: float = 0.0

    # 有效时薪（加班/早退后）
    effective_hourly: float = 0.0

    # 今日时间
    standard_work_seconds: int = 0
    worked_seconds: int = 0
    remaining_seconds: int = 0
    progress_pct: float = 0.0

    # 累计收入
    today_earned: float = 0.0
    month_earned: float = 0.0

    # 时间格式化
    worked_str: str = ""
    remaining_str: str = ""


class SalaryCalculator:
    def __init__(
        self,
        salary_month: float,
        start_time: str,
        end_time: str,
        lunch_start: str,
        lunch_end: str,
        workday_type: str = "std",
        date_str: str | None = None,
        current_time: str | None = None,
        effective_mode: bool = False,
    ):
        self.salary_month = salary_month
        self.workday_type = workday_type
        self.effective_mode = effective_mode
        self.date_obj = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()
        now = datetime.now()
        self.current_dt = _str2datetime(current_time, self.date_obj) if current_time else datetime.combine(
            self.date_obj, now.time()
        )
        self.start_dt = _str2datetime(start_time, self.date_obj)
        self.end_dt = _str2datetime(end_time, self.date_obj)
        self.lunch_start_dt = _str2datetime(lunch_start, self.date_obj)
        self.lunch_end_dt = _str2datetime(lunch_end, self.date_obj)

    def compute(self) -> SalaryResult:
        r = SalaryResult()
        r.salary_month = self.salary_month
        r.workday_type = self.workday_type
        r.effective_mode = self.effective_mode

        # 工作日
        total, worked, holidays = get_month_workdays(self.date_obj, self.workday_type)
        r.total_workdays = total
        r.worked_days = worked
        r.holiday_count = holidays

        # 是否工作日
        r.is_workday = is_workday(self.current_dt)

        # 标准工时（秒）
        lunch_seconds = (self.lunch_end_dt - self.lunch_start_dt).seconds
        r.standard_work_seconds = (self.end_dt - self.start_dt).seconds - lunch_seconds

        # 已工作时间（秒）
        if self.current_dt < self.start_dt:
            worked = timedelta(0)
        elif self.current_dt < self.lunch_start_dt:
            worked = self.current_dt - self.start_dt
        elif self.current_dt < self.lunch_end_dt:
            worked = self.lunch_start_dt - self.start_dt
        elif self.current_dt < self.end_dt:
            worked = (self.lunch_start_dt - self.start_dt) + (self.current_dt - self.lunch_end_dt)
        else:
            # 下班后 — 按实际时间计算(含加班/晚走)
            worked = (self.lunch_start_dt - self.start_dt) + (self.current_dt - self.lunch_end_dt)
        r.worked_seconds = int(worked.total_seconds())
        r.remaining_seconds = max(0, r.standard_work_seconds - r.worked_seconds)
        r.progress_pct = (r.worked_seconds / r.standard_work_seconds * 100) if r.standard_work_seconds > 0 else 0

        # 日薪
        r.nominal_daily = self.salary_month / max(r.total_workdays, 1)

        # 名义时/分/秒薪（基于标准工时）
        standard_hours = r.standard_work_seconds / 3600
        r.nominal_hourly = r.nominal_daily / standard_hours if standard_hours > 0 else 0
        r.nominal_per_minute = r.nominal_hourly / 60
        r.nominal_per_second = r.nominal_hourly / 3600

        # 有效时薪
        if r.effective_mode and r.is_workday:
            actual_hours = r.worked_seconds / 3600 if r.worked_seconds > 0 else standard_hours
            r.effective_hourly = r.nominal_daily / actual_hours if actual_hours > 0 else 0
        else:
            r.effective_hourly = r.nominal_hourly

        # 累计收入
        r.today_earned = r.nominal_per_second * r.worked_seconds
        r.month_earned = r.nominal_daily * r.worked_days + r.today_earned

        # 格式化
        r.worked_str = _seconds_to_str(r.worked_seconds)
        r.remaining_str = _seconds_to_str(r.remaining_seconds)

        return r


def _seconds_to_str(total_seconds: int) -> str:
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    return f"{h}小时{m}分钟{s}秒"
