import requests
import xml.etree.ElementTree as ET


# Function to fetch and parse the XML from the recordedVotes URL
def fetch_and_parse_vote_xml(vote_url):
    response = requests.get(vote_url)
    if response.status_code == 200:
        # Parse the XML response
        return ET.fromstring(response.content)
    else:
        print(f"Error fetching XML data: {response.status_code}")
        return None


# Function to inspect XML structure
def inspect_xml_structure(xml_data):
    print("Inspecting XML structure:")
    for elem in xml_data.iter():
        print(f"Tag: {elem.tag}, Text: {elem.text}")


# Function to extract votes from the parsed XML for Senate
def extract_senate_votes_from_xml(xml_data):
    if xml_data is None:
        return None, None

    by_senator = []
    by_party = {}

    # Extract vote records
    for vote in xml_data.findall(".//vote_cast"):
        senator_name_elem = vote.find("member_full")
        party_elem = vote.find("party")
        state_elem = vote.find("state")
        vote_position_elem = vote.find("vote_cast")

        # Ensure each element exists before trying to access it
        senator_name = (
            senator_name_elem.text if senator_name_elem is not None else "Unknown"
        )
        party = party_elem.text if party_elem is not None else "Unknown"
        state = state_elem.text if state_elem is not None else "Unknown"
        vote_position = (
            vote_position_elem.text if vote_position_elem is not None else "Unknown"
        )

        # Add to individual senator votes
        by_senator.append(
            {
                "senator": senator_name,
                "party": party,
                "state": state,
                "vote_position": vote_position,
            }
        )

        # Add to party-based aggregation
        if party not in by_party:
            by_party[party] = {"Yea": 0, "Nay": 0, "Not Voting": 0}

        if vote_position == "Yea":
            by_party[party]["Yea"] += 1
        elif vote_position == "Nay":
            by_party[party]["Nay"] += 1
        else:
            by_party[party]["Not Voting"] += 1

    return by_senator, by_party


# Example vote URL (from recordedVotes data)
vote_url = "https://www.senate.gov/legislative/LIS/roll_call_votes/vote1172/vote_117_2_00071.xml"

# Fetch and parse the XML data
xml_data = fetch_and_parse_vote_xml(vote_url)

# Inspect XML structure to see how it's organized
inspect_xml_structure(xml_data)

# Extract votes for the Senate
votes_by_senator, votes_by_party = extract_senate_votes_from_xml(xml_data)

# Display results
print("Votes by Senator:")
print(votes_by_senator)

print("\nVotes by Party:")
print(votes_by_party)
