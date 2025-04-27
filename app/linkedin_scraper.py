from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import re
import time
import pandas as pd

def extract_sections_from_jd(text):
    # Define possible section headers (case-insensitive)
    section_titles = [
        "Job Description",
        "Job Responsibilities",
        "Required Qualifications, Capabilities, And Skills",
        "Preferred Qualifications, Capabilities, And Skills",
        "ABOUT US",
        "About The Team"
    ]
    
    pattern = r"(?i)(" + "|".join(map(re.escape, section_titles)) + r")\n+"
    
    parts = re.split(pattern, text)
    
    jd_dict = {}
    i = 1  
    while i < len(parts) - 1:
        key = parts[i].strip()
        value = parts[i+1].strip()
        jd_dict[key] = value
        i += 2
    
    return jd_dict

def scrape_jd_from_url(url:str):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') 
    options.add_argument('--disable-gpu')
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    
    try:
        wait = WebDriverWait(driver, 5)
        popup = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.modal__overlay.modal__overlay--visible")))
        print("Popup detected. Clicking outside to dismiss.")
        ActionChains(driver).move_by_offset(50, 50).click().perform()
    except Exception as e:
        print("Popup not detected. Continuing...")  
        
    try:
        show_more_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.show-more-less-html__button--more")))
        show_more_button.click()
        print("Clicked 'Show more' button.")
    except Exception as e:
        print("No 'Show more' button found or already expanded.")
    
    jd_div = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "show-more-less-html__markup")))
    job_description = jd_div.text

    return job_description



def scrape_jobs_for_keywords(job_keywords, location="India", scroll_page=5):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-notifications")
    options.add_argument("--headless")  # optional: remove this line if you want to see the browser
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    all_jobs_df=pd.DataFrame()
    for keyword in job_keywords:
        print(f"\n🔍 Searching for: {keyword}")
        query = keyword.replace(" ", "%20")
        loc = location.replace(" ", "%20")
        url = f"https://www.linkedin.com/jobs/search/?keywords={query}&location={loc}&f_TPR=r86400"  # last 24h jobs
        # url = f"https://www.linkedin.com/jobs/search/?keywords={query}&location={loc}" 
        driver.get(url)
        time.sleep(4)
        ActionChains(driver).move_by_offset(50, 50).click().perform()
        
        for _ in range(scroll_page):  # You can increase the range for more scrolls
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2) 
        job_list = driver.find_element(By.CLASS_NAME, "jobs-search__results-list")
        job_cards = job_list.find_elements(By.TAG_NAME, "li")
        print(f"Total job cards found for keyword {keyword} are:{len(job_cards)}")
        job_urls = []
        jobs = []
        for card in job_cards:
            try:
                title =card.find_element(By.CLASS_NAME, "base-search-card__title").text.strip()
                company = card.find_element(By.CLASS_NAME, "base-search-card__subtitle").find_element(By.TAG_NAME, "a").text.strip()
                link =card.find_element(By.CLASS_NAME, "base-card__full-link").get_attribute("href")
                jobs.append({"title": title, "company": company, "link": link})
            
                #the below code also works for extracting links
                link = card.find_element(By.TAG_NAME, "a").get_attribute("href")
                job_urls.append(link)
            except:
                pass 
        df=pd.DataFrame(jobs)
        df["keyword"]=keyword
        all_jobs_df = pd.concat([all_jobs_df, df], ignore_index=True)

    driver.quit()
    return all_jobs_df

