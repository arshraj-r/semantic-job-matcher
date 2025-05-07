import pandas as pd
from rank_bm25 import BM25Okapi
import pandas as pd
import re
import pickle


def preprocess_text(text):
    return re.findall(r"\w+", text.lower())

def build_bm25(df, text_column):
    tokenized_corpus = df[text_column].dropna().apply(preprocess_text).tolist()
    return BM25Okapi(tokenized_corpus), tokenized_corpus

def retrieve_bm25(query, bm25, metadata, text_column, k=5):
    tokenized_query = preprocess_text(query)
    scores = bm25.get_scores(tokenized_query)
    top_k_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
    return metadata.iloc[top_k_indices], [scores[i] for i in top_k_indices]

def score_jds_with_bm25(df, str_skills, text_column="jd"):
    bm25, tokenized_corpus = build_bm25(df, text_column)
    query = str_skills
    tokenized_query = preprocess_text(query)
    scores = bm25.get_scores(tokenized_query)

    # Add scores to the DataFrame
    df = df.copy()
    df["score"] = scores
    return df


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