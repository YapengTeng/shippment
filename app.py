import os
from flask import Flask, abort, send_file, g, request, redirect, jsonify, render_template
from bson.objectid import ObjectId
from flasgger.utils import swag_from
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

from mongoengine import connect, Q
from urllib.parse import urlencode
from dotenv import load_dotenv
from flask_cors import CORS

from backend.ship.data.table import Product_Pricing
from data.ship_data import *


def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)

    CORS(app)

    load_dotenv()

    connect('dev', alias='default', host=os.getenv('MONGO_URL'))

    #
    @app.route('/api/ship', methods=['POST'])
    def zeng():

        product_pricing = Product_Pricing(Product_List=Product_Pricing_List(
            sku="SKU",
            Product_Name_CN="Product Name",
            Product_Name_EN="Product Name",
        ),
                                          Product_Describe=Product_Describe(
                                              Length="1",
                                              Width="1",
                                              Height="1",
                                              Weight="1",
                                              Electricity="Y",
                                          ),
                                          workday_5_10=workday_5_10(
                                              Shipping_Way_5_10="Shipping Way",
                                              price_5_10=1,
                                          ),
                                          Last_Leg=Last_Leg(
                                              workday_2_5="2-5",
                                              price_2_5=1,
                                          ),
                                          First_Leg=First_Leg(
                                              Air_Transport=1,
                                              Air_Transport_date=datetime.now(),
                                          ))

        product_pricing.save()

    # @app.route('/api/ship', methods=['GET'])
    # def cha():

    #     # product_pricing = Product_Pricing.objects(Product_List.sku='').first()
    #     if not product_pricing:
    #         abort(404)
    #     return jsonify(product_pricing.to_json())
