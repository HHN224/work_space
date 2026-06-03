# 🗺️ 大一 AI Agent / Python 后端实习半年作战地图

> **目标**：2027 年初投出第一份实习简历  
> **当前**：2026 年 6 月底（期末）  
> **主节奏**：项目驱动 + 算法保底  
> **每日投入**：暑假 8–10h；开学后 4–5h  

---

## 📊 整体时间线

| 阶段 | 时间 | 核心目标 | 每日投入 |
|------|------|----------|----------|
| **① 基础补牢期** | 暑假 7 月 (4 周) | Python 底层 + 数据结构 + 算法 + 网络 | 8–10h |
| **② 后端实战期** | 暑假 8 月 (4 周) | MySQL / Redis + Flask 项目骨架 + Docker | 8–10h |
| **③ AI Agent 进阶期** | 9–10 月 (8 周) | LangGraph + 多 Agent + MCP + RAG 优化 | 4–5h |
| **④ 项目整合期** | 11–12 月 (8 周) | 完整项目打磨 + 简历 + 八股 + 投递 | 4–5h |

---

## 🏗️ 核心项目：SmartKB（智能企业知识库平台）

这是贯穿半年的**主线项目**，也是你简历上最大的筹码。每个阶段都为它添砖加瓦。

### 技术栈设计

```
前端: React (复用你现有的 ia_chatbot_react_flask 经验)
后端: Flask + SQLAlchemy + MySQL + Redis
AI层: LangChain + LangGraph + DeepSeek API
向量库: Chroma → 后期可升级到 Qdrant
任务队列: Celery + Redis Broker
部署: Docker + Docker Compose
```

### 功能模块拆解

| 阶段 | 模块 | 面试考察点 |
|------|------|------------|
| 8 月 | 用户系统（JWT / 注册 / 登录） | Web 安全、Session 管理 |
| 8 月 | 文档上传 / 解析 / 分块 | 异步处理、文件 IO |
| 9 月 | RAG 检索问答 | 向量检索、Prompt 工程 |
| 9 月 | 多轮对话（LangGraph 重构） | StateGraph、循环、记忆 |
| 10 月 | 多 Agent 协作 | ReAct、任务规划、工具调用 |
| 10 月 | MCP 工具集成 | 协议理解、生态对接 |
| 11 月 | 管理后台（用量 / 日志） | 数据库设计、聚合查询 |
| 11 月 | Docker 一键部署 | DevOps、工程化 |

---

## 📅 逐周详细计划

### 阶段①：基础补牢期（7 月，暑假）

> **目标**：打牢地基，防止面试被基础八股问崩。算法达到“能写出 Hot 100 前 60 题”水平。

#### 第 1 周：Python 底层 + 算法数组 / 链表

- **Python**（每天 2h）：GIL、装饰器底层实现、`__call__`、生成器、`asyncio` 事件循环、`==` vs `is`、深浅拷贝
- **算法**（每天 2h）：LeetCode 数组（1, 15, 53）、链表（21, 141, 206）——每天 2 题，手写 + 理解
- **产出**：整理“Python 八股 10 题”文档

#### 第 2 周：数据结构 + 算法栈 / 队列 / 哈希 / 树

- **数据结构**（每天 1.5h）：栈、队列、哈希表、二叉树遍历（你线代学完了，理解矩阵 / 向量计算会很容易）
- **算法**（每天 2h）：LeetCode 栈（20, 155）、二叉树（104, 226）、BFS / DFS（200, 994）
- **产出**：用 Python 手写一个简易 LRU Cache（面试极高频）

#### 第 3 周：计算机网络 + 算法动态规划入门

- **网络**（每天 2h）：TCP 三次握手 / 四次挥手、HTTP / 1.1 vs 2.0 vs 3.0、HTTPS 握手、WebSocket、状态码、Cookie / Session / JWT
- **算法**（每天 2h）：DP 入门（70, 198, 322, 1143）
- **产出**：用 Flask 手写一个 WebSocket Echo 服务器

#### 第 4 周：MySQL 基础 + 数据库设计

