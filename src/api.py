import requests
from flask import Flask, jsonify, request, redirect
from stripGekko import StripGekko
from contract import CTF
import os
from dotenv import load_dotenv
from pprint import pprint

app = Flask(__name__)
stripGekko = StripGekko()
load_dotenv()



@app.route("/")
def home():
    return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ")


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
    data = {
    "data": stripGekko.getHistoricalData(coinpair)
    }
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
    


Infura_key = os.getenv("infura_key")
chains = {
    "optimism": {
        "ENDPOINT": f"https://optimism-sepolia.infura.io/v3/{Infura_key}",
        "SWAP_ADDRESS": "0xdc478014d9c22969A82CD6dfb2Fa441618f3462b",
        "SWAP_provider": "0xdc478014d9c22969A82CD6dfb2Fa441618f3462b",
        "BALANCER_POOL_ADDRESS": "0x75DFc9064614498EDD9FAd00857d4917CAaDdeE5",
        "BALANCER_QUERIES": "0x268eb558B65526361599aB4108d3Ef53c3dB97b5",
        "ChainId": 11155420,
        "usdcAddress": "0x5fd84259d66Cd46123540766Be93DFE6D43130D7"
    },
    "base": {
        "ENDPOINT": f"https://base-sepolia.infura.io/v3/{Infura_key}",
        "SWAP_ADDRESS": "0xF4b37DBA9D8382294e66882dcfD55d65dDbAbFd2",
        "SWAP_provider": "0xF4b37DBA9D8382294e66882dcfD55d65dDbAbFd2",
        "BALANCER_POOL_ADDRESS": "0x5cc729e3099e6372E0e9406613E043e609d789be",
        "BALANCER_QUERIES": "0xaFEE0F279375E9544C4a745340487f4Cd9B5D17a",
        "ChainId": 84532,
        "usdcAddress": "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
    }
}


@app.route("/withraw")
def withraw():
    data = {}
    amount = int(request.args.get('ctfAmount'))
    for key, value in chains.items():
        ctf = CTF(Infura_endpoint=value["ENDPOINT"], SWAP_ADDRESS=value["SWAP_ADDRESS"], SWAP_provider=value["SWAP_provider"], BALANCER_POOL_ADDRESS=value["BALANCER_POOL_ADDRESS"], BALANCER_QUERIES=value["BALANCER_QUERIES"], ChainId=value["ChainId"], usdcAddress=value["usdcAddress"])
        e = ctf.withraw(amount)
        print("DONE!")
        data[key] = e

    return jsonify(data)

@app.route("/deposit")
def deposit():
    data = {}
    amount = int(request.args.get('usdcAmount'))
    for key, value in chains.items():
        ctf = CTF(Infura_endpoint=value["ENDPOINT"], SWAP_ADDRESS=value["SWAP_ADDRESS"], SWAP_provider=value["SWAP_provider"], BALANCER_POOL_ADDRESS=value["BALANCER_POOL_ADDRESS"], BALANCER_QUERIES=value["BALANCER_QUERIES"], ChainId=value["ChainId"], usdcAddress=value["usdcAddress"])
        e = ctf.deposit(amount)
        print("DONE!")
        data[key] = e


    swapProviders = []
    swapCalldata = []

    for key, value in data.items():
        swapProviders.append(value["SwapsProvider"])
        for i in value["SwapsCalldata"]:
            swapCalldata.append(i)
    
        data[key]["SwapsProvider"] = swapProviders
        data[key]["SwapsCalldata"] = swapCalldata



    return jsonify(data)
    
