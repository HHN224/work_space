# DHS 2025: 智能体 RAG 与自适应检索

本仓库包含使用 LangChain、LangGraph 和 OpenAI 模型构建的高级检索增强生成（RAG）工作流和智能体架构。笔记本演示了如何构建自适应、智能体的文档检索、评分和答案生成系统，并支持网络搜索和向量数据库集成。

## 特性
- **自适应 RAG 流水线**: 根据主题相关性动态将查询路由到向量库或网络搜索。
- **文档检索与评分**: 使用 LLM 评估文档相关性并过滤结果。
- **答案生成**: 基于检索到的文档生成答案，并进行幻觉检测和答案评分。
- **问题重写**: 改进用户查询以获得更好的检索性能。
- **基于图的工作流**: 利用 LangGraph 实现灵活、有状态的工作流编排。
- **网络搜索集成**: 通过 Tavily API 支持外部搜索。

## 文件夹结构
- `Agentic RAG.ipynb`, `5_Agentic_Rag.ipynb`: 演示智能体 RAG 流水线的主笔记本。
- 其他笔记本: 异步处理、人机协作、可观测性等方面的实验和演示。
- `requirements.txt`: 所需的 Python 包列表。

## 设置
1. 克隆仓库：
   ```
   git clone https://github.com/yourusername/DHS-2025.git
   cd DHS-2025
   ```
2. 安装依赖：
   ```
   pip install -r requirements.txt
   ```
3. 在 `.env` 文件中设置你的 API 密钥（OpenAI、Tavily 等）：
   ```
   OPENAI_API_KEY=your_openai_key
   TAVILY_API_KEY=your_tavily_key
   ```

## 使用方式
- 在 Jupyter 或 VS Code 中打开笔记本。
- 运行单元格以加载文档、构建向量库并执行智能体 RAG 工作流。
- 修改输入问题以测试不同的检索和生成场景。

## 使用的技术
- LangChain
- LangGraph
- OpenAI API
- FAISS
- Tavily Search
- Python, Jupyter

## 许可证
MIT 许可证

## 作者
Sanat（及贡献者）
