import json
import numpy as np

class ClusterVariance:
    def __init__(self, embedding_file):
        with open(embedding_file, "r", encoding="utf-8") as f:
            self.embeddings = json.load(f)

    def compute_variance(self):
        # gom theo từng category
        cat_vectors = {}
        for pid, cats in self.embeddings.items():
            for cat, vec in cats.items():
                v = np.array(vec)
                if cat not in cat_vectors:
                    cat_vectors[cat] = []
                cat_vectors[cat].append(v)

        results = {}
        for cat, vectors in cat_vectors.items():
            arr = np.vstack(vectors)  # N × d
            mean_vec = arr.mean(axis=0)
            var = arr.var(axis=0).mean()  # variance trung bình trên các chiều
            results[cat] = {
                "variance": float(var),
                "mean_vector": mean_vec.tolist(),
                "num_winners": len(vectors)
            }

        return results

    def save(self, output_path="./input/processed/cluster_variance.json"):
        results = self.compute_variance()
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f">> Saved variance results at {output_path}")

if __name__ == "__main__":
    embedding_file = "./input/processed/winner_embeddings.json"
    out_path = "./input/processed/cluster_variance.json"

    cv = ClusterVariance(embedding_file)
    cv.save(out_path)
