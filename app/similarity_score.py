

import numpy as np
from sentence_transformers import SentenceTransformer, util
import matplotlib.pyplot as plt
import seaborn as sns

# Check if CUDA is available
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Using device: {device}")

model = SentenceTransformer('all-MiniLM-L6-v2', device=device)


def similarity_score_calculator(cv_text, jd_text,heatmap_path=None,model=model):
    cv_sentences = [sentence.strip() for sentence in cv_text.strip().split('\n') if sentence.strip()]
    jd_sentences = [sentence.strip() for sentence in jd_text.strip().split('\n') if sentence.strip()]
    cv_embeddings = model.encode(cv_sentences, convert_to_tensor=True, device=device)
    jd_embeddings = model.encode(jd_sentences, convert_to_tensor=True, device=device)
    similarity_matrix = util.cos_sim(cv_embeddings, jd_embeddings).cpu().numpy()
    
    if heatmap_path:

            plt.figure(figsize=(30, 18))
            sns.heatmap(similarity_matrix, annot=True, cmap="YlGnBu", xticklabels=jd_sentences, yticklabels=cv_sentences)
            plt.title("CV vs JD Similarity Heatmap")
            plt.xlabel("Job Description Sentences")
            plt.ylabel("CV Sentences")
            plt.xticks(rotation=45, ha='right')
            plt.yticks(rotation=0)
            plt.tight_layout()
            print("saving the heatmap as :{heatmap_path}")
            plt.savefig(heatmap_path)
        
    mean_all = similarity_matrix.mean()
    mean_best_jd = similarity_matrix.max(axis=0).mean()
    mean_best_cv = similarity_matrix.max(axis=1).mean()
    # k = 5
    # top_k_mean = np.sort(similarity_matrix.flatten())[-k:].mean()
    final_score = (mean_best_jd + mean_best_cv) / 2

    return mean_all,mean_best_jd,mean_best_cv,final_score