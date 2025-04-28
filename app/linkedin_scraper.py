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
    # options.add_argument("--start-maximized")
    # options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--disable-notifications")
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



#below is old code for linkedin scrapper
def scrape_linkedin_jobs__archive(job_keywords, location="Bengaluru", num_jobs_per_keyword=5):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-notifications")
    options.add_argument("--headless")  # optionasl: remove this line if you want to see the browser

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    all_jobs = []

    for keyword in job_keywords:
        print(f"\n🔍 Searching for: {keyword}")
        query = keyword.replace(" ", "%20")
        loc = location.replace(" ", "%20")
        url = f"https://www.linkedin.com/jobs/search/?keywords={query}&location={loc}&f_TPR=r86400"  # last 24h jobs
        driver.get(url)

        time.sleep(5)  # allow dynamic content to load

        jobs_collected = 0
        job_links_seen = set()

        while jobs_collected < num_jobs_per_keyword:
            job_cards = driver.find_elements(By.CSS_SELECTOR, "a.base-card__full-link")

            for job_link in job_cards:
                link = job_link.get_attribute("href")
                if link in job_links_seen:
                    continue

                job_links_seen.add(link)
                driver.execute_script("window.open(arguments[0]);", link)
                driver.switch_to.window(driver.window_handles[1])

                try:
                    wait = WebDriverWait(driver, 10)

                    title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))).text
                    try:
                        company = driver.find_element(By.CSS_SELECTOR, ".topcard__org-name-link").text
                    except:
                        company = "N/A"

                    description = driver.find_element(By.CLASS_NAME, "description__text").text

                    all_jobs.append({
                        "keyword": keyword,
                        "title": title,
                        "company": company,
                        "description": description,
                        "link": link
                    })

                    jobs_collected += 1
                    print(f"✅ Collected {jobs_collected} for '{keyword}'")

                except Exception as e:
                    print("⚠️ Failed to parse job detail:", e)
                finally:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                if jobs_collected >= num_jobs_per_keyword:
                    break

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(4)

    driver.quit()
    return all_jobs


def scrape_linkedin_jobs_archive(job_keywords, location="India", num_jobs_per_keyword=5):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    all_jobs = []

    for keyword in job_keywords:
        print(f"\n🔍 Searching for: {keyword}")
        query = keyword.replace(" ", "%20")
        loc = location.replace(" ", "%20")
        url = f"https://www.linkedin.com/jobs/search/?keywords={query}&location={loc}"
        driver.get(url)

        time.sleep(3)

        jobs_collected = 0
        job_cards = driver.find_elements(By.CLASS_NAME, "job-card-container")

        while jobs_collected < num_jobs_per_keyword and len(job_cards) > 0:
            for card in job_cards:
                try:
                    job_link_element = card.find_element(By.CSS_SELECTOR, "a.job-card-list__title")
                    job_url = job_link_element.get_attribute("href")

                    job_link_element.click()
                    time.sleep(2)

                    job_title = driver.find_element(By.CLASS_NAME, "top-card-layout__title").text
                    company = driver.find_element(By.CLASS_NAME, "topcard__org-name-link").text
                    job_description = driver.find_element(By.CLASS_NAME, "description__text").text

                    all_jobs.append({
                        "keyword": keyword,
                        "title": job_title,
                        "company": company,
                        "description": job_description,
                        "link": job_url
                    })

                    jobs_collected += 1
                    if jobs_collected >= num_jobs_per_keyword:
                        break

                except Exception as e:
                    print("⚠️ Error reading job card:", e)
                    continue

            # Scroll to load more jobs
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            job_cards = driver.find_elements(By.CLASS_NAME, "job-card-container")

    driver.quit()
    return all_jobs