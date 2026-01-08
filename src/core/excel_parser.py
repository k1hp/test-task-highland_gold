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

        def process_df(df, column_mapping):
            if df.empty:
                return []

            df.columns = df.columns.str.strip()
            df = df.rename(columns=column_mapping)
            return df.to_dict("records")

        return {
            "holes": process_df(holes_df, self.HOLE_COLUMN_MAPPING),
            "assays": process_df(assays_df, self.ASSAY_COLUMN_MAPPING),
        }
