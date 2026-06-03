# ============================================
# Chain 组件库 (Reusable Chains)
#
# 架构原则：
# 1. 每个 Chain 都是纯函数式的 Runnable，输入输出类型明确。
# 2. 用 LCEL（| 运算符）组合，而非旧版的 LLMChain 类。
# 3. 将 Prompt、LLM、Parser 分离，方便单独替换和单元测试。
# ============================================

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSerializable

from .llm_factory import default_llm


def build_qa_chain(temperature: float = 0.3, max_tokens: int = 1024) -> RunnableSerializable:
    """
    构建一个最基础的问答链。

    输入: {"question": "什么是 LangChain?"}
    输出: str（纯文本回答）

    架构说明：
    - ChatPromptTemplate: 负责拼接 System + Human 消息，填充变量。
    - ChatOpenAI: 负责调用模型生成回复。
    - StrOutputParser: 负责从 AIMessage 中提取 .content 字符串。
    - "|": LCEL 管道运算符，将左侧输出作为右侧输入。
    """
    # 1. Prompt 模板：System 角色设定行为，Human 角色传递问题
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个简洁的技术专家，用一句话回答用户问题。"),
        ("human", "{question}")
    ])

    # 2. LLM：从工厂获取默认实例，允许局部覆盖参数
    llm = default_llm(temperature=temperature, max_tokens=max_tokens)

    # 3. 输出解析器
    parser = StrOutputParser()

    # 4. 用 LCEL 组装成链
    # 数据流：dict{"question"} → prompt → ChatMessage[] → llm → AIMessage → parser → str
    chain = prompt | llm | parser

    return chain


def build_explain_chain(topic_prompt: str = "用通俗语言解释技术概念") -> RunnableSerializable:
    """
    构建一个科普解释链，适合生成教程或博客内容。

    输入: {"topic": "区块链"}
    输出: str
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", topic_prompt),
        ("human", "请解释：{topic}")
    ])

    llm = default_llm(temperature=0.7, max_tokens=2048)  # 科普允许更有创意、更长
    parser = StrOutputParser()

    return prompt | llm | parser
