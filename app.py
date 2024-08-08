import os
from flask import Flask, abort, send_file, g, request, redirect, jsonify, render_template
from bson.objectid import ObjectId
from flasgger.utils import swag_from
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

from mongoengine import connect, Q
from urllib.parse import urlencode
from dotenv import load_dotenv
from flask_cors import CORS

from data.table import Product_Pricing
from data.ship_data import *
#from upload_data2 import calculate_shipping_cost, update_shipping_price, delete_shipping_info, ShippingPriceFirstLeg
from upload_data2 import calculate_shipping_cost_first_leg, calculate_shipping_cost_last_leg, update_shipping_price, delete_shipping_info, ShippingPriceFirstLeg
import re 

def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)

    CORS(app)

    load_dotenv()

    connect('dev', alias='default', host=os.getenv('MONGO_URL'))

    #
    # @app.route('/api/ship', methods=['POST'])
    # def zeng():

    #     product_pricing = Product_Pricing(Product_List=Product_Pricing_List(
    #         sku="SKU",
    #         Product_Name_CN="Product Name",
    #         Product_Name_EN="Product Name",
    #     ),
    #                                       Product_Describe=Product_Describe(
    #                                           Length="1",
    #                                           Width="1",
    #                                           Height="1",
    #                                           Weight="1",
    #                                           Electricity="Y",
    #                                       ),
    #                                       workday_5_10=workday_5_10(
    #                                           Shipping_Way_5_10="Shipping Way",
    #                                           price_5_10=1,
    #                                       ),
    #                                       Last_Leg=Last_Leg(
    #                                           workday_2_5="2-5",
    #                                           price_2_5=1,
    #                                       ),
    #                                       First_Leg=First_Leg(
    #                                           Air_Transport=1,
    #                                           Air_Transport_date=datetime.now(),
    #                                       ))

    #     product_pricing.save()

    # @app.route('/api/ship', methods=['GET'])
    # def cha():

    #     # product_pricing = Product_Pricing.objects(Product_List.sku='').first()
    #     if not product_pricing:
    #         abort(404)
    #     return jsonify(product_pricing.to_json())
    
    @app.route('/calculate_shipping_cost', methods=['POST'])
    def calculate_shipping_cost_endpoint():
        try:
            data = request.json
            lag = data.get('lag')
            
            if lag == 'first':
                package_weight = data.get('package_weight')
                electricity = data.get('electricity')
                result = calculate_shipping_cost_first_leg(package_weight, electricity)
            elif lag == 'last':
                oz = data.get('oz')
                lbs = data.get('lbs')
                zone = data.get('zone')
                result = calculate_shipping_cost_last_leg(oz, lbs, zone)
            else:
                raise ValueError("Invalid lag parameter")
            
            return jsonify(result)
        except Exception as e:
            app.logger.error(f"Error: {e}")
            return jsonify({"error": str(e)}), 500

    
    # @app.route('/calculate_shipping_cost', methods=['POST'])
    # def calculate_shipping_cost_endpoint():
    #     try:
    #         data = request.json
    #         package_weight = data.get('package_weight')
    #         electricity = data.get('electricity')
    #         result = calculate_shipping_cost(package_weight, electricity)
    #         return jsonify(result)
    #     except Exception as e:
    #         app.logger.error(f"Error: {e}")
    #         return jsonify({"error": str(e)}), 500
        
    @app.route('/update_shipping_price', methods=['POST'])
    def update_shipping_price_endpoint():
        try:
            data = request.json
            collection_name = data.get('collection_name')
            weight = data.get('weight')
            new_price = data.get('new_price')
            additional_params = data.get('additional_params', {})
            update_shipping_price(collection_name, weight, new_price, **additional_params)
            return jsonify({"status": "success"})
        except Exception as e:
            app.logger.error(f"Error: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/delete_shipping_info', methods=['POST'])
    def delete_shipping_info_endpoint():
        try:
            data = request.json
            collection_name = data.get('collection_name')
            additional_params = data.get('additional_params', {})
            delete_shipping_info(collection_name, **additional_params)
            return jsonify({"status": "success"})
        except Exception as e:
            app.logger.error(f"Error: {e}")
            return jsonify({"error": str(e)}), 500
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)