- **MySQL**（每天 3h）：SQL 语法、索引类型（B+ 树）、最左前缀原则、事务 ACID、隔离级别、MVCC、慢查询优化
- **项目**（每天 2h）：设计 SmartKB 的数据库 Schema（用户表、文档表、对话记录表、知识库表）
- **产出**：画出 SmartKB 的 ER 图 + 建表 SQL

---

### 阶段②：后端实战期（8 月，暑假）

> **目标**：SmartKB 后端骨架搭起来，能跑通用户系统 + 文档上传。Docker 容器化。

#### 第 5 周：Flask + SQLAlchemy + MySQL 实战

- 搭建 Flask 项目结构（工厂模式、Blueprint、配置分离）
- 实现用户注册 / 登录 / JWT 鉴权
- 实现文档上传接口（PDF / TXT / Word）
- **产出**：Postman 测试通过的用户 + 文档 API

#### 第 6 周：Redis + Celery 异步任务

- **Redis**：5 大数据结构、缓存策略、会话存储、限流（Rate Limiting）
- **Celery**：Redis 做 Broker，实现“文档解析异步任务”
  - 上传文件 → 返回任务 ID → 前端轮询进度 → 解析完成入库
- **产出**：大文件上传不再阻塞 API

#### 第 7 周：Docker + Docker Compose

- Dockerfile 编写（多阶段构建）
- docker-compose 编排：Flask + MySQL + Redis + Nginx
- **产出**：`docker-compose up` 一键启动整个项目

#### 第 8 周：后端收尾 + 接口文档

- 统一异常处理、日志记录（loguru）
- 单元测试（pytest）
- 接口文档（Swagger / Flasgger 或手写 Markdown）
- **产出**：一个可独立运行的后端服务

---

### 阶段③：AI Agent 进阶期（9–10 月，开学后）

> **目标**：用 LangGraph 重构 AI 逻辑，实现多 Agent。RAG 深度优化。

#### 第 9 周：LangGraph 入门

- 理解 StateGraph、节点（Node）、边（Edge）、条件边
- 重写“路由决策”：从 `if/else` 规则升级为 LangGraph 图结构
- **产出**：用 LangGraph 实现“问题分类 → 检索 / 闲聊 / 工具”的简单图

#### 第 10 周：多轮对话 + 记忆管理（LangGraph 版）

- 用 LangGraph 的 `MemorySaver` 或 Redis 实现持久化记忆
- 流式输出集成到 Graph 中
- **产出**：SmartKB 对话模块 LangGraph 重构完成

#### 第 11 周：多 Agent 系统

- ReAct 模式（推理 → 行动 → 观察 → 再推理）
- Plan-and-Execute（规划 Agent + 执行 Agent + 评审 Agent）
- **产出**：实现“复杂问题分解 → 多步骤检索 → 综合回答”的 Multi-Agent 流程

#### 第 12 周：MCP 协议

- 理解 MCP（Model Context Protocol）架构
- 实现一个自定义 MCP Server（比如连接你的文档数据库）
- **产出**：SmartKB 支持 MCP 工具调用

#### 第 13 周：RAG 优化 ① —— 混合检索

- 向量检索（Chroma）+ BM25 关键词检索
- RRF（Reciprocal Rank Fusion）融合排序
- **产出**：检索准确率显著提升（可用几个测试问题对比）

#### 第 14 周：RAG 优化 ② —— 重排序与文档解析

- 重排序模型（Cross-Encoder 或简单 BGE Reranker）
- 升级文档解析：PyPDF2 / pdfplumber / python-docx，智能分块策略
- **产出**：支持 PDF / Word / Excel 上传

#### 第 15 周：Memory 优化

- 摘要记忆（ConversationSummaryMemory）
- 向量记忆（将历史对话也 Embedding 存储）
- **产出**：长对话不再 OOM 或超出上下文限制

#### 第 16 周：WebSocket + 流式输出

- 前端 WebSocket 实时接收流式 Token
- 后端 LangGraph 流式集成
- **产出**：打字机效果的知识库问答

