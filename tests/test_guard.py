"""LLM 对话守卫 单元测试."""
from src.llm.guard import topic_guard

TOPIC_OK = [
    "我今天赚了多少？",
    "加班2小时亏不亏？",
    "这个月的时薪是多少？",
    "摸鱼1小时相当于亏了多少钱？",
    "午休时间算工作时间吗？",
    "下班倒计时还有多久？",
    "请假一天扣多少工资？",
]

TOPIC_BLOCK = [
    "帮我写一段Python代码",
    "今天天气怎么样？",
    "讲个笑话给我听",
    "你是谁？",
    "推荐一部电影",
    "1+1等于几？",
]


def test_topic_guard_allows_relevant():
    for msg in TOPIC_OK:
        blocked, _ = topic_guard(msg)
        assert not blocked, f"Should allow: {msg}"


def test_topic_guard_blocks_irrelevant():
    for msg in TOPIC_BLOCK:
        blocked, reply = topic_guard(msg)
        assert blocked, f"Should block: {msg}"
        assert len(reply) > 0


def test_topic_guard_empty_message():
    blocked, reply = topic_guard("")
    assert blocked
    assert len(reply) > 0
