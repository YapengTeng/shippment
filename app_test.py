from flask import Flask, request, jsonify
from mongoengine import connect
from upload_data2 import calculate_shipping_cost, update_shipping_price, delete_shipping_info

app = Flask(__name__)

# 连接到MongoDB数据库
connect('dev', alias='default', host=os.getenv('MONGO_URL'))

@app.route('/calculate_shipping_cost', methods=['POST'])
def calculate_shipping_cost_endpoint():
    try:
        data = request.json
        product_weight = data.get('product_weight')
        electricity = data.get('electricity')
        result = calculate_shipping_cost(product_weight, electricity)
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

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

if __name__ == '__main__':
    app.run(debug=True, port=5000)