---

### 阶段④：项目整合期（11–12 月）

> **目标**：项目打磨到“能写进简历”的程度，整理八股，开始投递。

#### 第 17 周：前后端联调

- React 前端接入所有后端 API
- 文件上传进度条、对话界面、知识库管理页面
- **产出**：可交互的完整 Web 应用

#### 第 18–19 周：性能优化 + 压测

- 数据库查询优化（Explain 分析、加索引）
- Redis 缓存热点数据
- 并发测试（Locust 或 JMeter）
- **产出**：能支撑 10 并发用户的 Demo

#### 第 20 周：部署文档 + 演示视频

- 写 README（项目介绍、架构图、部署步骤）
- 录制 3 分钟项目演示视频（放 GitHub 或 B站）
- **产出**：GitHub 仓库“能见人”

#### 第 21 周：简历撰写

- 项目描述要**量化**：“基于 RAG 的问答系统，支持 PDF / Word / Excel 解析，检索准确率提升 30% …”
- 技术栈清晰列出
- **产出**：一份一页纸的中文简历

#### 第 22 周：八股整理

- Python 八股 30 题
- 数据库八股 20 题
- 网络八股 15 题
- AI Agent 专项 20 题（RAG 优化、Agent 架构、MCP 等）
- **产出**：自己的面试题库文档

#### 第 23 周：模拟面试 + 算法突击

- 找同学互相模拟，或对着镜子练
- LeetCode Hot 100 再刷一遍重点题
- **产出**：能流畅讲清楚 SmartKB 架构

#### 第 24 周：开始投递！

- **渠道**：BOSS 直聘、实习僧、牛客网、各大厂官网
- **策略**：先投中小厂练手，再投大厂
- **产出**：第一封投出的简历

---

## 📚 推荐资源（不让你走弯路）

### Python 底层

- 《流畅的 Python》（先看第 1、3、5、7、15、16 章）
- 牛客网 Python 专项练习（每天 10 题）

### 算法

- **主战场**：LeetCode Hot 100（至少刷 2 遍）
- **辅助**：labuladong 算法小抄（公众号 / 网站，看 DP 和回溯部分）

### 计算机网络

- 《图解 HTTP》（2 天能看完）
- 《图解 TCP / IP》（重点看 TCP 章节）
- 小林 Coding 网络部分（网站，面试版）

### 数据库

- **MySQL**：《MySQL 必知必会》+ 极客时间《MySQL 实战 45 讲》（看前 20 讲）
- **Redis**：《Redis 设计与实现》（重点看数据结构和持久化）
- **面试题**：牛客 SQL 实战 + 牛客 Redis 专项

### AI Agent

- LangGraph 官方文档（必看 Tutorial）
- MCP 官方文档（理解架构即可）
- 项目：你已有的 LangChain 11 课是基础，LangGraph 是进阶

---

## ⚠️ 关键提醒

1. **算法不能断**：即使“做项目为主”，LeetCode 每天至少 1 题保持手感。大厂面试算法是“斩杀线”。
2. **不要同时学太多**：每周聚焦 1–2 个主题，深度理解比广度重要。
3. **GitHub 要绿**：每周至少提交 3–5 次代码，养成记录习惯。
4. **写博客**：每学完一个大模块，写一篇技术博客（掘金 / CSDN / 知乎）。倒逼输出 = 检验理解。
5. **期末先安心考试**：暑假才是主战场，现在别急。

---

## ✅ 本周行动清单（以 7 月第 1 周为例）

- [ ] 阅读《流畅的 Python》第 1、3 章（装饰器 + 生成器）
- [ ] LeetCode：1. Two Sum、15. 3Sum、53. Maximum Subarray
- [ ] LeetCode：21. Merge Two Sorted Lists、141. Linked List Cycle
- [ ] 手写装饰器底层代码（不带 `@` 语法糖版本）
- [ ] 整理“Python 八股 10 题”到笔记

---

> **文档创建时间**：2026-06-03  
> **下次更新时间**：每周末回顾后更新进度与下周计划
