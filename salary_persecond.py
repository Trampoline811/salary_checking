import chinese_calendar as cc
from datetime import datetime, timedelta, date, time
import matplotlib as plt
import pandas as pd
import emoji


# 写个小函数将只有h:m的数据转为有 y-m-d-h-m的datatime类型数据
def str2datetime(time_data, date_data=datetime.now().date()):
    # 获取时间
    if len(time_data) == 8:
        time_data = datetime.strptime(time_data, "%H:%M:%S").time()
    elif len(time_data) == 5:
        time_data = datetime.strptime(time_data, "%H:%M").time()
    else:
        raise ValueError("输入了错误的时间格式 '{}'".format(time_data))
    # 时间 + 日期
    return datetime.combine(date_data, time_data)


class MoYu_salary_second:
    def __init__(self, salary_month, start_time, end_time, lunch_start, lunch_end,
                 date_str=None, current_time=None, **kwargs):
        self.salary_month = salary_month
        # 时间对象，给定则用给定的，没给定则用当前日期
        self.date_obj = (datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.now()).date()
        self.current_datetime = str2datetime(current_time, self.date_obj) if current_time else datetime.now()
        # 调用已经写好的函数，直接初始化为 datetime 类型数据
        self.start_time = str2datetime(start_time, self.date_obj)
        self.end_time = str2datetime(end_time, self.date_obj)
        self.lunch_start = str2datetime(lunch_start, self.date_obj)
        self.lunch_end = str2datetime(lunch_end, self.date_obj)
        # if date_str is None:
        #     self.date_obj = datetime.now().date()
        # else:
        #     # 将传入的str格式日期转换为 datetime格式日期
        #     self.date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        self.workday_type = kwargs.pop('workday_type', 'std')
        if self.workday_type not in ['std', 'flo']:
            raise ValueError("输入了错误的工作日计算类型 '{}'".format(self.workday_type))

    # 判断当天是不是工作日
    def is_workday(self):
        return cc.is_workday(self.current_datetime)

    # 计算当月工作日和已经工作过的工作日数
    @property
    def count_workdays(self):
        start_date = self.date_obj.replace(day=1)
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        _workday_list = cc.get_workdays(start_date, end_date)
        _workdays = len(_workday_list)
        _worked_days = sum([1 for i in _workday_list if self.date_obj > i])
        if self.workday_type == 'flo':
            return _workdays, _worked_days
        elif self.workday_type == 'std':
            _workdays = 21.75
            return _workdays, _worked_days

    # 计算已工作时间、每日的工作时长和下班倒计时，按秒计算
    def calculate_work_time(self):
        # 计算每个工作日的总工作时长
        total_work_time_perday = (self.end_time - self.start_time) - (self.lunch_end - self.lunch_start)
        if self.current_datetime < self.start_time:
            worked_time = self.current_datetime - self.current_datetime  # 避免整数0类型错
        elif self.start_time <= self.current_datetime < self.lunch_start:
            worked_time = self.current_datetime - self.start_time
        elif self.lunch_start <= self.current_datetime < self.lunch_end:
            worked_time = self.lunch_start - self.start_time
        elif self.lunch_end <= self.current_datetime < self.end_time:
            worked_time = self.lunch_start - self.start_time + self.current_datetime - self.lunch_end
        else:
            worked_time = total_work_time_perday
        time_remaining = total_work_time_perday - worked_time
        return worked_time, total_work_time_perday, time_remaining

    # 正向处理已工作时间，将时间差处理为文字
    def fd_timedelta2str(self):
        # 拿到上面的工作时间
        work_time_total_seconds = self.calculate_work_time()[0].seconds
        hours = work_time_total_seconds // 3600
        minutes = (work_time_total_seconds % 3600) // 60
        seconds = work_time_total_seconds % 60
        return f'{hours}小时{minutes}分钟{seconds}秒'

    # 反向处理距离下班时间，将时间差处理为文字
    def bd_timedelta2str(self):
        time_remaining = self.calculate_work_time()[2].seconds
        hours = time_remaining // 3600
        minutes = (time_remaining % 3600) // 60
        seconds = time_remaining % 60
        return f'{hours}小时{minutes}分钟{seconds}秒'

    # 计算秒薪
    def salary_second(self):
        # 拿到上面的工作日
        _workdays = self.count_workdays[0]
        # 拿到上面的每日工作时间
        total_work_time_perday = self.calculate_work_time()[1].seconds
        salary_day = self.salary_month / _workdays
        salary_second = salary_day / total_work_time_perday
        # 返回时薪，秒薪
        return salary_day, salary_second

    # 计算当日累计秒薪
    def salary_cumulative_second(self):
        # 拿到上面的秒薪
        salary_second = self.salary_second()[1]
        # 拿到上面的累计工作秒数
        work_time = self.calculate_work_time()[0].seconds
        salary_cumulative_second = salary_second * work_time
        return salary_cumulative_second

    # 计算本月累计薪水
    def salary_cumulative_month(self):
        # 拿到上面的当日累计秒薪
        salary_cumulative_second = self.salary_cumulative_second()
        # 拿到上面的日薪
        salary_day = self.salary_second()[0]
        # 拿到已经工作的日期
        _worked_days = self.count_workdays[1]
        return salary_day * _worked_days + salary_cumulative_second

    # 撰写输出
    def salary_print(self):
        # 设置字典转换
        dic_workday = {'std': '标准工作日', 'flo': '浮动工作日'}
        # 输出给定日期的工作日数量
        print(f'本次工作日计算方式为：{dic_workday[self.workday_type]}法，')
        print(f'{self.date_obj.year}年{self.date_obj.month}月'
              f'共有{self.count_workdays[0]}个工作日，')
        print(
            f'您已工作{self.count_workdays[1] + (self.calculate_work_time()[0] / self.calculate_work_time()[1]) :.2f}个工作日。')

        print('=' * 30)
        if self.is_workday():
            # 输出现在的时间和已工作时间
            print(f"现在是：{self.current_datetime.strftime('%Y-%m-%d %H:%M:%S %a')}",
                  f"今日已工作：{self.fd_timedelta2str()}(含摸鱼{emoji.emojize(':waving_hand::fish::thumbs_up:')}",
                  f"下班倒计时：{self.bd_timedelta2str()}", sep='\n')
            # 直接调用下面的输出函数，输出已工作时间和薪水
            self._test_print()
            # print('秒数', '分钟数', '小时数', '工作日数', sep='\t')
            # print(f'{self.calculate_work_time()[0].seconds:,}',
            #       f'{self.calculate_work_time()[0].seconds / 60 :.1f}',
            #       f'{self.calculate_work_time()[0].seconds / 3600 :.2f}',
            #       f'{self.calculate_work_time()[0] / self.calculate_work_time()[1]:^6.2f}',
            #       sep='\t')
            # print('=' * 30)  # 输出薪水（时分秒）
            # print('秒薪', '分薪', '时薪', '日薪', sep='\t')
            # print(f'￥{self.salary_second()[1]:^8.4f}',
            #       f'￥{self.salary_second()[1] * 60:^6.2f}',
            #       f'￥{self.salary_second()[1] * 3600:^6.2f}',
            #       f'￥{self.salary_second()[0]:^6.2f}',
            #       sep='\t')

            print('=' * 30)  # 输出累计薪水（本日，当月）
            print('本日累计薪水', '本月累计薪水', sep='\t')
            print(f'￥{self.salary_cumulative_second():.2f}',
                  f'￥{self.salary_cumulative_month():.2f}', sep='\t')

        else:
            print(f"现在是{self.current_datetime.strftime('%Y-%m-%d %H:%M:%S %a')}")
            print('今天是休息日，请好好享受休息吧~')

    @staticmethod
    def log():
        log_dic = {}
        log_dic['1'] = '2024/01/28 添加判断是否为工作日，工作日则计算日薪，非工作日则享受周末。'
        log_dic['2'] = '2024/01/28 添加功能：计算当月累计薪水'
        log_dic['3'] = '2024/01/28 优化给定日期字符串和时间的逻辑，' \
                       'date_str 和 current_time 均给定，则均使用给定值；' \
                       '只给定一个则给定的使用给定值，另外一个使用当前时间的对应日期/时间；' \
                       '都不给定则均使用当前时间的日期和时间'
        log_dic['4'] = '通过制表符，将输出方式修改为表格'
        log_dic['5'] = '2024/02/06 修改输出方式，增加测试输出函数，使用了pd和for循环两种输出方式，可根据需求进行调用'
        log_dic['6'] = '2024/04/03 在输出中增加emoji表情包，并增加下班倒计时。'
        # 先留着 后续再修改
        df = pd.DataFrame([log_dic])
        return log_dic

    def _test_print(self):
        # 测试输出方式一，用pd
        worked_time_salary = [[f'{self.calculate_work_time()[0].seconds:^6}',
                               f'{self.calculate_work_time()[0].seconds / 60 :^6.1f}',
                               f'{self.calculate_work_time()[0].seconds / 3600 :^6.2f}',
                               f'{self.calculate_work_time()[0] / self.calculate_work_time()[1]:^6.2f}'],
                              [f'{self.calculate_work_time()[2].seconds:^6}',
                               f'{self.calculate_work_time()[2].seconds / 60 :^6.1f}',
                               f'{self.calculate_work_time()[2].seconds / 3600 :^6.2f}',
                               f'{self.calculate_work_time()[2] / self.calculate_work_time()[1]:^6.2f}'],
                              [f'{self.salary_second()[1]:^8.4f}',
                               f'{self.salary_second()[1] * 60:^6.2f}',
                               f'{self.salary_second()[1] * 3600:^6.2f}',
                               f'{self.salary_second()[0]:^6.2f}']
                              ]
        df = pd.DataFrame(data=worked_time_salary,
                          index=['工作时间(累计)', '下班倒计时(累计)', '薪水(￥)/每时刻'], columns=['秒计', '分钟计', '小时计', '日计'])
        print(df)
        # 测试输出方式二，用循环遍历访问二维表
        worked_time_salary_list = [['指标', '秒计', '分钟计', '小时计', '日计'],
                                   ['工作时间(累计)', f'{self.calculate_work_time()[0].seconds:6}',
                                    f'{self.calculate_work_time()[0].seconds / 60 :6.1f}',
                                    f'{self.calculate_work_time()[0].seconds / 3600 :6.2f}',
                                    f'{self.calculate_work_time()[0] / self.calculate_work_time()[1]:6.2f}'],
                                   ['薪水(￥)', f'{self.salary_second()[1]:8.4f}',
                                    f'{self.salary_second()[1] * 60:6.2f}',
                                    f'{self.salary_second()[1] * 3600:6.2f}',
                                    f'{self.salary_second()[0]:6.2f}']
                                   ]
        for row in worked_time_salary_list:
            line = ''
            for item in row:
                line += '{:^8}\t'.format(item)
            # print(line)


if __name__ == '__main__':
    # 给定日期，可查看该日期所在月份的工作日数量
    # 可选，默认为当前操作时间所在日期
    # date_str = '2024-01-31'
    date_str = None
    # 给定月薪
    salary_month = 15500
    # 给定时间
    start_time = "09:00"  # 上班时间
    end_time = "18:00"  # 下班时间
    lunch_start = "12:00"  # 午休开始
    lunch_end = "13:00"  # 午休结束

    # 给定工作日计算方式，支持标准和浮动两种，默认为标准
    # 标准工作日(std)每月固定21.75天，浮动工作日(flo)计算每月实际工作日数量
    workday_type = 'std'  # 选填，'std'或'flo'即可

    # 测试变量
    # current_time = "17:55:58"  # 当前时间，可选，不给默认为当前操作时间
    current_time = None

    # 实例化
    cbl = MoYu_salary_second(
        salary_month, start_time, end_time, lunch_start, lunch_end,
        workday_type=workday_type)
    # 输出
    cbl.salary_print()

    # print(cbl.log())
    print('-' * 15, 'Done!', '-' * 15)

