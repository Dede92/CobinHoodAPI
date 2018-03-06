#!flask/bin/python
from flask import Flask, jsonify
from flask import request
import json
import requests
import time
import os

app = Flask(__name__)

base_url = 'https://api.cobinhood.com'
get_currencies = '/v1/market/currencies'
get_currency_price = '/v1/market/tickers/{trading_pair_id}'
get_order = '/v1/trading/orders/{order_id}'
get_orders = '/v1/trading/orders'
get_order_book = '/v1/market/orderbooks/{trading_pair_id}'

# doc
@app.route('/swagger.json', methods=['GET'])
def get_swagger():
	SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
	json_file_path = os.path.join(SITE_ROOT, 'swagger.json')
	with open(json_file_path, encoding='utf-8') as f:
		thedata = json.load(f)

	return app.response_class(
		response=json.dumps(thedata),
		status=200,
		mimetype='application/json'
	)
	
# Getting latest price of a symbol
@app.route('/api/v1/market/currencies/<trading_pair_id>', methods=['GET'])
def get_price_per_symbol(trading_pair_id):
	r = requests.get(base_url+get_currency_price.format(trading_pair_id=trading_pair_id))
	return app.response_class(
		response=json.dumps(r.json()),
		status=r.status_code,
		mimetype='application/json'
	)

# Get depth of symbol / order book
@app.route('/api/v1/market/orderbooks/<trading_pair_id>', methods=['GET'])
def get_depth_symbol(trading_pair_id):
	headers = request.headers
	token = headers.get('Authorization')
	headers = {'Content-type': 'application/json', 'Authorization': token, 'nonce': str(int(time.time()))}

	r = requests.get(base_url+get_order_book.format(trading_pair_id=trading_pair_id), headers=headers)
	return app.response_class(
		response=json.dumps(r.json()),
		status=r.status_code,
		mimetype='application/json'
	)

# Checking an order’s status
@app.route('/api/v1/trading/orders/<order_id>', methods=['GET'])
def get_order_status(order_id):
	headers = request.headers
	token = headers.get('Authorization')
	headers = {'Content-type': 'application/json', 'Authorization': token, 'nonce': str(int(time.time()))}

	r = requests.get(base_url+get_order.format(order_id=order_id), headers=headers)

	return app.response_class(
		response=json.dumps(r.json()),
		status=r.status_code,
		mimetype='application/json'
	)

#  Cancelling an order
@app.route('/api/v1/trading/orders/<order_id>', methods=['DELETE'])
def delete_order(order_id):
	headers = request.headers
	token = headers.get('Authorization')
	headers = {'Content-type': 'application/json', 'Authorization': token, 'nonce': str(int(time.time()))}

	r = requests.delete(base_url+get_order.format(order_id=order_id), headers=headers)

	return app.response_class(
		response=json.dumps(r.json()),
		status=r.status_code,
		mimetype='application/json'
	)

# Getting list of open orders
@app.route('/api/v1/trading/orders', methods=['GET'])
def get_open_orders():
	headers = request.headers
	token = headers.get('Authorization')
	headers = {'Content-type': 'application/json', 'Authorization': token, 'nonce': str(int(time.time()))}

	r = requests.get(base_url+get_orders, headers=headers)
	
	result_json=r.json().get('result')
	open_orders = [x for x in r.json().get('result').get('orders') if x.get('state')=='open']
	result_json['orders'] = open_orders

	return app.response_class(
		response=json.dumps(result_json),
		status=r.status_code,
		mimetype='application/json'
	)

#  Placing a LIMIT order
@app.route('/api/v1/trading/orders/limit', methods=['POST'])
def post_limit_order():
	headers = request.headers
	response = request.data
	data = {}
	if response:
		data = json.loads(response.decode('utf-8'))
	token = headers.get('Authorization')
	data['type']='limit'
	headers = {'Content-type': 'application/json', 'Authorization': token, 'nonce': str(int(time.time()))}

	r = requests.post(base_url+get_orders, headers=headers, data=json.dumps(data))

	return app.response_class(
		response=json.dumps(r.json()),
		status=r.status_code,
		mimetype='application/json'
	)

# Placing a MARKET order
@app.route('/api/v1/trading/orders/market', methods=['POST'])
def post_market_order():
	headers = request.headers
	response = request.data
	data = {}
	if response:
		data = json.loads(response.decode('utf-8'))
	token = headers.get('Authorization')

	data['type']='market'
	headers = {'Content-type': 'application/json', 'Authorization': token, 'nonce': str(int(time.time()))}

	r = requests.post(base_url+get_orders, headers=headers, data=json.dumps(data))

	return app.response_class(
		response=json.dumps(r.json()),
		status=r.status_code,
		mimetype='application/json'
	)

if __name__ == '__main__':
    app.run(debug=False)