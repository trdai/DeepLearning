import pandas as pd
import numpy as np
import json
from sentence_transformers import SentenceTransformer

class WinnerEmbedding:
    def __init__(self, interview_csv, category_json, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.interview_csv = interview_csv
        self.category_json = category_json
        self.model = SentenceTransformer(model_name)
        self.embeddings = {}

    def load_data(self):
        # interviews: Q, Response, Author ID
        self.df = pd.read_csv(self.interview_csv, sep=";")
        # mapping câu hỏi → nhóm chủ đề
        with open(self.category_json, "r", encoding="utf-8") as f:
            self.categories = json.load(f)

    def build_embeddings(self):
        # đảo mapping: question_text -> category
        question2cat = {}
        for cat, questions in self.categories.items():
            for q in questions:
                question2cat[q] = cat

        results = {}

        for _, row in self.df.iterrows():
            q = str(row["Question"]).strip()
            a = str(row["Response"]).strip()
            pid = str(row["Author ID"]).strip()

            if q not in question2cat:
                continue  # bỏ qua nếu chưa map được câu hỏi
            cat = question2cat[q]

            # encode câu trả lời
            emb = self.model.encode(a)

            # lưu
            if pid not in results:
                results[pid] = {}
            if cat not in results[pid]:
                results[pid][cat] = []
            results[pid][cat].append(emb)

        # gom trung bình vector cho mỗi (pid, cat)
        for pid in results:
            for cat in results[pid]:
                arr = np.vstack(results[pid][cat])  # n × d
                results[pid][cat] = arr.mean(axis=0)  # 1 × d

        self.embeddings = results

    def save(self, output_path="./input/processed/winner_embeddings.json"):
        # convert np.array → list
        serializable = {pid: {cat: vec.tolist() for cat, vec in cats.items()}
                        for pid, cats in self.embeddings.items()}
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(serializable, f, ensure_ascii=False, indent=2)
        print(f">> Saved embeddings at {output_path}")

if __name__ == "__main__":
    interview_csv = "./input/processed/interviews.csv"
    category_json = "./input/processed/nobel_questions.json"
    out_path = "./input/processed/winner_embeddings.json"

    we = WinnerEmbedding(interview_csv, category_json)
    we.load_data()
    we.build_embeddings()
    we.save(out_path)
