from fastapi.testclient import TestClient
from main import app
    
client = TestClient(app)

def test_register_user():
    response = client.post("/register", json={"name": "New User", "email": "new-test@example.com", "password": "TestPass123!"})
    assert response.status_code == 200
    assert "email" in response.json()

def test_duplicate_user_registration():
    client.post("/register", json={"name": "Test User", "email": "dup@example.com", "password": "TestPass123!"})
    response = client.post("/register", json={"name": "Test User", "email": "dup@example.com", "password": "TestPass123!"})
    assert response.status_code == 400

def test_login_user():
    client.post("/register", json={"name": "Login User", "email": "login@example.com", "password": "LoginPass123!"})
    response = client.post("/token", data={"username": "login@example.com", "password": "LoginPass123!"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_create_device():
    client.post("/register", json={"name": "Device User", "email": "device@example.com", "password": "DevicePass123!"})
    login_response = client.post("/token", data={"username": "device@example.com", "password": "DevicePass123!"})
    token = login_response.json()["access_token"]
    response = client.post("/devices", json={"name": "Sensor", "location": "Lab"}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["name"] == "Sensor"

def test_list_devices_unauthorized():
    response = client.get("/devices")
    assert response.status_code == 401

def test_list_devices():
    client.post("/register", json={"name": "Device List User", "email": "devicelist@example.com", "password": "ListPass123!"})
    login_response = client.post("/token", data={"username": "devicelist@example.com", "password": "ListPass123!"})
    token = login_response.json()["access_token"]
    client.post("/devices", json={"name": "Thermometer", "location": "Room"}, headers={"Authorization": f"Bearer {token}"})
    response = client.get("/devices", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_post_telemetry_unauthorized():
    response = client.post("/telemetry", json={"device_id": 1, "data": {"temp": 25}})
    assert response.status_code == 401

def test_post_and_get_telemetry():
    client.post("/register", json={"name": "Telemetry User", "email": "telemetry@example.com", "password": "Telemetry123!"})
    login_response = client.post("/token", data={"username": "telemetry@example.com", "password": "Telemetry123!"})
    token = login_response.json()["access_token"]
    device_response = client.post("/devices", json={"name": "Thermo", "location": "Office"}, headers={"Authorization": f"Bearer {token}"})
    device_id = device_response.json()["id"]
    telemetry_response = client.post("/telemetry", json={"device_id": device_id, "data": {"temperature": 22}}, headers={"Authorization": f"Bearer {token}"})
    assert telemetry_response.status_code == 200
    response = client.get(f"/telemetry/{device_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) == 1
