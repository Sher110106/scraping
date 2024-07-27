import pandas as pd
import requests
from bs4 import BeautifulSoup
import difflib
import unicodedata

# Load the CSV file into a DataFrame
df = pd.read_csv('FinTech.csv')

# Specify the column you want to work with
target_column = 'Name'

# Filter out rows where the target column contains "Company Name"
filtered_df = df[~df[target_column].str.contains("Company Name", na=False)]

# Normalize and construct the search URL
def perform_action(item):
    # Normalize the string to decompose special characters
    item = unicodedata.normalize('NFKD', item).encode('ascii', 'ignore').decode('ascii')

    # Replace periods, '&', and possessive 's
    item2 = item.replace('.', '').replace('&', 'and').replace("'s", 's')

    # Convert to lowercase and replace spaces with hyphens
    new_item = item2.lower().replace(' ', '-')

    # Construct the search URL
    search_url = f'https://www.ambitionbox.com/salaries/{new_item}-salaries'
    return search_url

# Fetch designations and salaries from a given URL
def fetch_designations(base_url, target_designations):
    designations = []
    page = 1
    found_designations = set()

    while len(found_designations) < len(target_designations):
        url = f"{base_url}?page={page}"
        payload = {
            'api_key': '7738cd1db4e3df17213dc62bb854986f',
            'url': url,
            'keep_headers': 'true'
        }

        response = requests.get('https://api.scraperapi.com/', params=payload)
        if response.status_code != 200:
            print(f"Failed to fetch URL: {url} with status code: {response.status_code}")
            return None  # Return None if the request was not successful

        soup = BeautifulSoup(response.content, 'html.parser')
        print(f"Fetching URL: {url}")

        rows = soup.find_all('tr', class_='jobProfiles-table__row')
        if not rows:
            print(f"No rows found on page {page}. Ending pagination.")
            break

        for row in rows:
            designation_name = row.get('data-jobprofilename')
            salary_element = row.find('div', class_='avg-salary')
            if salary_element:
                salary = salary_element.find('span').text.strip()

                designations.append((designation_name, salary))

                # Check for exact match
                if designation_name in target_designations:
                    found_designations.add(designation_name)

        # Break the loop if all target designations are found
        if found_designations == set(target_designations):
            print("All target designations found. Stopping pagination.")
            break

        page += 1

    return designations

# Find the most similar designation from the fetched designations
def find_most_similar_designation(designations, target_designation, matched_designations):
    names = [designation[0] for designation in designations]
    closest_matches = difflib.get_close_matches(target_designation, names, n=1, cutoff=0.6)
    if closest_matches:
        for designation in designations:
            if designation[0] == closest_matches[0] and designation[0] not in matched_designations:
                matched_designations.add(designation[0])
                return designation
    return None

# Main function to integrate both functionalities
def main():
    target_designations = ['Data Scientist','Financial Analyst','Product Manager','Risk Analyst']  # Replace with your target designations

    # DataFrame to store results
    columns = ['Company Name'] + [f'Role{i+1}' for i in range(len(target_designations))] + [f'SalaryRole{i+1}' for i in range(len(target_designations))]
    results_df = pd.DataFrame(columns=columns)

    # List to store unsuccessful company names
    unsuccessful_companies = []

    for index, row in filtered_df.iterrows():
        company_name = row[target_column]
        search_url = perform_action(company_name)
        print(f"Fetching data for: {company_name}")
        print(f"Search URL: {search_url}")

        designations = fetch_designations(search_url, target_designations)
        if designations is None:
            unsuccessful_companies.append(company_name)
            continue

        matched_designations = set()
        company_results = {'Company Name': company_name}

        for i, target_designation in enumerate(target_designations):
            most_similar_designation = find_most_similar_designation(designations, target_designation, matched_designations)

            if most_similar_designation:
                company_results[f'Role{i+1}'] = most_similar_designation[0]
                company_results[f'SalaryRole{i+1}'] = most_similar_designation[1]
                print(f"Target designation: {target_designation}")
                print(f"Most similar designation: {most_similar_designation[0]}")
                print(f"Salary: {most_similar_designation[1]}")
                print()
            else:
                company_results[f'Role{i+1}'] = 'Not Found'
                company_results[f'SalaryRole{i+1}'] = 'Not Found'
                print(f"No similar designation found for: {target_designation}")
                print()

        results_df = pd.concat([results_df, pd.DataFrame([company_results])], ignore_index=True)

    # Save the results to a CSV file
    results_df.to_csv('designation_salaries3.csv', index=False)

    # Save the unsuccessful company names to another CSV file
    pd.DataFrame(unsuccessful_companies, columns=['Company Name']).to_csv('unsuccessful_companies3.csv', index=False)

if __name__ == "__main__":
    main()
