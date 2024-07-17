import requests
from bs4 import BeautifulSoup
import difflib


def fetch_designations(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    designations = []

    for row in soup.find_all('tr', class_='jobProfiles-table__row'):
        designation_name = row['data-jobprofilename']
        salary_element = row.find('div', class_='avg-salary')
        if salary_element:
            salary = salary_element.find('span').text.strip()
            designations.append((designation_name, salary))

    return designations


def find_most_similar_designation(designations, target_designation):
    names = [designation[0] for designation in designations]
    closest_matches = difflib.get_close_matches(target_designation, names, n=1, cutoff=0.6)
    if closest_matches:
        for designation in designations:
            if designation[0] == closest_matches[0]:
                return designation
    return None


def main():
    url = 'https://example.com/salaries'  # Replace with the actual URL
    target_designation = 'Project Coordinator'  # Replace with the target designation

    designations = fetch_designations(url)
    most_similar_designation = find_most_similar_designation(designations, target_designation)

    if most_similar_designation:
        print(f"Most similar designation: {most_similar_designation[0]}")
        print(f"Salary: {most_similar_designation[1]}")
    else:
        print("No similar designation found.")


if __name__ == "__main__":
    main()
