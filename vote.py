import requests
import json
from dotenv import dotenv_values
import os

import xml.etree.ElementTree as ET
config = dotenv_values(".env")
# Define the base URL for the Congress API
api_base_url = "https://api.congress.gov/v3"
api_key = os.environ.get("APIKEY")  # Replace with your actual API key


# Function to get actions (including votes) for a bill
def get_bill_actions(congress_num, bill_type, bill_num):
    url = f"{api_base_url}/bill/{congress_num}/{bill_type}/{bill_num}/actions?limit=200&api_key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None


# Function to fetch and parse the XML from the recordedVotes URL
def fetch_and_parse_vote_xml(vote_url):
    response = requests.get(vote_url)
    if response.status_code == 200:
        return ET.fromstring(response.content)
    else:
        print(f"Error fetching XML data: {response.status_code}")
        return None


# Function to extract votes from the parsed XML
def extract_votes_from_xml(xml_data, chamber):
    if xml_data is None:
        return None, None

    # Extract votes by senator or representative
    by_member = []
    by_party = {}

    # Navigate through the XML structure (adjust based on chamber: Senate or House)
    if chamber == "Senate":
        members = xml_data.findall(".//members/member")
    elif chamber == "House":
        members = xml_data.findall(".//vote-data/recorded-vote")
    else:
        print("Invalid chamber specified")
        return None, None

    for member in members:
        if chamber == "Senate":
            senator_name = member.find("last_name").text
            party = member.find("party").text
            state = member.find("state").text
            vote_position = member.find("vote_cast").text  # "Yea", "Nay", etc.
        elif chamber == "House":
            senator_name = member.find("legislator/last-name").text
            party = member.find("legislator/party").text
            state = member.find("legislator/state").text
            vote_position = member.find("vote").text  # "Aye", "No", etc.

        # Add to individual member votes
        by_member.append(
            {
                "name": senator_name,
                "party": party,
                "state": state,
                "vote_position": vote_position,
            }
        )

        # Add to party-based aggregation
        if party not in by_party:
            by_party[party] = {"Yea": 0, "Nay": 0, "Not Voting": 0}

        if vote_position in ["Yea", "Aye"]:  # Adjust for different chamber's terms
            by_party[party]["Yea"] += 1
        elif vote_position in ["Nay", "No"]:
            by_party[party]["Nay"] += 1
        else:
            by_party[party]["Not Voting"] += 1

    return by_member, by_party


# Function to iterate over recordedVotes and fetch data for each
def process_all_votes(congress_num, bill_type, bill_num):
    actions_data = get_bill_actions(congress_num, bill_type, bill_num)

    if actions_data is None:
        return

    all_votes_by_senator = []
    all_votes_by_party = {}

    # Iterate over actions and process each recordedVotes URL
    for action in actions_data.get("actions", []):
        recorded_votes = action.get("recordedVotes", [])
        for vote in recorded_votes:
            vote_url = vote["url"]
            chamber = vote["chamber"]

            # Fetch and parse vote XML
            xml_data = fetch_and_parse_vote_xml(vote_url)

            # Extract votes by senator/representative and by party
            votes_by_senator, votes_by_party = extract_votes_from_xml(xml_data, chamber)

            # Collect votes by senator/representative
            if votes_by_senator:
                all_votes_by_senator.extend(votes_by_senator)

            # Merge party votes into the overall summary
            if votes_by_party:
                for party, votes in votes_by_party.items():
                    if party not in all_votes_by_party:
                        all_votes_by_party[party] = {
                            "Yea": 0,
                            "Nay": 0,
                            "Not Voting": 0,
                        }
                    all_votes_by_party[party]["Yea"] += votes["Yea"]
                    all_votes_by_party[party]["Nay"] += votes["Nay"]
                    all_votes_by_party[party]["Not Voting"] += votes["Not Voting"]

    return all_votes_by_senator, all_votes_by_party


# Example usage
congress_num = "117"
bill_type = "hr"
bill_num = "3076"  # Example bill number

# Process all recorded votes for this bill
votes_by_senator, votes_by_party = process_all_votes(congress_num, bill_type, bill_num)

# Display results
print("All Votes by Senator/Representative:")
print(votes_by_senator)

print("\nAll Votes by Party:")
print(votes_by_party)
