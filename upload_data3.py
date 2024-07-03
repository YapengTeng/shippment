from mongoengine import connect, disconnect
from dotenv import load_dotenv

import os
from data.ship_data import *
import pandas as pd

from data.table import *
import sys

load_dotenv()

connect('dev', alias='default', host=os.getenv('MONGO_URL'))


def contains_currency_symbols(value):
    if isinstance(value, str):
        # 检查是否包含美元符号和人民币符号
        if '$' in value or '¥' in value or '￥' in value:
            value = value.replace('$', '').replace('¥', '').replace('￥', '')
            # 去除可能存在的千位分隔符
            value = value.replace(',', '')
    return value


def convert_type(value, type_function):

    value = contains_currency_symbols(value)

    if pd.isna(value) or value == '-':
        return None

    if type_function:
        try:
            return type_function(value)
        except ValueError:
            return None
    return None


# 读取excel文件
# Load the CSV file

current_file_path = os.path.abspath(__file__)
print(f"当前文件路径: {current_file_path}")

# 获取当前文件的目录
current_directory = os.path.dirname(current_file_path)

file_path = os.path.join(current_directory, 'Product_Pricing_data.xlsx')

sheetName = None

dfs = pd.read_excel(
    file_path,
    sheet_name=sheetName,
    header=[0, 1],
)

# Iterate over each row and print the data
# print(dfs.head())

