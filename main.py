import pandas as pd
from dotenv import dotenv_values
import requests
import json
import os

config = dotenv_values(".env")
key = os.environ.get("APIKEY")

# billQuery = f"https://api.congress.gov/v3/bill?limit=200&api_key={key}"
# response = requests.get(billQuery)

# print(response)
# data = response.json()
# print(data["bills"])
# df = pd.DataFrame(data["bills"])
# print(df.head())
# print(df.shape)
# pd.DataFrame(df).to_csv("bills.csv", index=False)

actionQuery = (
    f"https://api.congress.gov/v3/bill/117/hr/3076/actions?limit=200&api_key={key}"
)
actionResponse = requests.get(actionQuery)
print(actionResponse)
actionData = actionResponse.json()
print(actionData["actions"])
actionDF = pd.DataFrame(actionData["actions"])
print(actionDF.head())
print(actionDF.shape)
pd.DataFrame(actionDF).to_csv("actions.csv", index=False)
