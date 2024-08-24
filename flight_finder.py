"""
This script is used to find flights from one city to another.

References:
1. https://support.travelpayouts.com/hc/en-us/articles/203956083-Requirements-for-Aviasales-data-API-access
"""

import requests
import os
import datetime
import pandas as pd

class EnvLoader:
    @staticmethod
    def load_env(file_path='.env'):
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

class FlightSearchParams:
    def __init__(self, origin, destination, currency, page, unique, sorting, beginning_of_period, period_type, limit=30):
        self.origin = origin
        self.destination = destination
        self.currency = currency
        self.page = page
        self.limit = limit
        self.unique = unique
        self.sorting = sorting
        self.beginning_of_period = beginning_of_period
        self.period_type = period_type

    def to_dict(self):
        return {
            "origin": self.origin,
            "destination": self.destination,
            "currency": self.currency,
            "page": self.page,
            "limit": self.limit,
            "unique": self.unique,
            "sorting": self.sorting,
            "beginning_of_period": self.beginning_of_period,
            "period_type": self.period_type
        }

class FlightFinder:
    def __init__(self):
        EnvLoader.load_env()
        self.api_key = os.getenv("TRAVELPAYOUTS_API_KEY")
        self.url = "https://api.travelpayouts.com/v2/prices/latest"

    def find_flights(self, params: FlightSearchParams):
        headers = {"X-Access-Token": self.api_key}
        response = requests.get(self.url, headers=headers, params=params.to_dict())
        return response.json()

    def best_flight(self):
        params = FlightSearchParams(
            origin="SJC",       # Origin airport code (San Francisco)
            destination="LIM",  # Destination airport code (Lima)
            currency="USD",     # Currency of the price
            page=1,
            unique="true",
            sorting="price", 
            beginning_of_period="2024-09-01",
            period_type="month"
        )

        data = self.find_flights(params)

        short_listed = [
            flight for flight in data["data"]
            if (datetime.datetime.strptime(flight["return_date"], "%Y-%m-%d") - 
                datetime.datetime.strptime(flight["depart_date"], "%Y-%m-%d")).days > 7
        ]

        short_listed_df = pd.DataFrame(short_listed).sort_values(by="duration")
        return short_listed_df.head(1)

if __name__ == "__main__":
    flight_finder = FlightFinder()
    print(flight_finder.best_flight())