from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import random
import requests
import os
import csv
import pandas as pd
import re

"""
This script extracts all academic profiles from the last faculty listed on King's People.
For each user, it retrieves their profile webpage and scans the content to count occurrences
of the honorary titles: "GBE", "DBE", "CBE", "OBE", and "MBE".

This script performs the following steps:

1. Prompt the user to input the total number of pages.
2. Retrieve all academic profile links from the King's People website and save them to a CSV file.
3. Read the saved CSV file and iterate through each profile link.
4. Scrape each profile webpage to check for the presence of the honorary titles:
   "GBE", "DBE", "CBE", "OBE", and "MBE".
5. Update the CSV file with the results, indicating whether each title was found on the corresponding page.

"""

# It didn't work
def get_page_account():
    
    page_account_url = "https://www.kcl.ac.uk/api/delivery/projects/website/entries/search?fields=entryTitle%2CemployeeTypes%2Ctitle%2CfirstName%2ClastName%2Csuffix%2CjobTitle%2CadditionalJobTitle%2CprofileImage%2CresearchInterests%2CsubjectAreas%2Chide%2CemployeeTypes%2Coverride%2Csys%2CorgUnits&linkDepth=2&orderBy=%5B%7B%22asc%22%3A%22lastName%22%7D%2C%7B%22asc%22%3A%22firstName%22%7D%5D&pageIndex=0&pageSize=15&where=%5B%7B%22field%22%3A%22sys.versionStatus%22%2C%22equalTo%22%3A%22published%22%7D%2C%7B%22field%22%3A%22sys.contentTypeId%22%2C%22equalTo%22%3A%22person%22%7D%2C%7B%22field%22%3A%22employeeTypes%5B%5D%22%2C%22in%22%3A%5B%22Academics%22%5D%7D%2C%7B%22field%22%3A%22orgUnits%5B%5D.sys.id%22%2C%22in%22%3A%5B%22e27c5a5f-1571-4833-bd5f-9e2ef6375080%22%2C%22affd3ae9-0923-43cd-8d88-f4171acf0043%22%5D%7D%2C%7B%22field%22%3A%22hide%22%2C%22equalTo%22%3Afalse%7D%5D"
    
    # post request
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "authority":"www.kcl.ac.uk",
        "content-type":"application/json; charset=utf-8"
    }
    
    response = requests.get(page_account_url, headers=headers)

    page_count=1
    if response.status_code == 200:
        data = response.json()
        page_count = data.get("pageCount", 1)
        print(f"The total page: {page_count}")
    else:
        print(f"Request fail: {response.status_code}")
    return page_count

def selium_config():
    # Configure Selenium options
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-blink-features=AutomationControlled")  # Bypass Selenium detection
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")  # Mimic a real browser
    options.add_argument("--disable-gpu")  # Optimization for certain systems
    options.add_argument("--no-sandbox")  # Required for some Linux environments
    options.add_argument("--disable-dev-shm-usage")  # Prevent memory issues on some systems
    return options
