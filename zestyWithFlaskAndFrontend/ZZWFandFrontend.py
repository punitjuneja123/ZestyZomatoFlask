from flask import Flask, render_template, request, redirect
import pickle

app = Flask(__name__)

menu_data = []
order_data = []


def save_menu_data():
    with open('menu_data.pkl', 'wb') as file:
        pickle.dump(menu_data, file)


def load_menu_data():
    try:
        with open('menu_data.pkl', 'rb') as file:
            return pickle.load(file)
    except FileNotFoundError:
        return []


def create_table():
    global menu_data
    menu_data = load_menu_data()
    print('Menu data loaded successfully!')


def create_connection():
    create_table()
    return None


def add_dish_to_menu(dish):
    menu_data.append(dish)
    save_menu_data()


def remove_dish_from_menu(dish_id):
    global menu_data
    menu_data = [dish for dish in menu_data if dish['id'] != dish_id]
    save_menu_data()


def get_dish_by_id(dish_id):
    for dish in menu_data:
        if dish['id'] == dish_id:
            return dish
    return None


def save_order_data():
    with open('order_data.pkl', 'wb') as file:
        pickle.dump(order_data, file)


def load_order_data():
    try:
        with open('order_data.pkl', 'rb') as file:
            return pickle.load(file)
    except FileNotFoundError:
        return []


def add_order(order):
    order_data.append(order)
    save_order_data()


def get_order_by_id(order_id):
    for order in order_data:
        if order['id'] == order_id:
            return order
    return None


@app.route('/')
def welcome():
    return 'Welcome to Zesty Zomato'


@app.route('/menu', methods=['GET'])
def display_menu():
    return render_template('menu.html', menu=menu_data)


@app.route('/menu/add', methods=['GET'])
def add_dish_form():
    return render_template('add_dish.html')


@app.route('/menu/add', methods=['POST'])
def add_dish():
    name = request.form['name']
    price = float(request.form['price'])
    availability = bool(request.form.get('availability'))

    dish = {
        'id': len(menu_data) + 1,
        'name': name,
        'price': price,
        'availability': availability
    }

    add_dish_to_menu(dish)

    return redirect('/menu')


@app.route('/menu/edit/<int:dish_id>', methods=['GET'])
def edit_dish_form(dish_id):
    dish = get_dish_by_id(dish_id)
    return render_template('edit_dish.html', dish=dish, dish_id=dish_id)


@app.route('/menu/edit/<int:dish_id>', methods=['POST'])
def edit_dish(dish_id):
    name = request.form['name']
    price = float(request.form['price'])
    availability = bool(request.form.get('availability'))

    dish = get_dish_by_id(dish_id)
    dish['name'] = name
    dish['price'] = price
    dish['availability'] = availability

    save_menu_data()

    return redirect('/menu')


@app.route('/menu/delete/<int:dish_id>', methods=['GET'])
def delete_dish(dish_id):
    remove_dish_from_menu(dish_id)
    return redirect('/menu')


@app.route('/orders', methods=['GET'])
def display_orders():
    orders = order_data
    return render_template('orders.html', orders=orders)


@app.route('/orders/add', methods=['GET'])
def show_add_order_form():
    return render_template('add_order.html', error_message=None)


@app.route('/orders/add', methods=['POST'])
def add_order():
    customer_name = request.form['customer_name']
    dish_ids = [int(id.strip()) for id in request.form['dish_ids'].split(',')]

    # Check if all dishes are available
    available_dishes = [dish['id']
                        for dish in menu_data if dish['availability']]
    invalid_dishes = [
        dish_id for dish_id in dish_ids if dish_id not in available_dishes]

    if invalid_dishes:
        error_message = f"The following dishes are invalid or not available: {', '.join(map(str, invalid_dishes))}"
        return render_template('add_order.html', error_message=error_message)

    # Create the order and assign a unique order ID
    order_id = len(order_data) + 1
    order = {
        'id': order_id,
        'customer_name': customer_name,
        'dish_ids': dish_ids,
        'status': 'received'
    }
    order_data.append(order)

    with open('order_data.pkl', 'wb') as file:
        pickle.dump(order_data, file)

    return redirect('/orders')


@app.route('/orders/update/<int:order_id>', methods=['POST'])
def update_order(order_id):
    new_status = request.form['status']
    order = get_order_by_id(order_id)

    if not order:
        error_message = f"Order with ID {order_id} does not exist."
        return render_template('orders.html', orders=order_data, error_message=error_message)

    order['status'] = new_status
    save_order_data()

    return redirect('/orders')


if __name__ == '__main__':
    create_connection()
    app.run()
