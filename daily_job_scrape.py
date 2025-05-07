import pandas as pd
from utils.linkedin_scraper import   scrape_jobs_for_keywords,scrape_jd_from_url ,extract_and_save_jds
from utils.resume_parser import extract_text_from_resume  
from utils.similarity_score import  similarity_score_calculator
from utils.naukari_scrapper import scrape_naukari_jobs
from utils.naukari_scrapper import scrape_naukari_jobs
from utils.bm25_score import build_bm25, score_jds_with_bm25
import time
import re
import pickle

try:
    #linkedin scraping
    keywords=["LLM", "NLP", "Gen AI", "Data Scientist","Manager Gen AI"]
    jobs = scrape_jobs_for_keywords(job_keywords=keywords, location="Bengaluru", scroll_page=10)
    print(f"total jobs scraped are:{jobs.shape[0]}")
    jobs.to_csv("daily_jobs/linkedin_jobs.csv",index=False)
    #scraping jds
    df=pd.read_csv("daily_jobs/linkedin_jobs.csv")
    extract_and_save_jds(df)
except:
    print("error whith extracting linkedin jobs")

try:
    #scraping naukari jobs
    keywords=["LLM", "NLP", "Gen AI", "Data Scientist","Manager Gen AI"]
    jobs_df=scrape_naukari_jobs(keywords=keywords,location = "bengaluru", experience = 5)
    jobs_df.to_csv("daily_jobs/naukari_jobs_df.csv")
except:
    print("error with naukari jobs")


#bm25 score calculation

df_skills=pd.read_csv("resume/cv_skills_keywords.csv")
list_skills= df_skills["Keyword"].to_list()
str_skills=" ".join(list_skills)

CSV_PATH = "daily_jobs/jd_linkedin_output_.csv"           # Your CSV file
TEXT_COLUMN = "jd"                   # The column with text data
BM25_INDEX_PATH = "index/bm25_index.pkl"   # Where to save the BM25 object
METADATA_PATH = "index/bm25_metadata.pkl"  


# --- Load CSV ---
print("[INFO] Loading CSV...")
df = pd.read_csv(CSV_PATH)
df = df.dropna(subset=[TEXT_COLUMN])

# --- Build BM25 ---
print("[INFO] Building BM25 index...")
bm25, _ = build_bm25(df, TEXT_COLUMN)

# --- Save BM25 index ---
with open(BM25_INDEX_PATH, "wb") as f:
    pickle.dump(bm25, f)
print(f"[INFO] BM25 index saved to: {BM25_INDEX_PATH}")

# --- Save metadata (original DataFrame) ---
with open(METADATA_PATH, "wb") as f:
    pickle.dump(df, f)
print(f"[INFO] Metadata saved to: {METADATA_PATH}")


# Load BM25 index and metadata
with open(BM25_INDEX_PATH, "rb") as f:
    bm25 = pickle.load(f)

with open(METADATA_PATH, "rb") as f:
    metadata = pickle.load(f)

query = str_skills
scored_df = score_jds_with_bm25(df, str_skills)
scored_df.sort_values(by=["score"],ascending=False, inplace=True)
scored_df.to_csv("final_results_with_score.csv")
print("resuls saved to csv")