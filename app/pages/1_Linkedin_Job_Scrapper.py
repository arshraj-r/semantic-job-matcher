import streamlit as st
import pandas as pd
from resume_parser import extract_text_from_resume  # Your existing CV parser
from linkedin_scraper import scrape_jobs_for_keywords  # Your existing job scraping function

st.set_page_config(page_title="Semantic Job Matcher", layout="wide")
st.title("🔍 Semantic Job Matcher")

st.markdown("Upload your resume and we'll match you with jobs from LinkedIn based on extracted information.")

# === Upload Resume ===
resume_file = st.file_uploader("Upload your resume (PDF/DOCX):", type=["pdf", "docx"])

if resume_file is not None:
    with open("uploaded_cv.pdf", "wb") as f:
        f.write(resume_file.read())

    st.success("✅ Resume uploaded successfully.")
    extracted_info = extract_text_from_resume("uploaded_cv.pdf")
    # === Extract Information ===

    # === Choose Job Search Parameters ===
    st.subheader("🔍 Job Search")
    location = st.text_input("Enter location to search jobs in:", value="India")
    keywords_input = st.text_input("Enter job keywords (comma-separated):", value="LLM, GenAI, NLP")
    keywords = [kw.strip() for kw in keywords_input.split(",") if kw.strip()]
    scroll_page = st.slider("Page Scrolls:", 1, 10, 3)

    if st.button("Find Matching Jobs"):
        with st.spinner("Scraping LinkedIn for jobs..."):
            jobs = scrape_jobs_for_keywords(job_keywords=keywords, location=location, scroll_page=scroll_page)
            st.write(f"Total number of jobs found are :{jobs.shape[0]}")
            csv = jobs.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download job matches as CSV",
                data=csv,
                file_name='job_matches.csv',
                mime='text/csv',
            )

else:
    st.info("👆 Please upload a resume to begin.")
