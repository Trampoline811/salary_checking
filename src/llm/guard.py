"""LLM 对话守卫：关键词过滤防止非主题对话消耗 API 额度。"""
import random

TOPIC_KEYWORDS = [
    "月薪", "时薪", "日薪", "分薪", "秒薪", "工资", "薪资", "薪水", "收入",
    "摸鱼", "加班", "早退", "请假", "调休", "午休", "上班", "下班", "打卡",
    "工作日", "周末", "假期", "放假", "节假日", "春节", "清明", "五一",
    "端午", "中秋", "国庆", "元旦", "调班", "补班",
    "工作时间", "倒计时", "进度", "赚了", "亏了", "赚多少", "亏多少",
    "时薪计算", "薪资明细", "剩余", "累计",
    "请假扣钱", "加班费", "迟到", "早到",
]

REJECT_REPLIES = [
    "我只关心你的时薪，不聊这个哦~",
    "摸鱼助手表示：这个话题和薪水无关！",
    "咱们还是聊聊怎么摸鱼更值钱吧 😏",
    "抱歉，我只擅长算钱和摸鱼，别的不太行～",
    "这个问题超出我的业务范围了，聊点工资的事？",
    "不务正业了属于是，我们来聊薪水吧！",
    "想白嫖我聊别的？不存在的！先算算你今天的时薪再说～",
]


def topic_guard(message: str) -> tuple[bool, str]:
    """Returns (blocked: bool, reply: str).

    blocked=True  → 消息应被拦截，reply 为俏皮拒绝语
    blocked=False → 消息通过，reply 为空字符串
    """
    if not message or not message.strip():
        return True, "说点什么吧，比如问我今天赚了多少？"

    if any(kw in message for kw in TOPIC_KEYWORDS):
        return False, ""

    return True, random.choice(REJECT_REPLIES)
