from flask import Flask, jsonify, request
import pickle
app = Flask(__name__)


def get_dish_by_id(dish_id):
    for dish in menu:
        if dish["id"] == dish_id:
            return dish
    return None


def get_new_dish_id():
    max_id = 0
    for dish in menu:
        if dish["id"] > max_id:
            max_id = dish["id"]
    return max_id + 1


def load_menu():
    try:
        with open('menu.pkl', 'rb') as file:
            menu_data = pickle.load(file)
    except FileNotFoundError:
        menu_data = []
    return menu_data


menu = load_menu()


def save_menu(menu_data):
    with open('menu.pkl', 'wb') as file:
        pickle.dump(menu_data, file)


@app.route('/')
def welcome():
    return 'welcome to Zesty Zomato'


@app.route("/menu")
def showMenu():
    return jsonify(menu=menu)


@app.route("/add_dish", methods=["POST"])
def addDish():
    new_dish = request.json
    new_dish_id = get_new_dish_id()
    new_dish["id"] = new_dish_id
    menu.append(new_dish)
    save_menu(menu)
    return jsonify(message="Dish added successfully")


@app.route("/remove_dish/<int:dish_id>", methods=["DELETE"])
def removeDish(dish_id):
    for dish in menu:
        if dish["id"] == dish_id:
            menu.remove(dish)
            save_menu(menu)
            return jsonify(message="Dish removed successfully.")

    return jsonify(error="Dish not found.")


@app.route("/update_availability/<int:dish_id>", methods=["PUT"])
def updateAvailability(dish_id):
    new_availability = request.json.get("availability")
    if new_availability is None:
        return jsonify(error="Invalid request. Availability status is required.")

    for dish in menu:
        if dish["id"] == dish_id:
            dish["availability"] = new_availability
            save_menu(menu)
            return jsonify(message="Availability updated successfully.")

    return jsonify(error="Dish not found.")


# Add a new order

# Load orders from pickle file
def load_orders():
    try:
        with open("orders.pickle", "rb") as file:
            orders = pickle.load(file)
    except (FileNotFoundError, EOFError):
        orders = []

    return orders

# Save orders to pickle file


def save_orders(orders):
    with open("orders.pickle", "wb") as file:
        pickle.dump(orders, file)

# Generate a unique order ID


def generate_order_id():
    orders = load_orders()
    if orders:
        last_order = orders[-1]
        order_id = last_order["id"] + 1
    else:
        order_id = 1
    return order_id

# Add a new order


@app.route("/new_order", methods=["POST"])
def newOrder():
    customer_name = request.json["customer_name"]
    dishes_ids = request.json["dishes_ids"]
    orders = load_orders()
    order_id = generate_order_id()
    new_order = {
        "id": order_id,
        "customer_name": customer_name,
        "dishes_ids": dishes_ids,
        "status": "received"
    }
    orders.append(new_order)
    save_orders(orders)
    return jsonify(message="Order placed successfully", order_id=order_id)

# Update the status of an order


@app.route("/update_order_status/<int:order_id>", methods=["PUT"])
def updateOrderStatus(order_id):
    order_id = order_id
    new_status = request.json["status"]
    orders = load_orders()
    for order in orders:
        if order["id"] == order_id:
            order["status"] = new_status
            save_orders(orders)
            return jsonify(message="Order status updated successfully")
    return jsonify(error="Order not found")

# Display all orders


@app.route("/orders", methods=["GET"])
def getOrders():
    orders = load_orders()
    return jsonify(orders=orders)


if __name__ == '__main__':
    app.run()
