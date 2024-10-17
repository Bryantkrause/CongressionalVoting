import requests
import xml.etree.ElementTree as ET
import pandas as pd


# Step 1: Fetch the XML data from the URL
url = "https://www.senate.gov/legislative/LIS/roll_call_votes/vote1172/vote_117_2_00071.xml"
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Step 2: Parse the XML data
    xml_data = response.content
    root = ET.fromstring(xml_data)

    # Step 3: Extract relevant data into a list of dictionaries
    rows = []

    # Iterate through each member in the XML and extract the required details
    for member in root.findall(
        ".//member"
    ):  # Adjust the tag to match the structure in the XML
        vote_dict = {
            "member_full": (
                member.find("member_full").text
                if member.find("member_full") is not None
                else ""
            ),
            "last_name": (
                member.find("last_name").text
                if member.find("last_name") is not None
                else ""
            ),
            "first_name": (
                member.find("first_name").text
                if member.find("first_name") is not None
                else ""
            ),
            "party": (
                member.find("party").text if member.find("party") is not None else ""
            ),
            "state": (
                member.find("state").text if member.find("state") is not None else ""
            ),
            "vote_cast": (
                member.find("vote_cast").text
                if member.find("vote_cast") is not None
                else ""
            ),
        }
        # Add the dictionary to the list
        rows.append(vote_dict)

    # Step 4: Create a DataFrame from the list of dictionaries
    df = pd.DataFrame(rows)

    # Display the DataFrame
    print(df.head())  # Preview the first few rows
else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")
