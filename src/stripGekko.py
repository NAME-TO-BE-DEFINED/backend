from bs4 import BeautifulSoup
import requests


class StripGekko:

    def __init__(self):
        # URL's for scraping data
        self.TVL = "https://www.coingecko.com/en/chains"
        self.COIN = "https://www.coingecko.com/en/coins/"
    

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

        
    

