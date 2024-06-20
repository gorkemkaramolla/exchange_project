import requests
import json

def get_exchange_rate(base_currency='USD', target_currency='TRY', amount=1000):
    url = f"https://api.collectapi.com/economy/exchange?int={amount}&to={target_currency}&base={base_currency}"

    headers = {
        'content-type': "application/json",
        'authorization': "apikey 1ZEyjOoTARN56ebsNrELhF:7MlpGbzG0m6Sj6OBm1EJ02"
    }

    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        # Format the JSON data
        formatted_data = json.dumps(data, indent=4)
        print(formatted_data)
    else:
        print(f"Error: {response.status_code} - {response.text}")
        
get_exchange_rate()