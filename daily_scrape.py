import pandas as pd
from app.linkedin_scraper import   scrape_jobs_for_keywords
from app.resume_parser import extract_text_from_resume  
from app.similarity_score import  similarity_score_calculator
from app.naukari_scrapper import scrape_naukari_jobs


keywords=["LLM", "NLP", "Gen AI", "Data Scientist"]
jobs = scrape_jobs_for_keywords(job_keywords=keywords, location="Bengaluru", scroll_page=2)
jobs.to_csv("daily_jobs/linkedin_jobs_df.csv",index=False)

naukari_jobs_df=scrape_naukari_jobs(keywords, location = "bengaluru", experience = 5)
naukari_jobs_df.to_csv("daily_jobs/naukari_jobs_df.csv",index=False)