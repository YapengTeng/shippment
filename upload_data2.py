from mongoengine import connect, disconnect
from dotenv import load_dotenv

import os
from data.ship_data import *
import pandas as pd

from data.table import *
import sys

load_dotenv()

connect('dev', alias='default', host=os.getenv('MONGO_URL'))

class ShippingPriceFirstLeg(Document):
    Type = StringField()
    Company = StringField()
    Brand = StringField()
    Price_kg = ListField(DictField())
    Price_unit = ListField(DictField())

collections = {
    "shipping_price_first_leg": ShippingPriceFirstLeg._get_collection(),
    "air_transport_price_first_leg": db['dev']["air_transport_price_first__leg"],
    "sea_transport_price_first_leg": db['dev']["sea_transport_price_first__leg"],
    "shipping_price_last_leg": db['dev']["shipping_price_last__leg"],
    "product_shipping_price": db['dev']["product_shipping_price"]
}

# 查询最接近的物流价格
def find_nearest_price(weight, electricity):
    documents_price = ShippingPriceFirstLeg.objects(Company__in=["万邦", "加速"])

    price_kg_with_electricity = {}
    price_kg_without_electricity = {}
    price_unit_with_electricity = {}
    price_unit_without_electricity = {}
    meta_info_with_electricity = {}
    meta_info_without_electricity = {}

    for doc in documents_price:
        if doc.Type == '小包价格-带电5-10个工作日':
            price_kg_with_electricity = {float(item['key']): float(item['value']) for item in doc.Price_kg}
            price_unit_with_electricity = {float(item['key']): float(item['value']) for item in doc.Price_unit}
            meta_info_with_electricity = {
                "Type": doc.Type,
                "Company": doc.Company,
                "Brand": doc.Brand
            }
        elif doc.Type == '小包价格-普货5-10工作日':
            price_kg_without_electricity = {float(item['key']): float(item['value']) for item in doc.Price_kg}
            price_unit_without_electricity = {float(item['key']): float(item['value']) for item in doc.Price_unit}
            meta_info_without_electricity = {
                "Type": doc.Type,
                "Company": doc.Company,
                "Brand": doc.Brand
            }

    if electricity == 'Y':
        price_kg = price_kg_with_electricity
        price_unit = price_unit_with_electricity
        meta_info = meta_info_with_electricity
    else:
        price_kg = price_kg_without_electricity
        price_unit = price_unit_without_electricity
        meta_info = meta_info_without_electricity

    if not price_kg:
        raise ValueError("No price information available for the selected type and company.")

    nearest_weight = min(price_kg.keys(), key=lambda x: abs(x - weight))
    return nearest_weight, price_kg[nearest_weight], price_unit[nearest_weight], meta_info

# 计算物流价格
def calculate_shipping_cost(product_weight, electricity):
    nearest_weight, price_y, price_z, meta_info = find_nearest_price(product_weight, electricity)
    shipping_cost = product_weight * price_y + price_z

    return {
        "Selected Type": meta_info['Type'],
        "Selected Company": meta_info['Company'],
        "Selected Brand": meta_info['Brand'],
        "Nearest Weight": nearest_weight,
        "Price per kg": price_y,
        "Unit Price": price_z,
        "Shipping Cost": shipping_cost
    }

