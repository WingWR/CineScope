from __future__ import annotations

from server.app.modules.agent.planner import AgentPlan
from server.app.modules.recommendations.schemas import RecommendationItem


RECOMMENDATION_SYSTEM_PROMPT = """
你是 CineScope 课程项目中的电影推荐解释助手。
你只能基于给定的推荐结果、本地 RAG 片段和用户需求来组织回答。
不要新增电影，不要编造评分、年份、票房、算法结论或数据来源。
回答必须使用中文，语气简洁，适合课程项目演示。
""".strip()

PROJECT_QA_SYSTEM_PROMPT = """
你是 CineScope 课程项目的项目答辩助手。
你只能基于给定的本地 RAG 检索内容回答。
如果给定资料不足，请明确说“当前本地资料中没有足够信息”。
不要编造未实现的功能、指标或外部数据。
回答必须使用中文，并适合课程答辩说明。
""".strip()


def build_recommendation_messages(
    *,
    user_prompt: str,
    plan: AgentPlan,
    rag_context: str,
    items: list[RecommendationItem],
) -> list[dict[str, str]]:
    item_lines = []
    for item in items:
        item_lines.append(
            f"- {item.movie.title} | 年份={item.movie.year or '未知'} | 类型={', '.join(item.movie.genres[:3]) or '未知'} "
            f"| 分数={item.score:.3f} | 当前理由={item.reason}"
        )
    return [
        {"role": "system", "content": RECOMMENDATION_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"用户需求：{user_prompt or '未提供自然语言描述'}\n"
                f"解析条件：{plan.recommendation_summary()}\n"
                f"RAG 检索片段：\n{rag_context or '无'}\n"
                f"本地推荐结果：\n" + "\n".join(item_lines) + "\n"
                "请用 1 到 2 句中文总结这些推荐共有的依据，方便直接追加到推荐理由里。"
            ),
        },
    ]


def build_project_qa_messages(
    *,
    user_message: str,
    rag_context: str,
) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": PROJECT_QA_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"用户问题：{user_message}\n"
                f"RAG 检索片段：\n{rag_context or '无'}\n"
                "请基于这些资料直接回答。"
            ),
        },
    ]
