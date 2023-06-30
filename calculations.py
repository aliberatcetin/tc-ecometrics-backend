from datetime import datetime

import pandas as pd
import uuid

from data__ import indexes_visitors, indexes_suppliers


class Calculations:
    def __init__(self):
        pass

    def get_timestamp(self):
        format_str = "%A, %d %b %Y %H:%M:%S %p"
        result = datetime.now().strftime(format_str)
        return result

    def calculate_transport_distribution(self, data):
        counts = data["Means of Transport"].value_counts().to_list()
        items = list(data["Means of Transport"].value_counts().index)
        return {
            "items": items,
            "counts": counts
        }

    def _2_total_co2_emissions_accom(self, data):
        germany_hotel_index = indexes_visitors["germany_hotel_index"]
        hotel_visitors = data[data["Staying in Hotel"] == "Yes"]
        total_duration = hotel_visitors["Stay Duration in Days"].sum()
        return germany_hotel_index * len(hotel_visitors) * total_duration

    def _9_mobilty_score_visitors(self, data, total_co2):
        "Sum CO2 emissions ( Local Bus + National Train + International Train + Underground + Cycling + Walking)  /  Total CO2 Emissions Transportation  * 100"
        local_bus = data[data["Means of Transport"] == "Local Bus"]["CO2 Emission Travel in kg"].sum()
        international_train = data[data["Means of Transport"] == "International Train"][
            "CO2 Emission Travel in kg"].sum()
        cycling = data[data["Means of Transport"] == "Cycling"]["CO2 Emission Travel in kg"].sum()
        walking = data[data["Means of Transport"] == "Walking"]["CO2 Emission Travel in kg"].sum()
        return round(((local_bus + international_train + cycling + walking) / total_co2 * 100), 2)

    def calculate_suppliers(self, data, circularity_visitors):
        if "Mobility_Suppliers" not in data.sheet_names:
            return {}

        data = pd.read_excel(data, 'Mobility_Suppliers')
        total_co2_overall_suppliers = data["CO2 Emission Transportation"].sum()
        co2_per_supplier = total_co2_overall_suppliers / len(data)
        mobility_circularity_score_suppliers = (((data["Weight in kg"].sum()) / 1000) * indexes_suppliers[
            "Best Case Value CO2 (Low emissions)"] * data[
                                                    "Distance"].sum()) / total_co2_overall_suppliers * 100
        "(Mobility Circularity Score Suppliers + Mobility Circularity Score Visitors) / 2"
        "(Total Weight Tonnes * Distance * Best Case Value CO2) / Total CO2 Emissions Overall Suppliers * 100"
        return {
            "total_co2_overall_suppliers": round(total_co2_overall_suppliers, 2),
            "co2_per_supplier": round(co2_per_supplier, 2),
            "distribution_of_means_of_transport_suppliers": self.calculate_transport_distribution(data),
            "average_distance_per_supplier": round(data["Distance"].sum() / len(data), 2),
            "mobility_circularity_score_suppliers": round(mobility_circularity_score_suppliers, 2),
            "mobility_circularity_overall_score_suppliers": round(
                mobility_circularity_score_suppliers / circularity_visitors[
                    "mobility_circularity_score"], 2)
        }

    def calculate_visitors(self, data):
        if "Mobility_Visitors" not in data.sheet_names:
            return {}
        data = pd.read_excel(data, 'Mobility_Visitors')
        # visitors
        total_co2_transportation = data["CO2 Emission Travel in kg"].sum()
        total_co2_accommodation = self._2_total_co2_emissions_accom(data)
        co2_overall = total_co2_accommodation + total_co2_transportation
        reference_co2_per_visitor = 5000
        co2_per_visitor = co2_overall / len(data)
        return {
            "multiple_chart_labels": ["Total Co2 Transportation", "Total Co2 Accomodation"],
            "multiple_chart_data": [total_co2_transportation, total_co2_accommodation],
            "total_co2_emissions_transportation": total_co2_transportation,
            "total_co2_emissions_accomodation": total_co2_accommodation,
            "total_co2_emissions_overall": co2_overall,
            "co2_per_visitor": {
                "data": round(co2_per_visitor, 2),
                "color": "success" if round(co2_per_visitor, 2) < reference_co2_per_visitor else "danger",
                "tooltip": "The average event in Germany emits 5000Kg of Co2 per Person"
            },
            "distribution_of_means_of_transport": self.calculate_transport_distribution(data),
            "average_distance_per_visitor": round(data["Distance in km (return)"].sum() / len(data), 2),

            "mobility_circularity_score": self._9_mobilty_score_visitors(data, total_co2_transportation)
        }

    def calculate_mobility_scores(self, data):
        circularity_visitors = self.calculate_visitors(data)
        return {
            "circularity_visitors": circularity_visitors,
            "circularity_suppliers": self.calculate_suppliers(data, circularity_visitors),
            "calculation_id": str(uuid.uuid4()),
            "timestamp": self.get_timestamp()
        }
