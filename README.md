# 🐟 摸鱼助手 v2.0

> 时薪计算与 AI 摸鱼伴侣 — 基于 Streamlit 的 Web 应用

## 功能

- **薪资实时计算** — 日薪、时薪、分薪、秒薪即时展示
- **有效时薪** — 加班稀释 / 早退提升 的直观量化
- **工作日智能判断** — 标准算法 (21.75天) 或浮动算法 (中国法定工作日)
- **AI 摸鱼助手** — 基于书生浦语大模型的薪资对话，支持多轮对话
- **零安装使用** — 浏览器打开即用，移动端友好

## 快速开始

```bash
# 安装依赖
uv sync

# 配置 API (可选，不配置则使用 Mock 模式)
cp .env.example .env
# 编辑 .env 填入 API Key

# 启动
uv run streamlit run src/app.py
```

浏览器打开 `http://localhost:8501`

## 部署

可直接部署到 [Streamlit Community Cloud](https://streamlit.io/cloud)（免费）：
1. Fork 本仓库
2. 在 Streamlit Cloud 连接 GitHub
3. 入口文件设为 `src/app.py`

## 技术栈

- **框架**: Streamlit
- **计算**: chinese_calendar + pandas
- **LLM**: 书生浦语 (intern-latest) via OpenAI SDK
- **管理**: uv

## License

MIT
