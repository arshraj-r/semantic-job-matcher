from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def scrape_linkedin_jobs(job_keywords, location="India", num_jobs_per_keyword=5):
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

if __name__ == "__main__":
    keywords = [
        "LLM Engineer",
        "Generative AI Engineer",
        "NLP Researcher",
        "Machine Learning Engineer",
        "AI Scientist",
        "Data Scientist"
    ]
    
    jobs = scrape_linkedin_jobs(job_keywords=keywords, location="India", num_jobs_per_keyword=3)

    for job in jobs:
        print(f"\n🔗 {job['title']} at {job['company']}")
        print(f"Keyword: {job['keyword']}")
        print(f"Link: {job['link']}")
        print(f"Description: {job['description'][:200]}...\n")