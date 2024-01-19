from application import app
from flask import request
from database import Queries
import json

def response_to_front(result):
    return app.response_class(
        response=json.dumps(result),
        status=200,
        mimetype='application/json'
    )

def date_format(**kwargs):
    if 'date' in kwargs:
        kwargs['date'] = kwargs['date'].strftime('%Y-%m-%d %H:%M:%S')
    return kwargs

@app.route('/')
@app.route('/index')
def index():
    return "Hello from flask!"

@app.route('/product', methods=['GET', 'POST', 'PUT', 'DELETE'])
def product():
    if request.method == 'GET':
        query_get = Queries.get_product(**request.args)
        result = query_get.as_dict()
        response = response_to_front(result)
        return response
    
    if request.method == 'POST':
        id = Queries.add_product(**request.get_json())
        query_get = Queries.get_product(**{'id': id})
        result = query_get.as_dict()
        response = response_to_front(result)
        return response
    
    if request.method == 'PUT':
        id = Queries.update_product(**request.get_json())
        query_get = Queries.get_product(**{'id': id})
        result = query_get.as_dict()
        response = response_to_front(result)
        return response
    
    if request.method == 'DELETE':
        query_delete = Queries.delete_product(**request.get_json())
        response = response_to_front(query_delete)
        return response

@app.route("/user", methods=['GET', 'POST', 'PUT', 'DELETE'])
def user():
    if request.method =='GET':
        query_get = Queries.get_user(**request.args)
        result = {}
        result["user"] = query_get.as_dict()
        result["address"] = query_get.address.as_dict()
        response = response_to_front(result)
        return response
    
    if request.method == 'POST':
        id = Queries.add_user(**request.get_json())
        query_get = Queries.get_user(**{'id': id})
        result = {}
        result["user"] = query_get.as_dict()
        result["address"] = query_get.address.as_dict()
        response = response_to_front(result)
        return response
    
    if request.method == 'PUT':
        id = Queries.update_user(**request.get_json())
        query_get = Queries.get_user(**{'id': id})
        result = {}
        result["user"] = query_get.as_dict()
        result["address"] = query_get.address.as_dict()
        response = response_to_front(result)
        return response
    
    if request.method == 'DELETE':
        query_delete = Queries.delete_user(**request.get_json())
        response = response_to_front(query_delete)
        return response 

@app.route("/order", methods=['GET', 'POST', 'PUT', 'DELETE'])
def order():
    if request.method == 'GET':      
        query_get = Queries.get_order_by_user(**request.args)
        result = []
        for order in query_get:
            formatted = date_format(**order.as_dict())
            formatted["user"] = order.user.as_dict()
            formatted["product"] = [p.as_dict() for p in order.product]
            result.append(formatted)
        response = response_to_front(result)
        return response
    
    if request.method == 'POST':
        id = Queries.add_order(**request.get_json())
        query_get = Queries.get_order(**{'id': id})
        result = query_get.as_dict()
        result["user"] = query_get.user.as_dict()
        result["product"] = []
        for product in query_get.product:
            result["product"].append(product.as_dict())
        formatted = date_format(**result)
        response = response_to_front(formatted)
        return response
    
    if request.method == 'DELETE':
        query_delete = Queries.delete_order(**request.get_json())
        response = response_to_front(query_delete)
        return response
      
app.run(debug=True)