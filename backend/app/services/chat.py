from openai import OpenAI

from app.config import Settings
from app.models import DataSummary, Message
from app.services.summary import summary_prompt


def mock_answer(question: str, summary: DataSummary) -> str:
    metrics = summary.metrics
    return (
        f"저장된 {summary.count}개 기록({summary.period})을 기준으로 보면 최근 값은 "
        f"{metrics.latest:,.0f}천 명이고, 최근 추세는 {summary.trend}입니다. "
        f"전체 평균은 {metrics.average:,.1f}천 명, 최고값은 {metrics.maximum:,.0f}천 명입니다. "
        f"질문 ‘{question}’에 대해서는 이 요약 범위 안에서 판단했으며, 외부 사건의 영향은 추가 데이터가 필요합니다."
    )


def generate_answer(question: str, history: list[Message], summary: DataSummary, settings: Settings) -> str:
    if settings.ai_backend.lower() == "mock":
        return mock_answer(question, summary)
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY가 설정되지 않았습니다.")

    client = OpenAI(api_key=settings.openai_api_key)
    input_messages = [message.model_dump() for message in history[-10:]]
    input_messages.append({"role": "user", "content": question})
    response = client.responses.create(
        model=settings.openai_model,
        instructions=summary_prompt(summary),
        input=input_messages,
        max_output_tokens=settings.openai_max_output_tokens,
        store=False,
    )
    return response.output_text.strip()
