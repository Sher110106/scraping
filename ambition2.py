import unicodedata

import pandas as pd
import requests
from bs4 import BeautifulSoup

# Load the CSV file into a DataFrame
df = pd.read_csv('next.csv')

# Specify the column you want to work with
target_column = 'Name'

# Filter out rows where the target column contains "Company Name"
filtered_df = df[~df[target_column].str.contains("Company Name", na=False)]
error_companies = []
# Initialize columns for each rating category
rating_categories = [
    'Work Satisfaction Rating'

]
for category in rating_categories:
    filtered_df[category] = None


# Define a helper function to extract rating
def extract_rating(content, data_testid):
    div = content.find('div', {'data-testid': data_testid})
    if div:
        parent_div = div.find_parent('div', class_='css-175oi2r')
        if parent_div:
            rating_div = parent_div.find('div', class_='css-146c3p1 text-primary-text text-sm font-pn-700 ml-1')
            if rating_div:
                return rating_div.get_text().strip()
    return None


# Define the action you want to perform on each item
def perform_action(item):
    # Normalize the string to decompose special characters
    item = unicodedata.normalize('NFKD', item).encode('ascii', 'ignore').decode('ascii')

    # Replace periods, '&', and possessive 's
    item2 = item.replace('.', '').replace('&', 'and').replace("'s", 's')

    # Convert to lowercase and replace spaces with hyphens
    new_item = item2.lower().replace(' ', '-')

    # Construct the search URL
    search_url = f'https://www.ambitionbox.com/overview/{new_item}-overview?section=aboutUs'
    payload = {
        'api_key': '2a9459668bef6c002240ab51c0e96f5d',
        'url': search_url
    }

    categories = {

        'Work Satisfaction Rating': 'Work SatisfactionGlobalLink'

    }

    try:
        response = requests.get('https://api.scraperapi.com/', params=payload)
        if response.status_code == 200:
            print(f"Valid URL: {search_url}")
            content = BeautifulSoup(response.text, 'html.parser')

            ratings = {}

            for category, data_testid in categories.items():
                rating = extract_rating(content, data_testid)
                if rating:
                    print(f"{category} for {item}: {rating}")
                ratings[category] = rating

            return ratings
        else:
            print(f"Invalid URL: {search_url} (Status Code: {response.status_code})")
            error_companies.append(item)
            return {category: None for category in categories.keys()}
    except requests.RequestException as e:
        print(f"Error accessing URL: {search_url} (Error: {e})")
        error_companies.append(item)
        return {category: None for category in categories.keys()}


# Apply the action to each item in the filtered target column
results = filtered_df[target_column].apply(perform_action)

# Update the DataFrame with the results
for category in rating_categories:
    filtered_df[category] = results.apply(lambda x: x.get(category))

# Save the updated DataFrame back to a CSV file
filtered_df.to_csv('next_answer.csv', index=False)
error_df = pd.DataFrame(error_companies, columns=[target_column])
error_df.to_csv('error_companies.csv', index=False)
