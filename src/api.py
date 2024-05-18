import requests
from flask import Flask, jsonify, request
from stripGekko import StripGekko

app = Flask(__name__)
stripGekko = StripGekko()



@app.route("/")
def home():
    return "I dont like myself"


@app.route("/TVL")
def TVL():
    data = stripGekko.getTVL()
    print(data)
    return jsonify(data)


@app.route("/coin")
def coin():
    coin = request.args.get('coin')
    data = stripGekko.getCoin(coin)
    return jsonify(data)


@app.route("/chart")
def chart():
    coinpair = request.args.get('coinpair')
    data = stripGekko.getHistoricalData(coinpair)
    return jsonify(data)


@app.route("/tickers")
def tickers():
    coin = request.args.get('coin')
    data = stripGekko.getCoin(coin)

    # ugly temporary variables and maths stuff
    tp = float(data["price"].replace("$", "").replace(",", ""))
    tm = float(data["movement"].replace("%", "").replace("-", ""))

    og_price = tp / (1 + tm / 100)
    data = {
        "price": data["price"],
        "movement": data["movement"],
        "24h_price": og_price
    }


    return jsonify(data)
    
    