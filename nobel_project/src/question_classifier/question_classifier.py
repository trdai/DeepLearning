import json
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import KNeighborsClassifier
import numpy as np
import os

class QuestionClassifier:
    def __init__(self, question_json, interview_csv, output_csv, k=3):
        self.question_json = question_json
        self.interview_csv = interview_csv
        self.output_csv = output_csv
        self.k = k
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # nhẹ, nhanh
        self.knn = None
        self.categories = []
        self.train_embeddings = None

    def load_training_data(self):
        with open(self.question_json, "r", encoding="utf-8") as f:
            all_categories = json.load(f)

        train_texts, train_labels = [], []
        for cat, questions in all_categories.items():
            for q in questions:
                train_texts.append(q)
                train_labels.append(cat)

        print(f">>Loaded {len(train_texts)} training samples across {len(all_categories)} categories")
        self.categories = sorted(list(all_categories.keys()))

        # Embedding
        self.train_embeddings = self.model.encode(train_texts, convert_to_numpy=True, show_progress_bar=True)

        # Train KNN
        self.knn = KNeighborsClassifier(n_neighbors=self.k, metric="cosine")
        self.knn.fit(self.train_embeddings, train_labels)

    def classify_interviews(self):
        df = pd.read_csv(self.interview_csv, sep=";", encoding="utf-8-sig")

        questions = df["Question"].astype(str).tolist()
        embeddings = self.model.encode(questions, convert_to_numpy=True, show_progress_bar=True)

        preds = self.knn.predict(embeddings)
        df["Predicted Category"] = preds

        # Save
        df.to_csv(self.output_csv, index=False, encoding="utf-8-sig", sep=";")
        print(f">>Saved classified interviews to {self.output_csv}")

if __name__ == "__main__":
    base_dir = "./input/processed"
    qc = QuestionClassifier(
        question_json=os.path.join(base_dir, "nobel_questions.json"),
        interview_csv=os.path.join(base_dir, "interviews.csv"),
        output_csv=os.path.join(base_dir, "interviews_classified.csv"),
        k=5
    )
    qc.load_training_data()
    qc.classify_interviews()
