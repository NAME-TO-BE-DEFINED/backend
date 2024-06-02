import requests

ENDPOINT = "http://127.0.0.1:5000"


def test_rickroll():
    r = requests.get(ENDPOINT)
    assert r.status_code == 200


def test_get_tvl():
    r = requests.get(ENDPOINT + "/TVL")
    assert r.status_code == 200

    data = r.json()
    assert data["TVL"]
    assert data["movement"]


def test_get_coin():
    r = requests.get(ENDPOINT + "/coin?coin=bitcoin")
    assert r.status_code == 200

    data = r.json()
    assert data["price"]
    assert data["movement"]
    assert data["symbol"]


def test_get_chart():
    r = requests.get(ENDPOINT + "/chart?coinpair=BTCUSDC")
    assert r.status_code == 200
    assert type(r.json()["data"]) is list


def test_get_tickers():
    r = requests.get(ENDPOINT + "/tickers?coin=bitcoin")
    data = r.json()

    assert r.status_code == 200
    assert data["price"]
    assert data["movement"]
    assert data["24h_price"]