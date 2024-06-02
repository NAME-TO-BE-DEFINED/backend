from bs4 import BeautifulSoup
import requests
from binance import Client
import os
from dotenv import load_dotenv
import pprint


load_dotenv()

class StripGekko:

    def __init__(self):
        # URL's for scraping data
        self.TVL = "https://www.coingecko.com/en/chains"
        self.COIN = "https://www.coingecko.com/en/coins/"
        self.api_key = os.getenv("API_KEY")
        self.secret_key = os.getenv("secret_key")
        self.client = Client(self.api_key, self.secret_key)
    

    def getTVL(self):
        r = requests.get(self.TVL)
        soup = BeautifulSoup(r.text, 'html.parser')
        data = soup.find(class_="tw-text-xs tw-leading-4 tw-text-gray-500 dark:tw-text-moon-200 tw-font-regular md:!tw-text-sm")
        movement = data.find("span")

        # Abstracs TVL from data
        for i, word in enumerate(data.text.split()):
            if "$" in word:
                tvl = word + " " + data.text.split()[i+1].replace(",","")
                break


        # TODO: Get list of CTF's from database

        data = {
            "TVL": tvl,
            "movement": movement.text
        }

        return data

    # Function too ugly dont peak
    def getCoin(self, coin):
        r = requests.get(self.COIN + coin)
        soup = BeautifulSoup(r.text, 'html.parser')


        price = soup.find("span", {"data-price-target":"price"}).text
        movement = soup.find("span", {"data-percent-change-target":"percent"})
        symbol = soup.find("span", {"data-view-component":"true", "class":"tw-font-normal tw-text-gray-500 dark:tw-text-moon-200 tw-text-sm tw-leading-5 tw-mt-0.5"}).text.replace("Price", "").strip() # super long line go brrr
        
        # adds - if down
        movement_binary = movement.get("class")
        movement = movement.text

        if movement_binary[0] == "gecko-down":
            movement = "-" + movement
        

        data = {
            "price": price,
            "movement": movement,
            "symbol": symbol
        }


        # Get data(Yea very detailed comment)
        tb = soup.find_all("tbody")[1]

        for row in tb.find_all("tr"):
            cols = row.find_all(['th', 'td'])

            # Needed to split lines to filter data
            x = cols[0].text.splitlines()[1].strip() 
            y = cols[1].text.splitlines()[1].strip()
            data[x] = y

        
        




        return data

    def getHistoricalData(self, coinpair):
        print(coinpair)
        klines = self.client.get_historical_klines(coinpair, Client.KLINE_INTERVAL_1HOUR, "1 day ago")
        return klines   





# StripGekko.getHistoricalData()