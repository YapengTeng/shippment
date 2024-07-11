import requests

def test_calculate_shipping_cost():
    url = 'http://127.0.0.1:5000/calculate_shipping_cost'
    payload = {
        # Fill in your request data
    }
    response = requests.post(url, json=payload)
    assert response.status_code == 200
    print('Calculate Shipping Cost API Passed:', response.json())

def test_query_mongo_collection():
    url = 'http://127.0.0.1:5000/query_mongo_collection'
    payload = {
        # Fill in your request data
    }
    response = requests.post(url, json=payload)
    assert response.status_code == 200
    print('Query Mongo Collection API Passed:', response.json())

def test_update_shipping_price():
    url = 'http://127.0.0.1:5000/update_shipping_price'
    payload = {
        # Fill in your request data
    }
    response = requests.post(url, json=payload)
    assert response.status_code == 200
    print('Update Shipping Price API Passed:', response.json())

def test_delete_shipping_info():
    url = 'http://127.0.0.1:5000/delete_shipping_info'
    payload = {
        # Fill in your request data
    }
    response = requests.post(url, json=payload)
    assert response.status_code == 200
    print('Delete Shipping Info API Passed:', response.json())

if __name__ == '__main__':
    test_calculate_shipping_cost()
    test_query_mongo_collection()
    test_update_shipping_price()
    test_delete_shipping_info()
