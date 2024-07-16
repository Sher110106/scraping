import unicodedata
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Load the CSV file into a DataFrame
df = pd.read_csv('urls.csv')

# Specify the column you want to work with
target_column = 'URLs'

# Filter out rows where the target column contains "Company Name"

error_companies = []
# Initialize columns for each rating category
rating_categories = [
    'Work Balance Rating', 'Promotions Rating', 'Job Security Rating',
    'Salary Rating', 'Skill Development Rating', 'Work Satisfaction Rating',
    'Company Culture Rating'
]
for category in rating_categories:
    df[category] = None

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

# Define a helper function to extract company name
def extract_company_name(content):
    h1_tag = content.find('h1', class_='text-xl font-pn-700 text-primary-text mr-1 md:text-2xl line-clamp-1')
    if h1_tag:
        return h1_tag.get_text().strip()
    return None

# Define the action you want to perform on each item
def perform_action(item):
    search_url = item
    payload = {
        'api_key': '2a9459668bef6c002240ab51c0e96f5d',
        'url': search_url
    }

    categories = {
        'Work Balance Rating': 'Work-Life BalanceGlobalLink',
        'Promotions Rating': 'Promotions / AppraisalGlobalLink',
        'Job Security Rating': 'Job SecurityGlobalLink',
        'Salary Rating': 'Salary & BenefitsGlobalLink',
        'Skill Development Rating': 'Skill DevelopmentGlobalLink',
        'Work Satisfaction Rating': 'Work SatisfactionGlobalLink',
        'Company Culture Rating': 'Company CultureGlobalLink'
    }

    try:
        response = requests.get('https://api.scraperapi.com/', params=payload)
        if response.status_code == 200:
            print(f"Valid URL: {search_url}")
            content = BeautifulSoup(response.text, 'html.parser')

            company_name = extract_company_name(content)
            if not company_name:
                company_name = "Unknown Company"

            ratings = {}

            for category, data_testid in categories.items():
                rating = extract_rating(content, data_testid)
                if rating:
                    print(f"{category} for {company_name}: {rating}")
                ratings[category] = rating

            return company_name, ratings
        else:
            print(f"Invalid URL: {search_url} (Status Code: {response.status_code})")
            error_companies.append(item)
            return "Unknown Company", {category: None for category in categories.keys()}
    except requests.RequestException as e:
        print(f"Error accessing URL: {search_url} (Error: {e})")
        error_companies.append(item)
        return "Unknown Company", {category: None for category in categories.keys()}

# Apply the action to each item in the target column
results = df[target_column].apply(perform_action)

# Update the DataFrame with the results
df['Name'] = results.apply(lambda x: x[0])
for category in rating_categories:
    df[category] = results.apply(lambda x: x[1].get(category))

# Drop the original URL column
df.drop(columns=[target_column], inplace=True)

# Save the updated DataFrame back to a CSV file
df.to_csv('updates.csv', index=False)
error_df = pd.DataFrame(error_companies, columns=[target_column])
error_df.to_csv('errors.csv', index=False)
