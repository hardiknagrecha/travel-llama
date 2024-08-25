"""
AI agent recommends itinerary for a trip based on cheapest flight duration.
"""

import os
import json
import datetime
from flight_finder import FlightFinder, EnvLoader
from groq import Groq

class ItineraryPlanner:
    def __init__(self):
        EnvLoader.load_env()
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.system_prompt = {
            "role": "system",
            "content": "You are an expert at planning trips in South America."
        }
        self.chat_history = [self.system_prompt]
        self.best_flight = FlightFinder().best_flight()
        
    def get_itinerary(self):
        self._print_best_flight_details()
        user_input = self._generate_user_input()
        self.chat_history.append({"role": "user", "content": user_input})

        response = self.client.chat.completions.create(
            model="llama3-70b-8192",
            messages=self.chat_history,
            max_tokens=8192,
            temperature=0.7
        )

        self.chat_history.append({
            "role": "assistant",
            "content": response.choices[0].message.content
        })
        
        return json.loads(response.choices[0].message.content)

    def _print_best_flight_details(self):
        print("Best flight details are as follows:")
        for key, value in self.best_flight.items():
            print(f"{key}: {value}")

    def _generate_user_input(self):
        trip_start_date = datetime.datetime.strptime(self.best_flight['depart_date'], "%Y-%m-%d")
        trip_end_date = datetime.datetime.strptime(self.best_flight['return_date'], "%Y-%m-%d")
        return (f"The flights depart from {self.best_flight['origin']} and arrive in {self.best_flight['destination']}."
                f"They cost {self.best_flight['value']} USD."
                f"Plan a trip in Peru starting from {trip_start_date} in Lima to {trip_end_date} in Lima."
                f"Please provide a day by day itinerary for the trip in JSON format including which city to spend time in and the recommended activity for the day."
                f"Example: {{\"day\": \"10-01-2024\", \"city\": \"Lima\", \"activity\": \"Visit the historical center, museums, and markets.\"}}"
                f"Please be very detailed in the activity description, and only respond with the JSON string. Do not include text outside of the JSON format")

    @staticmethod
    def get_checkin_checkout_dates(itinerary):
        city_dates = {}
        current_city = None
        for day in itinerary:
            city = day['city']
            date = day['day']
            if city != current_city:
                if city not in city_dates:
                    city_dates[city] = []
                city_dates[city].append({'checkin': date, 'checkout': date})
                current_city = city
            else:
                city_dates[city][-1]['checkout'] = date
        return city_dates
    
if __name__ == "__main__":
    planner = ItineraryPlanner()
    itinerary = planner.get_itinerary()
    print(json.dumps(itinerary, indent=4))
    print(planner.get_checkin_checkout_dates(itinerary))