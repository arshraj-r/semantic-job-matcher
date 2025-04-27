from sentence_transformers import SentenceTransformer, util
import torch

def combine_resume_fields(info_dict):
    """
    Combines important fields from the resume into a single string.
    """
    fields = ['summary', 'experience', 'projects','skills']
    combined = []

    for field in fields:
        if field in info_dict and info_dict[field]:
            content = info_dict[field]
            if isinstance(content, list):
                combined.append(" ".join(content))
            else:
                combined.append(str(content))
    
    return " ".join(combined)


def score_all_jobs(cv_info: dict, jobs_df, model_name="all-MiniLM-L6-v2"):
    """
    Calculates similarity score between the CV and all job descriptions.

    Args:
        cv_info (dict): Extracted resume information.
        jobs_df (pd.DataFrame): DataFrame with a 'description' column.
        model_name (str): Model name from Sentence Transformers.

    Returns:
        pd.DataFrame: Original DataFrame with a new 'similarity_score' column.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"⚙️ Using device: {device}")

    model = SentenceTransformer(model_name, device=device)

    # Combine CV fields into a single string
    resume_text = combine_resume_fields(cv_info)

    # Encode resume and job descriptions
    resume_embedding = model.encode(resume_text, convert_to_tensor=True, device=device)
    job_embeddings = model.encode(jobs_df["description"].tolist(), convert_to_tensor=True, device=device)

    # Calculate cosine similarities
    similarity_scores = util.pytorch_cos_sim(resume_embedding, job_embeddings)[0]

    # Add scores to the DataFrame
    jobs_df = jobs_df.copy()
    jobs_df["similarity_score"] = [round(score.item(), 4) for score in similarity_scores]

    return jobs_df

if __name__=="__main__":
    print("__main__")
