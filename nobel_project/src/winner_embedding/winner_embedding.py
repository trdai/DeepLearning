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
        # đọc file interviews_classified.csv (có Question, Response, Author ID, Predicted Category)
        df = pd.read_csv(self.interview_classified_csv, sep=";")

        results = {}
        for _, row in df.iterrows():
            pid = str(row["Author ID"]).strip()
            cat = str(row["Predicted Category"]).strip()
            a = str(row["Response"]).strip()

            if not a:
                continue

            emb = self.model.encode(a)

            if pid not in results:
                results[pid] = {}
            if cat not in results[pid]:
                results[pid][cat] = []
            results[pid][cat].append(emb)

        # gom trung bình vector cho mỗi (pid, cat)
        for pid in results:
            for cat in results[pid]:
                arr = np.vstack(results[pid][cat])
                results[pid][cat] = arr.mean(axis=0)

        self.embeddings = results

    def save(self, output_path="./input/processed/winner_embeddings.json"):
        serializable = {pid: {cat: vec.tolist() for cat, vec in cats.items()}
                        for pid, cats in self.embeddings.items()}
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(serializable, f, ensure_ascii=False, indent=2)
        print(f">> Saved embeddings at {output_path}")


if __name__ == "__main__":
    # input = output file của Task 4 (đã classify category cho từng Q&A)
    interview_classified_csv = "./input/processed/interviews_classified.csv"
    out_path = "./input/processed/winner_embeddings.json"

    we = WinnerEmbedding(interview_classified_csv)
    we.build_embeddings()
    we.save(out_path)
