from app.bot import send_alert

def test_send_alert():
    response = send_alert("Test Alert")
    assert response.status_code == 200
