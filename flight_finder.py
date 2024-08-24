"""
This script is used to find flights from one city to another.
"""

import requests
import json
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
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "https://api.travelpayouts.com/v2/prices/latest"

    def find_flights(self, params: FlightSearchParams):
        headers = {
            "X-Access-Token": self.api_key
        }
        response = requests.get(self.url, headers=headers, params=params.to_dict())
        return response.json()

# Load the environment variables
EnvLoader.load_env()

# Your Travelpayouts API key
api_key = os.getenv("TRAVELPAYOUTS_API_KEY")

# Parameters for the flight search
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

# Create a FlightFinder instance
flight_finder = FlightFinder(api_key)

# Find flights
data = flight_finder.find_flights(params)

# Filter by depart_date and return_date of more than a week
short_listed = list()
for flight in data["data"]:
    depart_date = datetime.datetime.strptime(flight["depart_date"], "%Y-%m-%d")
    return_date = datetime.datetime.strptime(flight["return_date"], "%Y-%m-%d")
    if (return_date - depart_date).days > 7:
        short_listed.append(flight)

# Print the JSON response
short_listed = pd.DataFrame(short_listed).sort_values(by="duration")
print(short_listed)