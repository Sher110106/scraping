import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


base_url = "https://in.indeed.com/jobs"
query = "developer"
location = "Bangalore, Karnataka"
no_of_pages = 10


with open("./jobs.csv", mode='w', newline='') as file:
    writer = csv.writer(file, delimiter=',', lineterminator='\n')
    writer.writerow(['JOB_NAME', 'COMPANY', 'LOCATION', 'POSTED'])

chrome_options = Options()
driver = webdriver.Chrome(options=chrome_options)

for page in range(no_of_pages):
    url = f"{base_url}?q={query}&l={location.replace(' ', '+').replace(',', '%2C')}&start={str(page * 10)}"

    driver.get(url)
    time.sleep(5)

    job_listings = driver.find_elements(By.CLASS_NAME, 'job_seen_beacon')

    output_data = []

    for job in job_listings:
        try:
            company_location = job.find_element(By.CLASS_NAME, 'company_location')
            company_name = company_location.find_element(By.CSS_SELECTOR, 'span[data-testid="company-name"]').text
            job_location = company_location.find_element(By.CSS_SELECTOR, 'div[data-testid="text-location"]').text
            job_title_area = job.find_element(By.CLASS_NAME, "jobTitle")
            job_title = job_title_area.find_element(By.TAG_NAME, 'span').text

            job_metadata = job.find_element(By.CLASS_NAME, 'underShelfFooter')
            posted_date = job_metadata.find_element(By.CSS_SELECTOR, 'span[data-testid="myJobsStateDate"]').text



            job_data = [job_title, company_name, job_location, posted_date]
            output_data.append(job_data)

        except Exception as e:
            print(f"Error extracting job information: {e}")


    with open("./jobs.csv", mode='a', newline='') as file:
        writer = csv.writer(file, delimiter=',', lineterminator='\n')
        writer.writerows(output_data)

driver.quit()
