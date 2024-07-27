import pandas as pd
import requests
from bs4 import BeautifulSoup
import difflib
import json
import os
from google.colab import files

# Normalize and construct the search URL

# Fetch designations and salaries from a given URL
def fetch_designations(base_url, target_designations):
    designations = []
    page = 1
    found_designations = set()
    company_name = None
    max_pages = 80  # Set the pagination limit

    while len(found_designations) < len(target_designations) and page <= max_pages:
        url = f"{base_url}?page={page}"
        payload = {
            'api_key': '1a5f17fc33b7977bbee0a44f988444f7',
            'url': url,
            'keep_headers': 'true'
        }

        response = requests.get('https://api.scraperapi.com/', params=payload)
        if response.status_code != 200:
            print(f"Failed to fetch URL: {url} with status code: {response.status_code}")
            return None, None  # Return None if the request was not successful

        soup = BeautifulSoup(response.content, 'html.parser')
        print(f"Fetching URL: {url}")

        if company_name is None:
            company_tag = soup.find('p', class_='newHInfo__cNtxt')
            if company_tag:
                company_name = company_tag.text.strip()

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

    return company_name, designations

# Find the most similar designation from the fetched designations
def find_most_similar_designation(designations, target_designation, matched_designations):
    names = [designation[0] for designation in designations]
    closest_matches = difflib.get_close_matches(target_designation, names, n=1, cutoff=0.6)
    if closest_matches:
        for designation in designations:
            if designation[0] == closest_matches[0] and designation[0] not in matched_designations:
                matched_designations.add(designation[0])
                return designation

# Function to load cache
def load_cache():
    if os.path.exists('cache5.json'):
        with open('cache5.json', 'r') as f:
            return json.load(f)
    return {}

# Function to save cache
def save_cache(cache):
    with open('cache5.json', 'w') as f:
        json.dump(cache, f)

# Main function to integrate both functionalities
def main():
    target_designations = ['Software Engineer','Data Scientist','Project Manager','Product Manager']

    # Load cache
    cache = load_cache()

    # DataFrame to store results
    columns = ['Company Name'] + [f'Role{i + 1}' for i in range(len(target_designations))] + [f'SalaryRole{i + 1}' for i in range(len(target_designations))]
    results_df = pd.DataFrame(columns=columns)

    # List to store unsuccessful company names
    unsuccessful_companies = []

    # URL to process
    url = 'https://www.ambitionbox.com/salaries/hcl-technologies-salaries'

    # Check if results are in cache
    if url in cache:
        print(f"Using cached data for: {url}")
        company_results = cache[url]
    else:
        print(f"Fetching data for: {url}")

        company_name, designations = fetch_designations(url, target_designations)
        if designations is None:
            unsuccessful_companies.append(url)
        else:
            matched_designations = set()
            company_results = {'Company Name': company_name}

            for i, target_designation in enumerate(target_designations):
                most_similar_designation = find_most_similar_designation(designations, target_designation, matched_designations)

                if most_similar_designation:
                    company_results[f'Role{i + 1}'] = most_similar_designation[0]
                    company_results[f'SalaryRole{i + 1}'] = most_similar_designation[1]
                    print(f"Target designation: {target_designation}")
                    print(f"Most similar designation: {most_similar_designation[0]}")
                    print(f"Salary: {most_similar_designation[1]}")
                    print()
                else:
                    company_results[f'Role{i + 1}'] = 'Not Found'
                    company_results[f'SalaryRole{i + 1}'] = 'Not Found'
                    print(f"No similar designation found for: {target_designation}")
                    print()

            # Cache the results
            cache[url] = company_results
            save_cache(cache)

    results_df = pd.concat([results_df, pd.DataFrame([company_results])], ignore_index=True)

    # Save results
    results_df.to_csv('designation_salaries.csv', index=False)
    pd.DataFrame(unsuccessful_companies, columns=['Company Name']).to_csv('unsuccessful_companies.csv', index=False)

    # Download the results
    files.download('designation_salaries.csv')
    files.download('unsuccessful_companies.csv')
    files.download('cache5.json')

if __name__ == "__main__":
    main()
