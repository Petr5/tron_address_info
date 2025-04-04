from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_post_address_real_request():
    response = client.post(
        "/address/",
        json={"address": "TCw6YaWm3y6DvxY7M8hrCDnrJGeGMumzGJ"},
    )

    assert response.status_code == 200, response.json()
    data = response.json()

    assert data["address"] == "TCw6YaWm3y6DvxY7M8hrCDnrJGeGMumzGJ"
    assert "trx_balance" in data
    assert "bandwidth" in data
    assert "energy" in data

    # print(
    #     "\nTRX:",
    #     data["trx_balance"],
    #     "| Bandwidth:",
    #     data["bandwidth"],
    #     "| Energy:",
    #     data["energy"],
    # )
