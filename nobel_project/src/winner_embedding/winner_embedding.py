import pandas as pd
import numpy as np
import json
from sentence_transformers import SentenceTransformer

class WinnerEmbedding:
    def __init__(self, interview_classified_csv, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.interview_classified_csv = interview_classified_csv
        self.model = SentenceTransformer(model_name)
        self.embeddings = {}

    def build_embeddings(self):
        # Đọc file interviews_classified.csv (Question, Response, Author ID, Predicted Category)
        df = pd.read_csv(self.interview_classified_csv, sep=";")

        results = {}
        for _, row in df.iterrows():
            pid = str(row["Author ID"]).strip()
            cat = str(row["Predicted Category"]).strip()
            a = str(row["Response"]).strip()

            if not a:
                continue

            emb = self.model.encode(a)

            # Lưu nguyên vector từng câu trả lời
            if pid not in results:
                results[pid] = {}
            if cat not in results[pid]:
                results[pid][cat] = []
            results[pid][cat].append(emb.tolist())

        self.embeddings = results

    def save(self, output_path="./input/processed/winner_embeddings.json"):
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.embeddings, f, ensure_ascii=False, indent=2)
        print(f">> Saved embeddings at {output_path}")


if __name__ == "__main__":
    interview_classified_csv = "./input/processed/interviews_classified.csv"
    out_path = "./input/processed/winner_embeddings.json"

    we = WinnerEmbedding(interview_classified_csv)
    we.build_embeddings()
    we.save(out_path)
