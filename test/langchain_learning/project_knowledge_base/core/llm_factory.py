# ============================================
# LLM 工厂 (LLM Factory)
#
# 架构原则：
# 1. 工厂模式封装初始化逻辑，上层业务无需关心具体模型细节。
# 2. 所有 LLM 实例都符合 Runnable 接口（.invoke / .stream / .batch）。
# 3. 后续可在此扩展：Fallback、负载均衡、Token 限流、日志拦截。
# ============================================

from langchain_openai import ChatOpenAI
from ..config import MODEL_REGISTRY, default_llm_params


def create_llm(model_name: str = None, **overrides) -> ChatOpenAI:
    """
    根据模型名称创建 ChatOpenAI 实例。

    Args:
        model_name: 注册在 MODEL_REGISTRY 中的名称，None 则使用默认配置。
        **overrides: 覆盖默认参数，例如 temperature=0.0, max_tokens=512

    Returns:
        ChatOpenAI 实例（实现了 Runnable 接口）
    """
    if model_name and model_name in MODEL_REGISTRY:
        params = MODEL_REGISTRY[model_name].copy()
    else:
        params = default_llm_params.copy()

    # 允许调用时动态覆盖参数（如针对某个 Chain 调低 temperature）
    params.update(overrides)

    # 移除工厂自定义的字段，仅保留 ChatOpenAI 构造函数认可的参数
    params.pop("model_name", None)

    return ChatOpenAI(**params)


# 常用便捷入口
def default_llm(**overrides) -> ChatOpenAI:
    """使用默认模型（deepseek-chat）创建 LLM。"""
    return create_llm(model_name=None, **overrides)
