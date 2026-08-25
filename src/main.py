from fastapi import FastAPI
from pydantic import BaseModel
import re

app = FastAPI(title="Support Ticket Routing API (PoC)")


class TicketRequest(BaseModel):
    ticket_id: str
    text: str


class RoutingResponse(BaseModel):
    ticket_id: str
    status: str
    category: str | None = None
    confidence: float
    masked_text: str


def scrub_pii(text: str) -> str:
    """Маскирование персональных данных (PII)."""
    text = re.sub(r'\+?\d{10,15}', '[PHONE]', text)
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', '[EMAIL]', text)
    return text


def mock_ml_predict(text: str) -> tuple[str, float]:
    """Эвристическая заглушка, заменяющая ML-модель для PoC."""
    text_lower = text.lower()
    if "оплата" in text_lower or "карта" in text_lower:
        return "billing", 0.95
    elif "пароль" in text_lower or "доступ" in text_lower:
        return "tech_support", 0.90
    else:
        return "unknown", 0.45  # Низкая уверенность для fallback


@app.post("/route_ticket", response_model=RoutingResponse)
async def route_ticket(ticket: TicketRequest):
    # 1. Синхронная очистка данных
    masked_text = scrub_pii(ticket.text)

    # 2. Получение предсказания
    category, confidence = mock_ml_predict(masked_text)

    # 3. Реализация паттерна Fast & Slow Paths
    if confidence >= 0.85:
        # Happy Path: Уверенная маршрутизация
        return RoutingResponse(
            ticket_id=ticket.ticket_id,
            status="auto_routed",
            category=category,
            confidence=confidence,
            masked_text=masked_text
        )
    else:
        # Fallback Path: Эскалация на оператора (human-in-the-loop)
        return RoutingResponse(
            ticket_id=ticket.ticket_id,
            status="needs_human_review",
            category=None,
            confidence=confidence,
            masked_text=masked_text
        )