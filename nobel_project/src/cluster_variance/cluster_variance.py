import json
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min
from collections import deque
import pandas as pd

class ClusterVariance:
    def __init__(self, embedding_file, interview_classified_csv="./input/processed/interviews_classified.csv"):
        # Load embeddings: format expected: { pid: { category: [ [vec], [vec], ... ] } }
        with open(embedding_file, "r", encoding="utf-8") as f:
            self.embeddings = json.load(f)
        # Load original classified csv (to get the raw Response text and Author ID / Predicted Category)
        self.df = pd.read_csv(interview_classified_csv, sep=";", dtype=str, encoding="utf-8-sig")
        # normalize column names if needed
        self.df.columns = [c.strip() for c in self.df.columns]

    def compute_clusters(self, n_clusters=3):
        """
        Build cat_vectors by matching rows in interviews_classified.csv with vectors in self.embeddings.
        Assumes that winner_embeddings.json was created by iterating the same df in the same order,
        so we can pop vectors from per-(pid,cat) deque in sequence to align vectors with response strings.
        """
        # prepare per-(pid,cat) deque of vectors from embeddings
        emb_copy = {}
        for pid, cats in self.embeddings.items():
            emb_copy[pid] = {}
            for cat, vecs in cats.items():
                # ensure we have list of lists -> convert to deque of np.array
                emb_copy[pid][cat] = deque([np.array(v) for v in vecs])

        # Build cat_vectors by iterating original df rows to preserve alignment
        cat_vectors = {}  # cat -> list of tuples (vector(np.array), pid(str), answer_text(str))
        for idx, row in self.df.iterrows():
            pid = str(row.get("Author ID", "")).strip()
            cat = str(row.get("Predicted Category", "")).strip()
            ans = str(row.get("Response", "")).strip()

            if not pid or not cat or not ans:
                continue

            # If we have a vector available in emb_copy for this (pid,cat), pop it
            if pid in emb_copy and cat in emb_copy[pid] and len(emb_copy[pid][cat]) > 0:
                v = emb_copy[pid][cat].popleft()
                cat_vectors.setdefault(cat, []).append((v, pid, ans))
            else:
                # fallback: if no vector available (mismatch), skip or optionally handle
                # We'll skip to avoid incorrect mapping.
                # Optionally you could try to encode ans on the fly, but that is expensive.
                continue

        results = {}
        for cat, vec_info in cat_vectors.items():
            vectors = [v for v, _pid, _ans in vec_info]
            if len(vectors) == 0:
                continue

            arr = np.vstack(vectors)  # N x d

            k = n_clusters if len(arr) >= n_clusters else max(1, len(arr))
            kmeans = KMeans(n_clusters=k, random_state=0, n_init="auto").fit(arr)
            centers = kmeans.cluster_centers_

            # Tìm index gần nhất trong arr cho mỗi center
            closest_idx, _ = pairwise_distances_argmin_min(centers, arr)

            cluster_data = []
            for ci, center in enumerate(centers):
                idx_closest = int(closest_idx[ci])
                vec_nearest, pid_nearest, ans_nearest = vec_info[idx_closest]

                # Optionally compute intra-cluster statistics like avg distance, size:
                # cluster_member_mask = (kmeans.labels_ == ci)
                # cluster_size = int(cluster_member_mask.sum())
                # avg_dist = float(np.mean(np.linalg.norm(arr[cluster_member_mask] - center, axis=1)))

                cluster_data.append({
                    "center_vector": center.tolist(),
                    "nearest_author_id": pid_nearest,
                    "nearest_answer": ans_nearest,
                    # optional extras:
                    # "cluster_index": ci,
                    # "cluster_size": cluster_size,
                    # "avg_distance_to_center": avg_dist
                })

            results[cat] = {
                "num_samples": len(arr),
                "clusters": cluster_data
            }

        return results

    def save(self, output_path="./input/processed/cluster_centers.json", n_clusters=3):
        results = self.compute_clusters(n_clusters)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f">> Saved cluster centers at {output_path}")


if __name__ == "__main__":
    embedding_file = "./input/processed/winner_embeddings.json"
    out_path = "./input/processed/cluster_centers.json"
    classified_csv = "./input/processed/interviews_classified.csv"

    cv = ClusterVariance(embedding_file, classified_csv)
    cv.save(out_path, n_clusters=3)
