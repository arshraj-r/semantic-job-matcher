import streamlit as st
import pandas as pd
from linkedin_scraper import scrape_jd_from_url
from resume_parser import extract_text_from_resume,extract_resume_sections
from similarity_score import similarity_score_calculator
from PIL import Image

st.set_page_config(page_title="Job Description Scraper and Matcher", layout="wide")
st.title("🔍 Job Description Scraper and Matcher")

# === Upload Resume ===
resume_file = st.file_uploader("Upload your resume (PDF/DOCX):", type=["pdf", "docx"])

if resume_file is not None:
    with open("uploaded_cv.pdf", "wb") as f:
        f.write(resume_file.read())

    

    extracted_info = extract_text_from_resume("uploaded_cv.pdf")
    st.success("✅ Resume upload and information extraction successful")
    # st.write(extracted_info)

url = st.text_input("Enter the job listing URL:")
if st.button('Scrape JD and Calculate Similarity Score'):
    if url:
        job_description=scrape_jd_from_url(url)
        st.success("✅ JD scraped successfully.")
        if job_description:
                st.subheader("Similarity Results for CV vs JD")
                # st.write(job_description)
                mean_all,mean_best_jd,mean_best_cv,final_score=similarity_score_calculator(extracted_info,job_description,heatmap_path="similarity_plot.jpg")
                st.write(f"Mean Similarity (all pairs): {mean_all:.3f}")
                st.write(f"Mean of Best Matches per CV Sentence: {mean_best_cv:.3f}")
                st.write(f"Mean of Best Matches per JD Sentence: {mean_best_jd:.3f}")
                st.write(f"Final Symmetric Matching Score: {final_score:.3f}")

                image_path = "similarity_plot.jpg"
                image = Image.open(image_path)

                # Display the image in the app
                st.image(image, caption="Similarity Heatmap", use_container_width=True)
                with open(image_path, "rb") as file:
                   img_bytes = file.read()
                st.download_button(
                    label="📥 Download Heatmap",
                    data=img_bytes,
                    file_name="similarity_heatmap.jpg",
                    mime="image/jpeg"
)

