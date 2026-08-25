from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_scrub_pii_and_status_200():
    """Проверка доступности эндпоинта и корректного маскирования PII."""
    response = client.post(
        "/route_ticket",
        json={"ticket_id": "1", "text": "Мой телефон +79991234567, почта test@test.com"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "[PHONE]" in data["masked_text"]
    assert "[EMAIL]" in data["masked_text"]

def test_happy_path_routing():
    """Проверка уверенной классификации (Confidence >= 0.85)."""
    response = client.post(
        "/route_ticket",
        json={"ticket_id": "2", "text": "Не проходит оплата по карте"}
    )
    data = response.json()
    assert data["status"] == "auto_routed"
    assert data["category"] == "billing"
    assert data["confidence"] >= 0.85

def test_fallback_path_routing():
    """Проверка эскалации на оператора при нестандартном запросе."""
    response = client.post(
        "/route_ticket",
        json={"ticket_id": "3", "text": "Странная ошибка при входе, ничего не понятно"}
    )
    data = response.json()
    assert data["status"] == "needs_human_review"
    assert data["confidence"] < 0.85