"""
AI agent recommends itinerary for a trip based on cheapest flight duration.
"""

from flight_finder import FlightFinder
from flight_finder import EnvLoader

import os
import datetime

import pandas as pd

from groq import Groq

# Create the Groq client
EnvLoader.load_env()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"), )

# Set the system prompt
system_prompt = {
    "role": "system",
    "content": "You are an expert at planning trips in South America."
}

# Initialize the chat history
chat_history = [system_prompt]

# Find the best flight, start and end date of on-ground time
best_flight = FlightFinder().best_flight()

print("Best flight details are as follows:")
for keys, values in best_flight.items():
    print(f"{keys}: {values}")

trip_start_date = datetime.datetime.strptime(best_flight['depart_date'], "%Y-%m-%d")
trip_end_date = datetime.datetime.strptime(best_flight['return_date'], "%Y-%m-%d")
user_input = (f"The flights depart from {best_flight["origin"]} and arrive in {best_flight["destination"]}."
              f"They cost {best_flight["value"]} USD."
              f"Plan a trip in Peru starting from {trip_start_date} in Lima to {trip_end_date} in Lima."
              f"Please provide a day by day itinerary for the trip in JSON format including which city to spend time in and the recommended activity for the day."
              f"Example: {{\"day\": \"October 1st, 2024\", \"city\": \"Lima\", \"activity\": \"Visit the historical center, museums, and markets.\"}}")

# Append the user input to the chat history
chat_history.append({"role": "user", "content": user_input})

response = client.chat.completions.create(model="llama3-70b-8192",
                                          messages=chat_history,
                                          max_tokens=8192,
                                          temperature=0.7)

# Append the response to the chat history
chat_history.append({
  "role": "assistant",
  "content": response.choices[0].message.content
})
  
# Print the response
print("Assistant:", response.choices[0].message.content)