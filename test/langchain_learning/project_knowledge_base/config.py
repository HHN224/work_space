# ============================================
# 配置中心 (Configuration Center)
#
# 架构原则：
# 1. 敏感信息（API Key）建议通过环境变量注入，避免硬编码泄露。
# 2. 所有模型参数集中管理，方便切换和 A/B 测试。
# 3. 注释中标注了预估 Token 成本（以 DeepSeek 官方定价为参考）。
# ============================================

import os

# --------------------------------------------
# DeepSeek API 配置
# --------------------------------------------
# 建议：将 DEEPSEEK_API_KEY 设为环境变量，例如：
#   Windows PowerShell: $env:DEEPSEEK_API_KEY="sk-..."
#   Linux/macOS: export DEEPSEEK_API_KEY="sk-..."
#
# 如果环境变量未设置，则使用下方默认值（仅本地开发）。
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-xxx")

# DeepSeek 兼容 OpenAI 格式
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"

# 模型选择：
# - deepseek-chat: 通用对话模型，速度快，价格低（输入 0.001元/1K tokens，输出 0.002元/1K tokens）
# - deepseek-reasoner: 深度推理模型，适合复杂逻辑，价格较高（输入 0.004元/1K tokens，输出 0.016元/1K tokens）
# 为了节省余额，本项目默认使用 deepseek-chat。
DEFAULT_MODEL = "deepseek-chat"

# 全局默认参数
default_llm_params = {
    "model": DEFAULT_MODEL,
    "api_key": DEEPSEEK_API_KEY,
    "base_url": DEEPSEEK_BASE_URL,
    "temperature": 0.3,        # 0.0~2.0，越低越保守/确定，越高越有创意。工程场景建议 0.1~0.5。
    "max_tokens": 1024,        # 控制单次输出长度，防止意外消耗过多余额。
    "timeout": 30,             # 请求超时秒数，防止挂死。
}

# --------------------------------------------
# 多模型配置表（为后续 Fallback/路由 做准备）
# --------------------------------------------
MODEL_REGISTRY = {
    "deepseek-chat": {
        "model": "deepseek-chat",
        "api_key": DEEPSEEK_API_KEY,
        "base_url": DEEPSEEK_BASE_URL,
        "temperature": 0.3,
        "max_tokens": 1024,
    },
    # 预留槽位：当你有余额或其他厂商 Key 时，直接在此添加即可。
    # "deepseek-reasoner": { ... },
    # "glm-4": { ... },
    # "gpt-3.5-turbo": { ... },
}
