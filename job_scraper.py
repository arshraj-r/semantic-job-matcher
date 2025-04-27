from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def scrape_linkedin_jobs(job_keywords, location="Bengaluru", num_jobs_per_keyword=5):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-notifications")
    # options.add_argument("--headless")  # optional: remove this line if you want to see the browser

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


if __name__ == "__main__":
    keywords = [
        "LLM Engineer",
        "Generative AI",
        "NLP Researcher"
    ]

    jobs = scrape_linkedin_jobs(job_keywords=keywords, location="India", num_jobs_per_keyword=2)

    for job in jobs:
        print(f"\n🔗 {job['title']} at {job['company']}")
        print(f"Keyword: {job['keyword']}")
        print(f"Link: {job['link']}")
        print(f"Description: {job['description'][:200]}...\n")
