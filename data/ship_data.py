from mongoengine import Document, EnumField, EmailField, DecimalField, StringField, URLField, BooleanField, DateTimeField, FloatField, IntField, EmbeddedDocument, EmbeddedDocumentField, ListField, LazyReferenceField
from enum import Enum
from datetime import datetime

# Table shippment tracking


class Product_Pricing_List(EmbeddedDocument):

    sku = StringField()
    Product_Name_CN = StringField()
    Product_Name_EN = StringField()


class Product_Pricing_ListV2(EmbeddedDocument):

    sku = StringField()
    Product_Name_CN = StringField()
    Product_Name_EN = StringField()
    Type = StringField()


class Product_Describe(EmbeddedDocument):

    Length = StringField()    # cm
    Width = StringField()    # cm
    Height = StringField()    # cm
    Weight = StringField()    # kg
    Electricity = StringField()    # Y/N/S敏感


class workday_5_10(EmbeddedDocument):

    Shipping_Way_5_10 = StringField()
    price_5_10 = FloatField()    # RMB


class Last_Leg(EmbeddedDocument):

    workday_2_5 = StringField()
    price_2_5 = FloatField()    # USD


class First_Leg(EmbeddedDocument):

    Air_Transport = FloatField()    # USD
    Air_Transport_date = DateTimeField()
    Sea_shipping = FloatField()    # USD
    Sea_shipping_date = DateTimeField()
    Domestic_shipping_price = FloatField()    # RMB


class Cost(EmbeddedDocument):

    Vendor_price = FloatField()    # RMB
    Self_shipping_cost = FloatField()    # USD
    Oversea_cost = FloatField()    # USD


class Self_Pricing(EmbeddedDocument):

    Self_Price_range = StringField()    # USD
    Self_Set_price = FloatField()    # USD
    Self_Lowest_price = FloatField()    # USD
    Self_Profit = FloatField()    # USD
    Self_Profit_Margin = FloatField()


class Oversea_Pricing(EmbeddedDocument):

    Oversea_Price_range = StringField()    # USD
    Oversea_Set_price = FloatField()    # USD
    Oversea_Lowest_price = FloatField()    # USD
    Oversea_Profit_Margin = FloatField()
    Highest_Discount = FloatField()
    Oversea_Profit = FloatField()    # USD
    Profit_Margin = FloatField()


class Shippment_Tracking(Document):

    index = StringField(unique=True)
    Task = StringField()
    Item = StringField()
    Owner = StringField()
    Status = StringField()
    Service_Provider = StringField()
    Tracking_No = StringField()
    Start_date = DateTimeField()
    Due_date = DateTimeField()
    Total_day = StringField()
    Total_Workday = StringField()
    Actual_shipping_day = StringField()
    Note = StringField()


class workday_3_5(EmbeddedDocument):

    Shipping_Way_3_5 = StringField()
    price_3_5 = FloatField()    # RMB


class workday_6_12(EmbeddedDocument):

    Shipping_Way_6_12 = StringField()
    price_6_12 = FloatField()    # RMB


class SingleParcel_Describe(EmbeddedDocument):

    Length = FloatField()    # 长度cm
    Width = FloatField()    # 宽度cm
    Height = FloatField()    # 高度cm
    Volume = FloatField()    # 体积
    Volume_Weight = FloatField()    # kg
    Actual_Weight = FloatField()    # kg


class Deliver_Weight(EmbeddedDocument):
    Weightkg = FloatField()    # kg
    Weightlbs = FloatField()    # lbs
    Weightoz = FloatField()    # oz


class PriceKgItem(EmbeddedDocument):
    key = StringField(required=True)
    value = StringField(default='')
