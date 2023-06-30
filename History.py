from mongoengine import *


class History(Document):
    calculation_id = StringField(required=True)
    circularity_visitors = DictField(required=True)
    circularity_suppliers = DictField(required=True)
    timestamp = StringField(required=True)

    meta = {
        "indexes": [
            "calculation_id",
        ]
    }