#更新运费
def update_shipping_price(collection_name, weight, new_price, **kwargs):
    collection = collections.get(collection_name)
    if collection is None:
        print(f"No such collection: {collection_name}")
        return

    query = {}
    
    # 处理不同集合的查询条件
    if collection_name == "product_shipping_price":
        if "SKU" in kwargs and kwargs["SKU"]:
            query['Product_List.sku'] = re.compile(kwargs['SKU'], re.IGNORECASE)
        if "Product_Name_CN" in kwargs and kwargs["Product_Name_CN"]:
            query['Product_List.Product_Name_CN'] = re.compile(kwargs['Product_Name_CN'], re.IGNORECASE)
        if "Product_Name_EN" in kwargs and kwargs["Product_Name_EN"]:
            query['Product_List.Product_Name_EN'] = re.compile(kwargs['Product_Name_EN'], re.IGNORECASE)
        if "Type" in kwargs and kwargs["Type"]:
            query['Product_List.Type'] = re.compile(kwargs['Type'], re.IGNORECASE)
    else:
        if "types" in kwargs and kwargs["types"]:
            query['Type'] = {'$in': [re.compile(t, re.IGNORECASE) for t in kwargs['types']]}
        if "companies" in kwargs and kwargs["companies"]:
            query['Company'] = {'$in': [re.compile(c, re.IGNORECASE) for c in kwargs['companies']]}
        if "brands" in kwargs and kwargs["brands"] and collection_name != "sea_transport_price_first_leg":
            query['Brand'] = {'$in': [re.compile(b, re.IGNORECASE) for b in kwargs['brands']]}
        if "zones" in kwargs and kwargs["zones"] and collection_name == "sea_transport_price_first_leg":
            query['Zone'] = {'$in': [re.compile(z, re.IGNORECASE) for z in kwargs['zones']]}
    
    print(f"Query: {query}")  # 调试信息：打印查询条件
    
    document = collection.find_one(query)
    if document:
        # 打印找到的文档
        print(f"Found Document: {document}")
        
        # 确保 Price_kg 字段存在且是列表
        if 'Price_kg' in document and isinstance(document['Price_kg'], list):
            weight_str = str(weight)
            price_kg_dict = {item['key']: item['value'] for item in document['Price_kg']}
            current_price = price_kg_dict.get(weight_str)
            if current_price is not None:
                # 打印修改前的运费信息
                print(f"Weight: {weight_str}")
                print(f"Current Price: {current_price}")
                print(f"New Price: {new_price}")

                # 更新运费
                for item in document['Price_kg']:
                    if item['key'] == weight_str:
                        item['value'] = new_price
                        break

                collection.update_one(query, {"$set": {"Price_kg": document['Price_kg']}})
            else:
                print(f"Weight {weight_str} not found in the document.")
        else:
            print("Price_kg field is not found or not a list in the document.")
    else:
        print(f"No document found matching the query: {query}")

#删除功能
def delete_shipping_info(collection_name, **kwargs):
    collection = collections.get(collection_name)
    if collection is None:
        print(f"No such collection: {collection_name}")
        return

    query = {}

    # 处理不同集合的查询条件
    if collection_name == "product_shipping_price":
        if "SKU" in kwargs and kwargs["SKU"]:
            if isinstance(kwargs["SKU"], list):
                query['Product_List.sku'] = {'$in': [re.compile(sku, re.IGNORECASE) for sku in kwargs['SKU']]}
            else:
                query['Product_List.sku'] = re.compile(kwargs['SKU'], re.IGNORECASE)
    else:
        if "types" in kwargs and kwargs["types"]:
            query['Type'] = {'$in': [re.compile(t, re.IGNORECASE) for t in kwargs['types']]}
        if "companies" in kwargs and kwargs["companies"]:
            query['Company'] = {'$in': [re.compile(c, re.IGNORECASE) for c in kwargs['companies']]}
        if "brands" in kwargs and kwargs["brands"] and collection_name != "sea_transport_price_first_leg":
            query['Brand'] = {'$in': [re.compile(b, re.IGNORECASE) for b in kwargs['brands']]}
        if "zones" in kwargs and kwargs["zones"] and collection_name == "sea_transport_price_first_leg":
            query['Zone'] = {'$in': [re.compile(z, re.IGNORECASE) for z in kwargs['zones']]}
    
    print(f"Query for deletion: {query}")  # 调试信息：打印查询条件

    result = collection.delete_many(query)
    print(f"Deleted {result.deleted_count} documents.")


# 物流价格计算API
@app.route('/calculate_shipping_cost', methods=['POST'])
def calculate_shipping_cost_endpoint():
    data = request.json
    product_weight = data.get('product_weight')
    electricity = data.get('electricity')

    if product_weight is None or electricity is None:
        return jsonify({"error": "Missing required parameters"}), 400

    try:
        result = calculate_shipping_cost(product_weight, electricity)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 查询功能API
