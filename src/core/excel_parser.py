import pandas


class ExcelParser:
    HOLE_COLUMN_MAPPING = {
        "ИМЯ": "name",
        "X": "x",
        "Y": "y",
        "Z": "z",
        "ДЛИНА": "lenght",
        "ГОРИЗОНТ": "_level",
        "ДАТА ПРОХОДКИ": "issue_date",
    }

    ASSAY_COLUMN_MAPPING = {"ОБЪЕКТ": "name", "ОТ": "_from", "ДО": "_to", "Au": "Au"}

    def parse(self, file_path: str) -> dict:
        holes_df = pandas.read_excel(file_path, sheet_name="Holes")
        assays_df = pandas.read_excel(file_path, sheet_name="Assay")

        holes_df.columns = holes_df.columns.str.strip()
        assays_df.columns = assays_df.columns.str.strip()

        holes_df = holes_df.rename(columns=self.HOLE_COLUMN_MAPPING)
        assays_df = assays_df.rename(columns=self.ASSAY_COLUMN_MAPPING)

        return {
            "holes": holes_df.to_dict("records"),
            "assays": assays_df.to_dict("records"),
        }
