import pytest
import io
from service import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["status"] == "healthy"

def test_metrics_endpoint(client):
    res = client.get("/metrics")
    assert res.status_code == 200
    assert b"api_requests_total" in res.data

def test_style_transfer_missing_image(client):
    res = client.post("/styleTransfer")
    assert res.status_code == 400
    json_data = res.get_json()
    assert "error" in json_data

def test_style_transfer_valid_image(client):
    # Create sample in-memory image
    from PIL import Image
    img = Image.new("RGB", (100, 100), color="blue")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)

    data = {"image": (img_bytes, "test.jpg")}
    res = client.post("/styleTransfer", data=data, content_type="multipart/form-data")
    assert res.status_code == 200
    assert res.mimetype == "image/jpeg"
    assert len(res.data) > 0