@app.route('/query_mongo_collection', methods=['POST'])
def query_mongo_collection_endpoint():
    data = request.json
    collection_name = data.get('collection_name')
    query_params = data.get('query_params', {})

    if collection_name is None:
        return jsonify({"error": "Missing required parameter: collection_name"}), 400

    try:
        result = query_mongo_collection(collection_name, **query_params)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 更新运费功能API
@app.route('/update_shipping_price', methods=['POST'])
def update_shipping_price_endpoint():
    data = request.json
    collection_name = data.get('collection_name')
    weight = data.get('weight')
    new_price = data.get('new_price')
    update_params = data.get('update_params', {})

    if collection_name is None or weight is None or new_price is None:
        return jsonify({"error": "Missing required parameters"}), 400

    try:
        update_shipping_price(collection_name, weight, new_price, **update_params)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 删除功能API
@app.route('/delete_shipping_info', methods=['POST'])
def delete_shipping_info_endpoint():
    data = request.json
    collection_name = data.get('collection_name')
    delete_params = data.get('delete_params', {})

    if collection_name is None:
        return jsonify({"error": "Missing required parameter: collection_name"}), 400

    try:
        delete_shipping_info(collection_name, **delete_params)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

file_path = os.path.join(current_directory, '物流计算数据库.xlsx')

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

    if sheet_name == 'Product_shipping_price':
        for index, row in df.iterrows():
            print(f"Row {index}:")
            # print(row)
            print(df.head())
            print(df.columns)

            product_list = Product_Pricing_ListV2(
                sku=convert_type(row['Product_List']['SKU'], str),
                Product_Name_CN=convert_type(
                    row['Product_List']['Product_Name_CN'], str),
                Product_Name_EN=convert_type(
                    row['Product_List']['Product_Name_EN'], str),
                Type=convert_type(row['Product_List']['Type'], str),
            )

            print(row['SingleParcel_describe_cmkg']['Width'])

            product_describe_cmkg = Product_Describe(
                Length=convert_type(row['Product_describe_cmkg']['Length'],
                                    str),
                Width=convert_type(row['Product_describe_cmkg']['Width'], str),
                Height=convert_type(row['Product_describe_cmkg']['Height'],
                                    str),
                Weight=convert_type(row['Product_describe_cmkg']['Weight'],
                                    str),
                Electricity=convert_type(row['Electricity']['Electricity'],
                                         str),
            )

            print(row['SingleParcel_describe_cmkg']['Width'])

            singleParcel_describe_cmkg = SingleParcel_Describe(
                Length=convert_type(row['SingleParcel_describe_cmkg']['Length'],
                                    float),
                Width=convert_type(row['SingleParcel_describe_cmkg']['Width'],
                                   float),
                Height=convert_type(row['SingleParcel_describe_cmkg']['Height'],
                                    float),
                Volume=convert_type(row['SingleParcel_describe_cmkg']['Volume'],
                                    float),
                Volume_Weight=convert_type(
                    row['SingleParcel_describe_cmkg']['Volume_Weight'], float),
                Actual_Weight=convert_type(
                    row['SingleParcel_describe_cmkg']['Actual_Weight'], float),
            )

            deliver_weight = Deliver_Weight(
                Weightkg=convert_type(row['Deliver_Weight']['Weightkg'], float),
                Weightlbs=convert_type(row['Deliver_Weight']['Weightlbs'],
                                       float),
                Weightoz=convert_type(row['Deliver_Weight']['Weightoz'], float),
            )

            workday_3_5_ = workday_3_5(
                Shipping_Way_3_5=convert_type(
                    row['3_5_workday']['3_5_Shipping_Way'], str),
                price_3_5=convert_type(row['3_5_workday']['3_5_price'], float),
            )

            workday_5_10_ = workday_5_10(
                Shipping_Way_5_10=convert_type(
                    row['5_10_workday']['5_10_Shipping_Way'], str),
                price_5_10=convert_type(row['5_10_workday']['5_10_price'],
                                        float),
            )

            workday_6_12_ = workday_6_12(
                Shipping_Way_6_12=convert_type(
                    row['6_12_workday']['6_12_Shipping_Way'], str),
                price_6_12=convert_type(row['6_12_workday']['6_12_price'],
                                        float),
            )

            last_Leg = Last_Leg(
                workday_2_5=convert_type(row['Last_Leg']['2_5_workday'], str),
                price_2_5=convert_type(row['Last_Leg']['2_5_price'], float),
            )

            first_Leg = First_Leg(
                Air_Transport=convert_type(row['First_Leg']['Air_Transport'],
                                           float),
                Air_Transport_date=convert_type(
                    row['First_Leg']['Air_Transport_date'], datetime),
                Sea_shipping=convert_type(row['First_Leg']['Sea_shipping'],
                                          float),
                Sea_shipping_date=convert_type(
                    row['First_Leg']['Sea_shipping_date'], datetime),
                Domestic_shipping_price=convert_type(
                    row['First_Leg']['Domestic_shipping_price'], float),
            )

            product_ship_price_ins = Product_shipping_price.objects(
                Product_List=product_list).first()
            if product_ship_price_ins:
                continue
            product_ship_price_ins = Product_shipping_price(
                Product_List=product_list,
                Product_describe_cmkg=product_describe_cmkg,
                SingleParcel_describe_cmkg=singleParcel_describe_cmkg,
                Deliver_Weight=deliver_weight,
                workday_3_5=workday_3_5_,
                workday_5_10=workday_5_10_,
                workday_6_12=workday_6_12_,
                Last_Leg=last_Leg,
                First_Leg=first_Leg,
            )

            product_ship_price_ins.save()

    print("表头（列名）:")
    # print(df.columns)
    # print()

