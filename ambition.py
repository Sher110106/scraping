import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Initialize an empty DataFrame if not imported
try:
    from shop import df
except ImportError:
    df = pd.DataFrame(columns=['Company Name', 'Rating', 'Industry'])

base_URL = 'https://www.ambitionbox.com/list-of-companies?locations=chandil-jharkhand,karnaprayag-uttarakhand,karnah-jammu-and-kashmir&sortBy=popular'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US'
}

def soupFromUrl(scrapeUrl, HEADERS):
    try:
        req = requests.get(scrapeUrl, headers=HEADERS, timeout=10)
        req.raise_for_status()
        return BeautifulSoup(req.text, 'html.parser')
    except requests.RequestException as e:
        raise Exception(f'{e} - failed to scrape {scrapeUrl}')

def data_fetch(url, headers):
    global df
    nextUrl = url
    while nextUrl:
        company_names = []
        company_ratings = []
        company_industries = []
        try:
            print(f"Fetching URL: {nextUrl}")
            soup = soupFromUrl(nextUrl, headers)
        except Exception as e:
            print(e)
            break

        # Find company names
        for company_tag in soup.find_all('h2', class_=['companyCardWrapper__companyName', 'companyCardWrapper__companyName--m8']):
            company_names.append(company_tag.get_text(strip=True))

        # Find company ratings
        for company_rating in soup.find_all('span', class_='companyCardWrapper__companyRatingValue'):
            company_ratings.append(company_rating.get_text(strip=True))

        # Find industry information
        for industry_tag in soup.find_all('span', class_='companyCardWrapper__interLinking'):
            industry_text = industry_tag.get_text(strip=True)
            industry = industry_text.split('|')[0].strip()  # Extract the first part before '|'
            company_industries.append(industry)

        # Create a temporary DataFrame for this page
        temp_df = pd.DataFrame({
            'Company Name': company_names,
            'Rating': company_ratings,
            'Industry': company_industries
        })

        # Append the temporary DataFrame to the main DataFrame
        df = pd.concat([df, temp_df], ignore_index=True)

        # Find the link to the next page
        nextHL = soup.select_one('a.page-nav-btn')
        nextUrl = nextHL['href'] if nextHL else None
        if nextUrl:
            nextUrl = "https://www.ambitionbox.com" + nextUrl  # Make sure the URL is absolute
        print("One page done")

        # Add a delay to avoid overloading the server
        time.sleep(2)

    # Save the data to a CSV file
    df.to_csv('company_data.csv', index=False)
    print("\nData saved to company_data.csv")
    print(f"Total companies scraped: {len(df)}")

# Example usage
data_fetch(base_URL, HEADERS)
