import pandas as pd
from app.linkedin_scraper import   scrape_jobs_for_keywords
from app.resume_parser import extract_text_from_resume  
from app.similarity_score import  similarity_score_calculator

location="Bengaluru"
keywords=["LLM", "NLP", "Gen AI", "Data Scientist"]
scroll_page=2
# jobs = scrape_jobs_for_keywords(job_keywords=keywords, location=location, scroll_page=scroll_page)
# jobs.to_csv("daily_jobs/jobs_df.csv",index=False)

jobs=pd.read_csv("daily_jobs/jobs_df.csv")
jobs=jobs[:10]
print(f"running code for: {jobs.shape[0]}")
for i in range(jobs.shape[0]):
    link=jobs["link"].values[i]
