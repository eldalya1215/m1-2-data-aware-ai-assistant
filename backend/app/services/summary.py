from statistics import fmean

from app.models import DataRecord, DataSummary, SummaryMetrics


def build_summary(records: list[DataRecord]) -> DataSummary:
    if not records:
        return DataSummary(
            period="데이터 없음",
            count=0,
            metrics=SummaryMetrics(total=0, average=0, maximum=0, minimum=0, latest=0),
            trend="데이터 부족",
            recent_change_pct=None,
            latest_date=None,
        )

    ordered = sorted(records, key=lambda item: item.date)
    values = [record.value for record in ordered]
    window = min(6, len(values) // 2)
    change_pct = None
    trend = "데이터 부족"
    if window >= 2:
        previous = fmean(values[-2 * window : -window])
        recent = fmean(values[-window:])
        change_pct = 0.0 if previous == 0 else (recent / previous - 1) * 100
        if change_pct > 2:
            trend = "상승"
        elif change_pct < -2:
            trend = "하락"
        else:
            trend = "유지"

    return DataSummary(
        period=f"{ordered[0].date:%Y-%m} ~ {ordered[-1].date:%Y-%m}",
        count=len(ordered),
        metrics=SummaryMetrics(
            total=round(sum(values), 2),
            average=round(fmean(values), 2),
            maximum=round(max(values), 2),
            minimum=round(min(values), 2),
            latest=round(values[-1], 2),
        ),
        trend=trend,
        recent_change_pct=None if change_pct is None else round(change_pct, 2),
        latest_date=ordered[-1].date,
    )


def summary_prompt(summary: DataSummary) -> str:
    metrics = summary.metrics
    return f"""당신은 사용자의 국제선 승객 시계열 데이터를 이해하는 한국어 데이터 분석 비서입니다.

[사용자 데이터 요약]
- 기간: {summary.period}
- 레코드: {summary.count}개
- 평균: {metrics.average:,.2f}천 명
- 최대: {metrics.maximum:,.2f}천 명
- 최소: {metrics.minimum:,.2f}천 명
- 최근 값: {metrics.latest:,.2f}천 명
- 최근 추세: {summary.trend} ({summary.recent_change_pct if summary.recent_change_pct is not None else '계산 불가'}%)

위 수치를 우선 근거로 답하세요. 관찰과 가능한 원인 가설을 구분하고, 데이터에 없는 외부 원인은 단정하지 마세요. 답변은 간결한 한국어로 작성하세요."""
