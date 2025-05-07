from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
import time
import pandas as pd


def extract_job_details_from_card(job_element):
    try:
        title_element = job_element.find_element(By.CSS_SELECTOR, 'h2 > a.title')
        title = title_element.text
        job_link = title_element.get_attribute('href')

        company = job_element.find_element(By.CSS_SELECTOR, 'a.comp-name').text
        experience = job_element.find_element(By.CSS_SELECTOR, 'span.expwdth').text
        location = job_element.find_element(By.CSS_SELECTOR, 'span.locWdth').text
        description = job_element.find_element(By.CSS_SELECTOR, 'span.job-desc').text
        post_date = job_element.find_element(By.CSS_SELECTOR, 'span.job-post-day').text

        # Extract skills/tags
        skill_elements = job_element.find_elements(By.CSS_SELECTOR, 'ul.tags-gt > li')
        skills = [skill.text for skill in skill_elements]

        return {
            'Title': title,
            'Company': company,
            'Experience': experience,
            'Location': location,
            'Description': description,
            'Posted': post_date,
            'Skills': ', '.join(skills),
            'Link': job_link
        }
    except Exception as e:
        print(f"Error extracting job details: {e}")
        return None
        




def scrape_naukari_jobs(keywords, location = "bengaluru", experience = 5):        
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless') 
    options.add_argument('--disable-gpu')
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    all_jobs_df=pd.DataFrame()
    
    for keyword in keywords:
        url = f"https://www.naukri.com/{keyword}-jobs-in-{location}?experience={str(experience)}"
        driver.get(url)
        # Wait until job elements are present
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "srp-jobtuple-wrapper"))
            )
            print("Job elements loaded.")
        except:
            print("Job elements not found or took too long to load.")
        
        # Scroll to trigger more content load
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # Now get job cards
        jobs = driver.find_elements(By.CLASS_NAME, 'srp-jobtuple-wrapper')
        print(f"Found {len(jobs)} job elements.")
    
        #inspect html content for each job card
        # job=jobs[0]
        # print(job.get_attribute('innerHTML'))
    
        jobs_data = []
        for job in jobs:
            try:
                job_data=extract_job_details_from_card(job)
                jobs_data.append(job_data)
            except Exception as e:
                print(f"Error: {e}")
        jobs_df=pd.DataFrame(jobs_data)
        all_jobs_df = pd.concat([all_jobs_df, jobs_df], ignore_index=True)
    driver.quit()
    return all_jobs_df

if __name__=="__main__":
    keywords=["NLP","LLM","Gen AI"]
    all_jobs_df=scrape_naukari_jobs(keywords=keywords,location = "bengaluru", experience = 5)
    print(f"total jobs scraped are:{all_jobs_df.shape[0]}")