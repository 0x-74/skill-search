import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from dotenv import load_dotenv
import login 

load_dotenv()

def get_job_cards(driver):
    wait = WebDriverWait(driver, 30)
    time.sleep(3)
    scrollable_element = driver.execute_script('''
            function isVerticallyScrollable(element) {
                const style = window.getComputedStyle(element);
                const overflowY = style.overflowY;
                const overflowX = style.overflowX;
                const verticalScroll = (overflowY === 'auto' || overflowY === 'scroll');
                const horizontalBlocked = !(overflowX === 'auto' || overflowX === 'scroll');
                const canScrollVertically = element.scrollHeight > element.clientHeight;
                return verticalScroll && horizontalBlocked && canScrollVertically;
            }
            let allElements = Array.from(document.querySelectorAll('*'));
            return allElements.filter(el => isVerticallyScrollable(el));
        ''')
    scrollable_element = scrollable_element[0]
    for scroll_pos in [4, 2.2, 2, 1.6, 1.1]:
        driver.execute_script(f"arguments[0].scrollTop = arguments[0].scrollHeight / {scroll_pos};", scrollable_element)
        time.sleep(1)
    job_cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.job-card-container[data-job-id]")))
    return job_cards

def get_job_descriptions(job_cards, driver):
    descriptions = []
    for card in job_cards:
        try:
            driver.execute_script("arguments[0].scrollIntoView();", card)
            card.click()
            time.sleep(2)  # Allow page to load

            desc_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'jobs-search__job-details--wrapper'))
            )
            descriptions.append(desc_element.text.strip())
        except Exception as e:
            print(f"Skipping job due to error: {e}")
            continue
    return descriptions

def click_next_page(driver):
    try:
        wait = WebDriverWait(driver, 3)
        button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="View next page"]')))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
        button.click()
        time.sleep(2)
        return False  # Not the last page
    except Exception as e:
        print(f'Already on the last page or button not clickable.{e}')
        return True

if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options)
                        
    email = os.getenv('EMAIL')
    password = os.getenv('PASSWORD')
    all_descriptions = []
    try:
        login(driver, email, password)
        driver.get('https://www.linkedin.com/jobs/search/?currentJobId=4196452936&f_PP=105282602&f_WT=3%2C2&keywords=engineer&origin=JOB_SEARCH_PAGE_JOB_FILTER&sortBy=R')

        on_last_page = False
        while not on_last_page:
            job_cards = get_job_cards(driver)
            job_descriptions = get_job_descriptions(job_cards, driver)
            all_descriptions.extend(job_descriptions)
            on_last_page = click_next_page(driver)
            time.sleep(3)

        # Write raw descriptions to a text file
        with open('job_descriptions.txt', 'w', encoding='utf-8') as f:
            for desc in all_descriptions:
                f.write(desc + '\n\n' + '-'*80 + '\n\n')

        print(f"Saved {len(all_descriptions)} job descriptions to job_descriptions.txt ✅")

    finally:
        print("Closing browser...")