# 遍历每个工作表并查看表头
for sheet_name, df in dfs.items():
    print(f"工作表名称: {sheet_name}")

    if sheet_name == 'Product_information':

        for index, row in df.iterrows():
            print(f"Row {index}:")
            # print(row)
            print(df.head())
            print(df.columns)

            ProductPricingList = Product_Pricing_List(
                sku=convert_type(row['Products List']['SKU'], str),
                Product_Name_CN=convert_type(
                    row['Products List']['Product_Name_CN'], str),
                Product_Name_EN=convert_type(
                    row['Products List']['Product_Name_EN'], str),
            )

            ProductDescribe = Product_Describe(
                Length=convert_type(row['Product_describe']['Length'], str),
                Width=convert_type(row['Product_describe']['Width'], str),
                Height=convert_type(row['Product_describe']['Height'], str),
                Weight=convert_type(row['Product_describe']['Weight'], str),
                Electricity=convert_type(row['Product_describe']['Electricity'],
                                         str),
            )

            workday_5_10_ = workday_5_10(
                Shipping_Way_5_10=convert_type(
                    row['5_10_workday']['5_10_Shipping_Way'], str),
                price_5_10=convert_type(row['5_10_workday']['5_10_price'],
                                        float),
            )

            LastLeg = Last_Leg(
                workday_2_5=convert_type(row['Last_Leg']['2_5_workday'], str),
                price_2_5=convert_type(row['Last_Leg']['2_5_price'], float),
            )

            print(convert_type(row['First_Leg']['Air_Transport'], float))
            print(convert_type(row['First_Leg']['Air_Transport_date'], str))

            print(convert_type(row['Cost']['Oversea_cost'], float))

            FirstLeg = First_Leg(
                Air_Transport=convert_type(row['First_Leg']['Air_Transport'],
                                           float),
                Air_Transport_date=convert_type(
                    row['First_Leg']['Air_Transport_date'], str),
                Sea_shipping=convert_type(row['First_Leg']['Sea_shipping'],
                                          float),
                Domestic_shipping_price=convert_type(
                    row['First_Leg']['Domestic_shipping_cost'], float),
            )

            Cost_ = Cost(
                Vendor_price=convert_type(row['Cost']['Vendor_price'], float),
                Self_shipping_cost=convert_type(
                    row['Cost']['Self_shipping_cost'], float),
                Oversea_cost=convert_type(row['Cost']['Oversea_cost'], float),
            )

            SelfPricing = Self_Pricing(
                Self_Price_range=convert_type(
                    row['Self_Pricing']['Self_Price_range'], str),
                Self_Set_price=convert_type(
                    row['Self_Pricing']['Self_Set_price'], float),
                Self_Lowest_price=convert_type(
                    row['Self_Pricing']['Self_Lowest_price'], float),
                Self_Profit=convert_type(row['Self_Pricing']['Self_Profit'],
                                         float),
                Self_Profit_Margin=convert_type(
                    row['Self_Pricing']['Self_Profit_Margin'], float),
            )

            OverseaPricing = Oversea_Pricing(
                Oversea_Price_range=convert_type(
                    row['Oversea_Pricing']['Oversea_Price_range'], str),
                Oversea_Set_price=convert_type(
                    row['Oversea_Pricing']['Oversea_Set_price'], float),
                Oversea_Lowest_price=convert_type(
                    row['Oversea_Pricing']['Oversea _Lowest_price'], float),
                Oversea_Profit_Margin=convert_type(
                    row['Oversea_Pricing']['Oversea _Profit_Margin'], float),
                Highest_Discount=convert_type(
                    row['Oversea_Pricing']['Highest_Discount'], float),
                Profit_Margin=convert_type(
                    row['Oversea_Pricing']['Profit_Margin'], float),
                Oversea_Profit=convert_type(
                    row['Oversea_Pricing']['Oversea _Profit_Margin.1'], float),
            )

            productPricng = Product_Pricing(
                Product_List=ProductPricingList,
                Product_Describe=ProductDescribe,
                workday_5_10=workday_5_10_,
                Last_Leg=LastLeg,
                First_Leg=FirstLeg,
                Cost=Cost_,
                Self_Pricing=SelfPricing,
                Oversea_Pricing=OverseaPricing,
                Exchange_Rate=convert_type(
                    row['Oversea_Pricing']['Exchange_Rate'], float),
            )

            productPricng.save()

    # if sheet_name == 'Air_Transport_price_first_Leg':
    #     for index, row in df.iterrows():
    #         print(f"Row {index}:")
    #         # print(row)
    #         print(df.head())
    #         print(df.columns)
    #         price_kg_list = []
    #         price_unit_list = []
    #         for key, value in row.items():
    #             if key[0] == 'Price_kg':
    #                 price_kg_item = PriceKgItem(key=convert_type(key[1], str),
    #                                             value=convert_type(value, str))
    #                 price_kg_list.append(price_kg_item)
    #             elif key[0] == 'Price_unit':
    #                 price_unit_item = PriceKgItem(key=convert_type(key[1], str),
    #                                               value=convert_type(
    #                                                   value, str))
    #                 price_unit_list.append(price_unit_item)

    #         AirTransportPriceFirstLeg = Air_Transport_price_first_Leg(
    #             Company=convert_type(row['Unnamed: 0_level_0']['Company'], str),
    #             Brand=convert_type(row['Unnamed: 1_level_0']['Brand'], str),
    #             Price_kg=price_kg_list,
    #         )

    #         AirTransportPriceFirstLeg.save()

    # if sheet_name == 'Sea_Transport_price_first_Leg':
    #     for index, row in df.iterrows():
    #         print(f"Row {index}:")
    #         # print(row)
    #         print(df.head())
    #         print(df.columns)

    #         price_kg_list = []
    #         for key, value in row.items():
    #             if key[0] == 'price_kg':
    #                 price_kg_item = PriceKgItem(key=convert_type(key[1], str),
    #                                             value=convert_type(value, str))
    #                 price_kg_list.append(price_kg_item)

    #         AirTransportPriceFirstLeg = Sea_Transport_price_first_Leg(
    #             Company=convert_type(row['Unnamed: 0_level_0']['Company'], str),
    #             Brand=convert_type(row['Unnamed: 1_level_0']['Brand'], str),
    #             Zone=convert_type(row['Unnamed: 2_level_0']['Zone'], str),
    #             Price_kg=price_kg_list,
    #         )

    #         AirTransportPriceFirstLeg.save()

    # if sheet_name == 'Shipping_price_last_Leg':
    #     for index, row in df.iterrows():
    #         print(f"Row {index}:")
    #         # print(row)
    #         print(df.head())
    #         print(df.columns)

    #         price_oz_list = []
    #         price_lbs_list = []
    #         for key, value in row.items():
    #             if key[0] == 'price_oz':
    #                 price_oz_item = PriceKgItem(key=convert_type(key[1], str),
    #                                             value=convert_type(value, str))
    #                 price_oz_list.append(price_oz_item)

    #             elif key[0] == 'price_lbs':
    #                 price_lbs_item = PriceKgItem(key=convert_type(key[1], str),
    #                                              value=convert_type(value, str))
    #                 price_lbs_list.append(price_lbs_item)

    #         ShippingPriceLastLeg = Shipping_price_last_Leg(
    #             Company=convert_type(row['Unnamed: 0_level_0']['Company'], str),
    #             Brand=convert_type(row['Unnamed: 1_level_0']['Brand'], str),
    #             Service=convert_type(row['Unnamed: 2_level_0']['Service'], str),
    #             Price_oz=price_oz_list,
    #             Price_lbs=price_lbs_list,
    #         )

    #         ShippingPriceLastLeg.save()

    # if sheet_name == 'Shipping_price_first_Leg':
    #     for index, row in df.iterrows():
    #         print(f"Row {index}:")
    #         # print(row)
    #         print(df.head())
    #         print(df.columns)

    #         price_kg_list = []
    #         price_unit_list = []
    #         for key, value in row.items():
    #             if key[0] == 'Price_kg':
    #                 price_kg_item = PriceKgItem(key=convert_type(key[1], str),
    #                                             value=convert_type(value, str))
    #                 price_kg_list.append(price_kg_item)

    #             elif key[0] == 'price_unit':
    #                 price_unit_item = PriceKgItem(key=convert_type(key[1], str),
    #                                               value=convert_type(
    #                                                   value, str))
    #                 price_unit_list.append(price_unit_item)

    #         ShippingPriceLastLeg = Shipping_price_first_Leg(
    #             Type=convert_type(row['Unnamed: 0_level_0']['Type'], str),
    #             Company=convert_type(row['Unnamed: 1_level_0']['Company'], str),
    #             Brand=convert_type(row['Unnamed: 2_level_0']['Brand'], str),
    #             Service=convert_type(row['Unnamed: 3_level_0']['Service'], str),
    #             Price_kg=price_kg_list,
    #             Price_unit=price_unit_list,
    #             NOTE=convert_type(row['test']['NOTE'], str),
    #             Requirement=convert_type(row['test']['Requirement'], str),
    #             Effectiveness=convert_type(row['test']['Effectiveness'], str),
    #         )

    #         ShippingPriceLastLeg.save()

    print("表头（列名）:")

sys.exit()
