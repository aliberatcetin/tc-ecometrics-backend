import numpy as np
import pandas as pd

from data__ import kpi_to_names


class FileManager:
    def __init__(self):
        self.recommendation_json = self.read_recommendation_excel()

    def get_recommendation_json(self):
        return self.recommendation_json

    def convert_kpis_to_names(self, kpis):
        if not kpis:
            return ""
        kpis = kpis.replace("and", ",")
        kpis = kpis.split(",")
        return [kpi_to_names.get(kpi.strip().replace("KPI", ""), "") for kpi in kpis]

    def read_recommendation_excel(self):
        file = pd.ExcelFile("db.xlsx")
        recommendations = pd.read_excel(file, 'Circular Blueprints (recommenda')
        recommendations = recommendations.where(pd.notnull(recommendations), None)
        recommendation_array = [{"description": row["Description"], "startups": row["Startups"], "kpis": row["KPI"],
                                 "image_url": f"http://localhost:3002/static/images/{index + 1}.jpg",
                                 "best_practice": row["Best Practice"], "link": row["Hyperlink"]}
                                for index, row in recommendations.iterrows()
                                ]

        for recommendation_item in recommendation_array:
            recommendation_item["kpis"] = self.convert_kpis_to_names(recommendation_item["kpis"])

        return recommendation_array
