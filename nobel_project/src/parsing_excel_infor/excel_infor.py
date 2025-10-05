class ExcelInfor:
    def __init__(self, path):
        self.path = path
        self.all_questions = {}
    def show(self):
        print(f"Excel input file: {self.path}")
if __name__ == "__main__":
    excel_path = "./input/excel/2024_NobelData_CodingSheet_0825-2025_Final.xlsx"
    excel = ExcelInfor(excel_path)
    excel.show()