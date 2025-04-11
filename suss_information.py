from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import time
import random
import os
import csv
import pandas as pd
import re
import sys

"""
# This script scrapes course information from SUSS:
# URL example: https://www.suss.edu.sg/courses/course-finder?page=1&area=all&schools=all&t=Programmes&types=&sort=date&keyword4ProgrammeCourse=&keyword=

# This script is responsible for scraping data from a single page only.
# It is designed to be executed repeatedly for different page numbers,
# which are passed in as arguments from an external shell script (run_suss_information.sh).

# The benefit of this architecture is that it helps to avoid anti-scraping mechanisms:
# - Each execution loads only one page.
# - Timing between requests is controlled by the shell script.
# - Human-like behavior is simulated within this script (e.g., scrolling, mouse movement).

It's run through run_suss_information.sh
Finally, the data in these CSV files is visualized using the suss_data_analysis.ipynb notebook.
"""
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
    pre_url = "https://www.suss.edu.sg/courses/course-finder?page="
    after_url = "&area=all&schools=all&t=Courses&types=modular-undergraduate-course,modular-graduate-course,certificate-course,short-course,skillsfuture-series,ihl-micro-credentials&sort=date&schemes=&funding=&language=tamil&learning=&startDate=&keyword4ProgrammeCourse="
    
    # Configure Selenium options
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")  # Bypass Selenium detection
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")  # Mimic a real browser
    options.add_argument("--disable-gpu")  # Optimization for certain systems
    options.add_argument("--no-sandbox")  # Required for some Linux environments
    options.add_argument("--disable-dev-shm-usage")  # Prevent memory issues on some systems
    options.add_argument("accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8")
    options.add_argument("accept-language=en-US,en;q=0.9")
    options.add_argument("sec-fetch-mode=navigate")
    options.add_argument("upgrade-insecure-requests=1")

    # Start WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            })
        """
    })

    try:
        # for each_page in range(1, page_count):
        each_url = pre_url + str(page_count) + after_url
        print(f'each page url is :{each_url}')
        driver.get(each_url)
        time.sleep(random.uniform(2, 6))  # Random wait time to prevent detection
        
        # Simulate scrolling to load content
        body = driver.find_element(By.TAG_NAME, "body")

        scroll_times = random.randint(3, 6)
        for _ in range(scroll_times):
            body.send_keys(Keys.DOWN)
            time.sleep(random.uniform(0.5, 2))

        # Simulate mouse movement
        action = ActionChains(driver)

        action.move_by_offset(random.randint(10, 30), random.randint(10, 30)).perform()

        # Get the page HTML
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        items = soup.select("div.programme-item")

        results = []
        for item in items:
            title = item.get("data-title", "").strip()
            url_suffix = item.get("data-url", "")
            full_url = "https://www.suss.edu.sg" + url_suffix

            code_tag = item.select_one("span.course-code")
            course_code = code_tag.get_text(strip=True) if code_tag else ""

            types = [li.get_text(strip=True) for li in item.select("ul.programme-item__l-programme li")]

            featured_div = item.select_one("div.label-item.featured")
            is_featured = featured_div is not None

            def extract_info(label):
                span = item.find("span", string=lambda s: s and label in s)
                return span.find_next_sibling(text=True).strip() if span else ""

            app_open = extract_info("Applications Open")
            app_close = extract_info("Applications Close")
            intake = extract_info("Next Available Intake")
            duration = extract_info("Duration")
            fees = extract_info("Fees")
            interest = extract_info("Area of Interest")

            results.append({
                "title": title,
                "code": course_code,
                "url": full_url,
                "types": ", ".join(types),
                "featured": is_featured,
                "applications_open": app_open,
                "applications_close": app_close,
                "intake": intake,
                "duration": duration,
                "fees": fees,
                "area_of_interest": interest
            })
        write_results_to_csv(results)
    
    finally:
        driver.quit()

def write_results_to_csv(results):
    # Define the column headers
    headers = [
        "title", "code", "url", "types", "featured",
        "applications_open", "applications_close",
        "intake", "duration", "fees", "area_of_interest"
    ]
    unique_keys = ["title", "code", "url", "types", "featured", "area_of_interest"]

    folder_path = "result"
    filename = os.path.join(folder_path, "suss_courses.csv")
    os.makedirs(folder_path, exist_ok=True)

    # Convert scraped results to DataFrame
    new_df = pd.DataFrame(results)

    if not os.path.exists(filename):
        new_df.to_csv(filename, index=False, columns=headers)
        print(f"✅ Created new CSV with {len(new_df)} records.")
    else:
        
        old_df = pd.read_csv(filename)
    
        
        for col in unique_keys:
            new_df[col] = new_df[col].astype(str)
            old_df[col] = old_df[col].astype(str)
    
        mask = ~new_df[unique_keys].apply(tuple, axis=1).isin(old_df[unique_keys].apply(tuple, axis=1))
        to_append = new_df[mask]
    
        if not to_append.empty:
            to_append.to_csv(filename, mode='a', header=False, index=False)
            print(f"Appended {len(to_append)} new records.")
        else:
            print("No new records to add.")

if __name__ == '__main__':
    
    # page_count = 69
    page_count = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    gather_profile_links(page_count)