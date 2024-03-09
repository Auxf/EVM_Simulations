import json
import requests
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np

def find_address_by_symbol(symbol, data):
    for item in data:
        if item['symbol'] == symbol:
            return item['address']
    return None

def get_price_data(contract, start_timestamp, period_days):
    if contract.startswith("0x"):
        # Ethereum contract address
        contract = f"ethereum:{contract}"
    url = f"https://coins.llama.fi/chart/{contract}?start={start_timestamp}&span={period_days}&period=1d"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        prices = data.get('coins', {}).get(contract, {}).get('prices', [])
        timestamps = [datetime.utcfromtimestamp(price['timestamp']) for price in prices]
        prices = [price['price'] for price in prices]
        return timestamps, prices
    else:
        print(f"Failed to retrieve price data: {response.status_code}")
        return [], []

file_path = "protocols_contracts.json"

try:
    with open(file_path, 'r') as file:
        protocols_data = json.load(file)
except FileNotFoundError:
    print(f"File '{file_path}' not found.")
    exit()

def parse_period(period):
    periods = {'1y': 365, '6m': 6*30, '3m': 3*30, '1m': 30}
    return periods.get(period, 365)

symbols = []
while True:
    symbol = input("Enter the symbol of the protocol (or 'done' to finish): ")
    if symbol.lower() == 'done':
        break
    symbols.append(symbol)

if not symbols:
    print("No symbols provided. Exiting...")
    exit()

period_input = input("Enter the period ('1y', '6m', '3m', or '1m'): ")
period_days = parse_period(period_input)
start_timestamp = int((datetime.utcnow() - timedelta(days=period_days)).timestamp())

plt.figure(figsize=(10, 6))

min_date = datetime.utcnow()
max_date = datetime.utcfromtimestamp(start_timestamp)

for symbol in symbols:
    protocol_address = find_address_by_symbol(symbol, protocols_data)
    if protocol_address:
        timestamps, prices = get_price_data(protocol_address, start_timestamp, period_days)
        print("Timestamps:", timestamps)  # Debugging statement
        print("Prices:", prices)  # Debugging statement
        if timestamps and prices:
            # Sort timestamps in ascending order
            timestamps, prices = zip(*sorted(zip(timestamps, prices)))
            
            # Calculate cumulative daily percentage change
            prices = np.array(prices)
            daily_change = (prices[1:] - prices[:-1]) / prices[:-1] * 100
            cumulative_change = np.cumsum(daily_change)
            timestamps = timestamps[1:]  # Remove first timestamp since there's no change for it

            print("Cumulative Daily Percentage Change:", cumulative_change)  # Debugging statement

            # Plotting the line chart for cumulative daily percentage change
            plt.plot(timestamps, cumulative_change, label=symbol)

            # Update min_date and max_date based on retrieved timestamps
            if timestamps and timestamps[0] < min_date:
                min_date = timestamps[0]
            if timestamps and timestamps[-1] > max_date:
                max_date = timestamps[-1]

# Adjust x-axis limits based on the chosen period
plt.xlim(min_date, max_date)

plt.title(f'Cumulative Daily Percentage Change of Protocols ({period_input})')
plt.xlabel('Date')
plt.ylabel('Cumulative Daily Percentage Change (%)')
plt.xticks(rotation=45)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