def gather_profile_links(page_count):
    # Target directory page URL
    directory_url = "https://www.kcl.ac.uk/people?nodeId=638a559d-ca13-4c1a-883c-4f088edaa252&entryId=75d774bb-0f99-4956-a17e-8a8d80226c29&employeeTypes=Academics&orgUnits=affd3ae9-0923-43cd-8d88-f4171acf0043%2C29033ef0-2319-4257-bdb5-3d4623e50c71%2Cd488a19c-be7a-4892-8b2e-a02a065b1446%2Ce27c5a5f-1571-4833-bd5f-9e2ef6375080%2C3631fc5d-39c8-42b7-997c-5adc780c968e%2Ca00a56a0-7727-49d8-a527-3b76af892d12%2C4d01cd5b-5da3-4a2e-a4ba-3c8f434b8e90&researchInterests="
    base_url = "https://www.kcl.ac.uk"
    

    # Keyword statistics
    

    # Configure Selenium options
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-blink-features=AutomationControlled")  # Bypass Selenium detection
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")  # Mimic a real browser
    options.add_argument("--disable-gpu")  # Optimization for certain systems
    options.add_argument("--no-sandbox")  # Required for some Linux environments
    options.add_argument("--disable-dev-shm-usage")  # Prevent memory issues on some systems

    # Start WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        for each_page in range(35,page_count):
            each_url = directory_url + '&pageIndex=' +str(each_page)
            print(f'each page url is :{each_url}')
            driver.get(each_url)
            time.sleep(random.uniform(3, 6))  # Random wait time to prevent detection

            # Simulate scrolling to load content
            body = driver.find_element("tag name", "body")
            for _ in range(3):  # Scroll 3 times
                body.send_keys(Keys.PAGE_DOWN)
                time.sleep(random.uniform(1, 3))  # Random delay

            # Simulate mouse movement
            action = ActionChains(driver)

            action.move_by_offset(random.randint(10, 30), random.randint(10, 30)).perform()

            # Get the page HTML
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            # Extract profile links
            profile_links = [base_url + a["href"] for a in soup.select("h3 a[href^='/people/']")]
            print(f"In the page of {each_page}, I found {len(profile_links)} profile links")
            write_csv(profile_links)

    finally:
        driver.quit()
    


def write_csv(all_profile_links):
    # Define the file path
    folder_path = "result"
    file_path = os.path.join(folder_path, "kcl_people_link.csv")

    # Ensure the result folder exists
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Remove duplicates from the current list
    all_profile_links = list(set(all_profile_links))

    # Read existing links from the file if it exists
    existing_links = set()
    if os.path.exists(file_path):
        with open(file_path, "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            existing_links = {row[0] for row in reader}

    # Filter out links that already exist in the file
    new_links = [link for link in all_profile_links if link not in existing_links]

    # Write only new links to the file
    if new_links:
        with open(file_path, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            for link in new_links:
                writer.writerow([link])
        print(f"Added {len(new_links)} new profile links to {file_path}")
    else:
        print("No new profile links to add.")


def compute_metrics(start_index=0):
    keywords = ["GBE", "DBE", "CBE", "OBE", "MBE"]
    csv_file = "result/kcl_people_link.csv"
    df = pd.read_csv(csv_file)

    options = selium_config()
    # Visit each profile page and check for keywords
    try:
        for i in range(start_index, len(df)):
            print(f'Processing data item {i}')
            profile_url = df.iloc[i, 0]
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            driver.get(profile_url)
            time.sleep(random.uniform(3, 6))  # Random wait time to prevent detection
    
            # Simulate scrolling to load content
            body = driver.find_element("tag name", "body")
            for _ in range(3):  # Scroll 3 times
                body.send_keys(Keys.PAGE_DOWN)
                time.sleep(random.uniform(1, 3))  # Random delay
    
            # Simulate mouse movement
            action = ActionChains(driver)
    
            action.move_by_offset(random.randint(10, 30), random.randint(10, 30)).perform()
    
            profile_html = driver.page_source
    
            profile_soup = BeautifulSoup(profile_html, "html.parser")
            profile_text = profile_soup.get_text()
    
            # Count occurrences of keywords and store profile link
            for keyword in keywords:
                if re.search(rf'\b{re.escape(keyword)}\b', profile_text):
                    df.at[i, keyword] = 1
                    print(f'The {profile_url} contains {keyword}')
                else:
                    df.at[i, keyword] = 0
            df.to_csv(csv_file, index=False)
            print(f"Processed: {profile_url}")
    finally:
        driver.quit()

    # Print final statistics
    print("\nFinal Statistics:")
    for keyword in keywords:
        count = df[keyword].sum()
        print(f"{keyword}: {count}")
        
if __name__ == '__main__':
    # currently it's not working
    # page_count=get_page_account()
    
    page_count=39
    # gather_profile_links(page_count)
    compute_metrics(start_index=0)
    




