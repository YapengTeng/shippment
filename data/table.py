from .ship_data import *


# DeKai
class Product_Pricing(Document):

    Product_List = EmbeddedDocumentField('Product_Pricing_List')
    Product_Describe = EmbeddedDocumentField('Product_Describe')
    workday_5_10 = EmbeddedDocumentField('workday_5_10')
    Last_Leg = EmbeddedDocumentField('Last_Leg')
    First_Leg = EmbeddedDocumentField('First_Leg')
    Cost = EmbeddedDocumentField('Cost')
    Self_Pricing = EmbeddedDocumentField('Self_Pricing')
    Oversea_Pricing = EmbeddedDocumentField('Oversea_Pricing')
    Exchange_Rate = FloatField()


# Xiaoxu
class Product_shipping_price(Document):
    Product_List = EmbeddedDocumentField('Product_Pricing_ListV2')
    Product_describe_cmkg = EmbeddedDocumentField('Product_Describe')
    SingleParcel_describe_cmkg = EmbeddedDocumentField('SingleParcel_Describe')
    Deliver_Weight = EmbeddedDocumentField('Deliver_Weight')
    workday_3_5 = EmbeddedDocumentField('workday_3_5')
    workday_5_10 = EmbeddedDocumentField('workday_5_10')
    workday_6_12 = EmbeddedDocumentField('workday_6_12')
    Last_Leg = EmbeddedDocumentField('Last_Leg')
    First_Leg = EmbeddedDocumentField('First_Leg')


class Shipping_price_first_Leg(Document):
    Type = StringField()
    Range = StringField(choices=["3_5_workday", "5_10_workday", "6_15_workday"])
    Company = StringField()
    Brand = StringField()
    Service = StringField()
    Price_kg = ListField(EmbeddedDocumentField(PriceKgItem), default=[])
    Price_unit = ListField(EmbeddedDocumentField(PriceKgItem), default=[])
    NOTE = StringField()
    Requirement = StringField()
    Effectiveness = StringField()


class Air_Transport_price_first_Leg(Document):

    Company = StringField()
    Brand = StringField()
    Price_kg = ListField(EmbeddedDocumentField(PriceKgItem), default=[])


class Sea_Transport_price_first_Leg(Document):
    Company = StringField()
    Brand = StringField()
    Zone = StringField()
    Price_kg = ListField(EmbeddedDocumentField(PriceKgItem), default=[])


class Shipping_price_last_Leg(Document):
    Company = StringField()
    Brand = StringField()
    Service = StringField()
    Price_oz = ListField(EmbeddedDocumentField(PriceKgItem), default=[])
    Price_lbs = ListField(EmbeddedDocumentField(PriceKgItem), default=[])
