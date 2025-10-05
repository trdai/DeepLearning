import os
import json
import re
from docx import Document
from pathlib import Path
import pandas as pd

class WordInfor:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.all_people = []

    def export_interviews_to_csv(self, output_csv):
        rows = []
        for person in self.all_people:
            pid = person.get("id", "")
            for qa in person.get("Interview", []):
                rows.append({
                    "Question": qa.get("question", ""),
                    "Response": qa.get("answer", ""),
                    "Author ID": pid
                })

        df = pd.DataFrame(rows, columns=["Question", "Response", "Author ID"])
        df.to_csv(output_csv, index=False, encoding="utf-8-sig", sep=";")

    def parse_word_files(self):

        # Gom tất cả người
        for file in os.listdir(self.folder_path):
            if file.endswith(".docx"):
                #person = self._parse_word_file(self.folder_path + "/" + file)
                self._parse_word_file(self.folder_path + "/" + file)

        
        # Xuất JSON
        output_file = self.folder_path + "/../processed/nobel_people.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.all_people, f, ensure_ascii=False, indent=2)
   
    def _parse_word_file(self, path):
        doc = Document(path)

        current = None
        last_question = None

        for table in doc.tables:
            for row in table.rows:
                cells = [c.text.strip() for c in row.cells]
                if len(cells) < 2:
                    continue

                key, value = cells[0], cells[1]

                # Khi gặp ID mới -> bắt đầu 1 người mới
                if key.lower().startswith("id"):
                    # lưu người cũ nếu có
                    if current:
                        self.all_people.append(current)
                    current = {"id": value, "Interview": []}
                    last_question = None
                    continue

                if current is None:
                    continue  # bỏ qua nếu chưa có ID nào

                # Nếu là Q (question)
                if key.strip().lower().startswith("q"):
                    last_question = value
                # Nếu không có key (hoặc key không phải Q) nhưng vừa có question trước đó => đây là answer
                elif last_question:
                    current["Interview"].append({
                        "question": last_question,
                        "answer": value
                    })
                    last_question = None
                else:
                    if key == "Interview":
                        continue
                    # Field thông thường
                    current[key] = value

        # Lưu người cuối cùng
        if current:
            self.all_people.append(current)

if __name__ == "__main__":
    # Define word infor
    word_folder = "./input/word"
    word = WordInfor(word_folder)
    word.parse_word_files()
    word.all_people
    output_csv = "./input/processed/interviews.csv"
    word.export_interviews_to_csv(output_csv)