import pandas as pd
import json
import os
import re

class ExcelInfor:
    def __init__(self, file_path, sheet):
        self._file_path = file_path
        self._sheet = sheet
        self.all_categories = {}

    def show(self):
        print(f">>Excel path: {self._file_path}")
        print(f">>Excel sheets: {self._sheet}")

    def parsing_excel_sheets(self):
        print(type(self._sheet), self._sheet)
        # Một số token rác hay gặp (bạn có thể bổ sung nếu thấy token khác)
        trash_tokens = {"9999", "n/a", "na", "none", "-", "--", "...", "&nbsp;"}
        for sheet in self._sheet:
            df = pd.read_excel(self._file_path, sheet_name=sheet)

            # Nếu vô tình trả về dict (khi sheet_name=None), lấy DataFrame đầu tiên
            if isinstance(df, dict):
                df = list(df.values())[0]

            # Bỏ hàng đầu (chứa Q1, Q2,...)
            df_data = df.iloc[1:].reset_index(drop=True)

            for col in df.columns:
                if str(col).startswith("Unnamed"):
                    continue

                # chuẩn hóa category: bỏ hậu tố .1 .2 ...
                category = re.sub(r"\.\d+$", "", str(col)).strip()
                if not category:
                    continue

                questions = []
                for val in df_data[col].dropna():
                    # chỉ xử lý string
                    if isinstance(val, str):
                        text = val.strip()               # <-- loại bỏ whitespace 2 đầu
                        if not text:
                            continue                     # bỏ chuỗi rỗng sau strip()
                        # bỏ những ô chỉ là mã Q1, Q2,...
                        if re.match(r'^[Qq]\d+', text):
                            continue
                        # bỏ token rác thường gặp (ví dụ '9999' ở dạng string)
                        if text.lower() in trash_tokens:
                            continue
                        # bỏ chuỗi chỉ chứa chữ số (vd "1234", "9999")
                        if re.fullmatch(r'\d+', text):
                            continue
                        # bỏ chuỗi chỉ chứa ký tự không phải chữ/chữ số (chỉ dấu)
                        if not re.search(r'\w', text):
                            continue

                        questions.append(text)
                    else:
                        # nếu muốn bỏ các giá trị numeric (đã dropna) - giữ logic hiện tại: bỏ
                        continue

                # loại trùng trong cột
                questions = list(dict.fromkeys(questions))

                # gom vào all_categories (và loại trùng toàn bộ)
                if category not in self.all_categories:
                    self.all_categories[category] = questions
                else:
                    self.all_categories[category].extend(questions)
                    self.all_categories[category] = list(dict.fromkeys(self.all_categories[category]))

        dir_path = os.path.dirname(self._file_path)
        question_path = dir_path + "/../processed/nobel_questions.json"
        print(f">>Save question information at: {question_path}")
        with open(question_path, "w", encoding="utf-8") as f:
            json.dump(self.all_categories, f, ensure_ascii=False, indent=2)
    
if __name__ == "__main__":

    # Define excel infor
    excel_path = "./input/excel/2024_NobelData_CodingSheet_0825-2025_Final.xlsx"
    question_sheets = [
    "Interview Questions_Physics",
    "Interview Questions Chemistry",
    "interview Questions Medicine",
    "Interview Questions Economical ",
    "Interview Questions Literature"
    ]

    excel = ExcelInfor(excel_path, question_sheets)
    excel.show()
    excel.parsing_excel_sheets()
    excel.all_categories