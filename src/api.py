import requests
from flask import Flask, jsonify
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





