from mongoengine import connect, disconnect
from dotenv import load_dotenv

import os
from data.ship_data import *
import pandas as pd

load_dotenv()

connect('dev', alias='default', host=os.getenv('MONGO_URL'))

# 读取excel文件
# Load the CSV file

current_file_path = os.path.abspath(__file__)
print(f"当前文件路径: {current_file_path}")

# 获取当前文件的目录
current_directory = os.path.dirname(current_file_path)

file_path = os.path.join(current_directory, 'Shippment_Tracking.xlsx')

# 读取 Excel 文件
data = pd.read_excel(file_path)

# Iterate over each row and print the data
for index, row in data.iterrows():
    print(f"Row {index}:")
    print(row)

    print(pd.isna(row['Due_date']))

    ship = Shippment_Tracking.objects(index=str(row['id'])).first()

    if not ship:

        ship = Shippment_Tracking(
            index=str(row['id']),
            Task=row['Task'],
            Item=row['Item'] if not pd.isna(row['Item']) else None,
            Owner=row['Owner'],
            Status=row['Status'],
            Service_Provider=row['Service_Provider']
            if not pd.isna(row['Service_Provider']) else None,
            Tracking_No=str(row['Tracking_No']),
            Start_date=row['Start_date']
            if not pd.isna(row['Start_date']) else None,
            Due_date=row['Due_date'] if not pd.isna(row['Due_date']) else None,
            Total_day=str(row['Total_day'])
            if not pd.isna(row['Total_day']) else None,
            Total_Workday=str(row['Total_Workday'])
            if not pd.isna(row['Total_Workday']) else None,
            Actual_shipping_day=str(row['Actual_shipping_day'])
            if not pd.isna(row['Actual_shipping_day']) else None,
            Note=row['Note'] if not pd.isna(row['Note']) else None,
        )

        ship.save()

    else:
        ship = Shippment_Tracking.objects(index=str(row['id'])).update(
            set__Total_day=str(row['Total_day'])
            if not pd.isna(row['Total_day']) else None,
            set__Total_Workday=str(row['Total_Workday'])
            if not pd.isna(row['Total_Workday']) else None,
            set__Actual_shipping_day=str(row['Actual_shipping_day'])
            if not pd.isna(row['Actual_shipping_day']) else None,
        )

    # if pro:
    #     print('find')

    #     review = ProductReview(
    #     # index=index,
    #         state=row['state'],
    #         rating=row['rating'],
    #         author=row['author'],
    #         email=row['email'] if not pd.isna(row['email']) else None,
    #         location=row['location'] if not pd.isna(row['location']) else '',
    #         body=row['body'],
    #         imageUrl=row['imageUrl'] if not pd.isna(row['imageUrl']) else '',
    #         reply=row['reply'] if not pd.isna(row['reply']) else '',
    #         created_at=row['created_at']
    #         if not pd.isna(row['created_at']) else '',
    #         replied_at=row['replied_at']
    #         if not pd.isna(row['replied_at']) else None,
    #     )

    #     # pro.reviews.append(review)
    #     Product.objects(title=row['title']).update_one(
    #         add_to_set__reviews=review)

    # else:
    #     print('cao')
    # print("\n")

    # break
