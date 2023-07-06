from bson.json_util import dumps
import json
from bson.objectid import ObjectId
from bson import ObjectId
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_pymongo import pymongo
from bson.errors import InvalidId
from flask_socketio import SocketIO, emit
CONNECTION_STRING = "mongodb+srv://punit:punit@cluster0.hpn8i.mongodb.net/?retryWrites=true&w=majority"
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database('zestyZomato')
menu_collection = pymongo.collection.Collection(db, 'menu')
orders_collection = pymongo.collection.Collection(db, 'order')


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)


app = Flask(__name__)
app.json_encoder = CustomJSONEncoder
socketio = SocketIO(app, async_mode='eventlet')


@socketio.on('connect', namespace='/all_orders')
def handle_connect():
    emit('connected', {'data': 'Connected to all_orders namespace'})


class Dish:
    def __init__(self, dish_id, dish_name, price, availability):
        self.dish_id = dish_id
        self.dish_name = dish_name
        self.price = price
        self.availability = availability


@app.route('/test')
def test():
    db.menu_collection.insert_one({"name": "John"})
    return "Connected to the data base!"


@app.route('/user', methods=['GET'])
def user_page():
    menu = list(menu_collection.find())
    return render_template('user_page.html', menu=menu)


@app.route('/orders/place', methods=['POST'])
def place_order():
    customer_name = request.form.get('customer_name')
    selected_dishes = request.form.getlist('selected_dishes')
    menu = list(menu_collection.find())
    order = {
        'customer_name': customer_name,
        'dishes': selected_dishes,
        'status': 'received'
    }
    new_order = orders_collection.insert_one(order)
    new_order_id = new_order.inserted_id

    dish_names = []
    total_price = 0.0
    for dish_id in order['dishes']:
        dish = next((item for item in menu if str(
            item['_id']) == dish_id), None)
        if dish:
            dish_names.append(dish['dish_name'])
            total_price += dish['price']
        else:
            dish_names.append('Unknown Dish')

    cName = order["customer_name"]
    status = order["status"]
    order = {"cName": cName, "dish_names": dish_names,
             "total_price": total_price, "status": status, "order_id": str(new_order_id)}
    # Emit real-time update for new order
    emit('new_order', order,
         namespace='/all_orders', broadcast=True)

    return redirect(url_for('user_order', order_id=str(new_order_id)))


# ...


@app.route('/user_order/<order_id>', methods=['GET'])
def user_order(order_id):
    order = orders_collection.find_one({'_id': ObjectId(order_id)})
    menu = list(menu_collection.find())

    dish_names = []
    total_price = 0.0

    for dish_id in order['dishes']:
        dish = next((item for item in menu if str(
            item['_id']) == dish_id), None)
        if dish:
            dish_names.append(dish['dish_name'])
            total_price += dish['price']
        else:
            dish_names.append('Unknown Dish')

    return render_template('user_order.html', order=order, dish_names=dish_names, total_price=total_price)


@app.route('/all_orders')
def all_orders():
    orders = list(orders_collection.find())
    for order in orders:
        total_price = 0.0
        dish_details = []
        for dish_id in order['dishes']:
            dish_obj = menu_collection.find_one({'_id': ObjectId(dish_id)})
            if dish_obj:
                dish_details.append(dish_obj['dish_name'])
                total_price += dish_obj['price']

        order['dish_details'] = dish_details
        order['total_price'] = total_price

    return render_template('all_orders.html', orders=orders)


@socketio.on('update_order_status')
def update_order_status(order_id, status):
    updated_order = orders_collection.find_one_and_update(
        {'_id': ObjectId(order_id)},
        {'$set': {'status': status}},
        return_document=pymongo.ReturnDocument.AFTER
    )
    # Emit real-time update for order status
    socketio.emit('order_status_update', updated_order)


# @app.route('/menu', methods=['GET'])
# def get_menu_items():
#     menu = list(menu_collection.find())
#     for dish in menu:
#         dish['_id'] = str(dish['_id'])  # Convert ObjectId to string
#     return jsonify(menu)


@app.route('/menu', methods=['GET'])
def display_menu():
    menu = list(menu_collection.find())
    return render_template('menu.html', menu=menu)


@app.route('/menu/add', methods=["GET", 'POST'])
def add_dish():
    if request.method == 'POST':
        dish = {
            'dish_name': request.form.get('dish_name'),
            'price': float(request.form.get('price')),
            'availability': bool(request.form.get('availability'))
        }
        menu_collection.insert_one(dish)
        return redirect('/menu')
    return render_template('add_dish.html')


@app.route('/menu/edit/<dish_id>', methods=['GET', 'POST'])
def edit_dish(dish_id):
    if request.method == 'POST':
        dish_updates = {
            'dish_name': request.form.get('dish_name'),
            'price': float(request.form.get('price')),
            'availability': bool(request.form.get('availability'))
        }
        menu_collection.update_one({'_id': ObjectId(dish_id)}, {
                                   '$set': dish_updates})
        return redirect('/menu')
    else:
        dish = menu_collection.find_one({'_id': ObjectId(dish_id)})
        return render_template('edit_dish.html', dish=dish, dish_id=dish_id)


@app.route('/menu/delete/<dish_id>', methods=['GET'])
def delete_dish(dish_id):
    menu_collection.delete_one({'_id': ObjectId(dish_id)})
    return redirect('/menu')


if __name__ == '__main__':
    socketio.run(app, debug=True)