sys.exit()

for index, row in dfs.iterrows():
    print(f"Row {index}:")
    print(row)

    product_list = Product_Pricing_ListV2(
        sku=str(row['Product_List']['SKU'])
        if not pd.isna(row['Product_List']['SKU']) else None,
        Product_Name_CN=row['Product_List']['Product_Name_CN']
        if not pd.isna(row['Product_List']['Product_Name_CN']) else None,
        Product_Name_EN=row['Product_List']['Product_Name_EN']
        if not pd.isna(row['Product_List']['Product_Name_EN']) else None,
        Type=row['Product_List']['Type']
        if not pd.isna(row['Product_List']['Type']) else None,
    )

    Product_describe_cmkg = Product_Describe(
        Length=str(row['Product_describe_cmkg']['Length']) if
        not pd.isna(row['Product_describe_cmkg']['Length']) else None,    # cm
        Width=str(row['Product_describe_cmkg']['Width'])
        if not pd.isna(row['Product_describe_cmkg']['Width']) else None,    # cm
        Height=str(row['Product_describe_cmkg']['Height']) if
        not pd.isna(row['Product_describe_cmkg']['Height']) else None,    # cm
        Weight=str(row['Product_describe_cmkg']['Weight']) if
        not pd.isna(row['Product_describe_cmkg']['Weight']) else None,    # kg
        Electricity=row['Electricity']['Electricity']
        if not pd.isna(row['Electricity']['Electricity']) else None    # Y/N/S敏感
    )

    SingleParcel_describe_cmkg = SingleParcel_Describe(
        Length=row['SingleParcel_describe_cmkg']['Length']
        if not pd.isna(row['SingleParcel_describe_cmkg']['Length']) else None,
        Height=row['SingleParcel_describe_cmkg']['Height']
        if not pd.isna(row['SingleParcel_describe_cmkg']['Height']) else None,
        Volume=row['SingleParcel_describe_cmkg']['Volume']
        if not pd.isna(row['SingleParcel_describe_cmkg']['Volume']) else None,
        Volume_Weight=row['SingleParcel_describe_cmkg']['Volume_Weight']
        if not pd.isna(row['SingleParcel_describe_cmkg']['Volume_Weight']) else
        None,
        Actual_Weight=row['SingleParcel_describe_cmkg']['Actual_Weight']
        if not pd.isna(row['SingleParcel_describe_cmkg']['Actual_Weight']) else
        None,
    )

    deliver_weight = Deliver_Weight(
        Weightkg=row['Deliver_Weight']['Weightkg']
        if not pd.isna(row['Deliver_Weight']['Weightkg']) else None,
        Weightlbs=row['Deliver_Weight']['Weightlbs']
        if not pd.isna(row['Deliver_Weight']['Weightlbs']) else None,
        Weightoz=row['Deliver_Weight']['Weightoz']
        if not pd.isna(row['Deliver_Weight']['Weightoz']) else None,
    )

    workday_3_5_ = workday_3_5(
        Shipping_Way_3_5=str(row['3_5_workday']['3_5_Shipping_Way'])
        if not pd.isna(row['3_5_workday']['3_5_Shipping_Way'])
        and row['3_5_workday']['3_5_Shipping_Way'] != '-' else None,
        price_3_5=row['3_5_workday']['3_5_price']
        if not pd.isna(row['3_5_workday']['3_5_price'])
        and row['3_5_workday']['3_5_price'] != '-' else None,
    )

    workday_5_10_ = workday_5_10(
        Shipping_Way_5_10=str(row['5_10_workday']['5_10_Shipping_Way'])
        if not pd.isna(row['5_10_workday']['5_10_Shipping_Way'])
        and row['5_10_workday']['5_10_Shipping_Way'] != '-' else None,
        price_5_10=row['5_10_workday']['5_10_price']
        if not pd.isna(row['5_10_workday']['5_10_price'])
        and row['5_10_workday']['5_10_price'] != '-' else None,
    )

    workday_6_12_ = workday_6_12(
        Shipping_Way_6_12=str(row['6_12_workday']['6_12_Shipping_Way'])
        if not pd.isna(row['6_12_workday']['6_12_Shipping_Way'])
        and row['6_12_workday']['6_12_Shipping_Way'] != '-' else None,
        price_6_12=row['6_12_workday']['6_12_price']
        if not pd.isna(row['6_12_workday']['6_12_price'])
        and row['6_12_workday']['6_12_price'] != '-' else None,
    )

    last_Leg = Last_Leg(
        workday_2_5=row['Last_Leg']['2_5_workday']
        if not pd.isna(row['Last_Leg']['2_5_workday'])
        and row['Last_Leg']['2_5_workday'] != '-' else None,
        price_2_5=row['Last_Leg']['2_5_price']
        if not pd.isna(row['Last_Leg']['2_5_price'])
        and row['Last_Leg']['2_5_price'] != '-' else None,
    )

    first_Leg = First_Leg(
        Air_Transport=row['First_Leg']['Air_Transport']
        if not pd.isna(row['First_Leg']['Air_Transport']) else None,
        Air_Transport_date=row['First_Leg']['Air_Transport_date']
        if not pd.isna(row['First_Leg']['Air_Transport_date']) else None,
        Sea_shipping=row['First_Leg']['Sea_shipping']
        if not pd.isna(row['First_Leg']['Sea_shipping']) else None,
        Sea_shipping_date=row['First_Leg']['Sea_shipping_date']
        if not pd.isna(row['First_Leg']['Sea_shipping_date']) else None,
        Domestic_shipping_price=row['First_Leg']['Domestic_shipping_price']
        if not pd.isna(row['First_Leg']['Domestic_shipping_price'])
        and row['First_Leg']['Domestic_shipping_price'] != '-' else None,
    )

    product_ship_price_ins = Product_shipping_price.objects(
        Product_List=product_list).first()
    if product_ship_price_ins:
        continue

    product_ship_price = Product_shipping_price(
        Product_List=product_list,
        Product_describe_cmkg=Product_describe_cmkg,
        SingleParcel_describe_cmkg=SingleParcel_describe_cmkg,
        Deliver_Weight=deliver_weight,
        workday_3_5=workday_3_5_,
        workday_5_10=workday_5_10_,
        workday_6_12=workday_6_12_,
        Last_Leg=last_Leg,
        First_Leg=first_Leg,
    )

    product_ship_price.save()
