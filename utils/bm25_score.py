import pandas as pd
from rank_bm25 import BM25Okapi
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