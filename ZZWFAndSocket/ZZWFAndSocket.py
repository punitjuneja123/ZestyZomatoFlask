import pickle
from flask import Flask, render_template, request, redirect

app = Flask(__name__)
MENU_FILE = 'menu.pkl'


def load_menu():
    try:
        with open(MENU_FILE, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return []


def save_menu(menu):
    with open(MENU_FILE, 'wb') as f:
        pickle.dump(menu, f)

# Define the Dish class


class Dish:
    def __init__(self, name, price, availability=True):
        self.name = name
        self.price = price
        self.availability = availability


@app.route('/')
def welcome():
    return 'Welcome to Zesty Zomato'


@app.route('/menu')
def menu():
    dishes = load_menu()
    return render_template('menu.html', dishes=dishes)


@app.route('/add_dish', methods=['GET', 'POST'])
def add_dish():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        availability = bool(request.form.get('availability'))

        dish = Dish(name=name, price=price, availability=availability)
        menu = load_menu()
        menu.append(dish)
        save_menu(menu)
        return redirect('/menu')
    return render_template('add_dish.html')


@app.route('/edit_dish/<int:dish_id>', methods=['GET', 'POST'])
def edit_dish(dish_id):
    menu = load_menu()
    dish = menu[dish_id]

    if request.method == 'POST':
        dish.name = request.form['name']
        dish.price = float(request.form['price'])
        dish.availability = bool(request.form.get('availability'))

        save_menu(menu)
        return redirect('/menu')
    return render_template('edit_dish.html', dish=dish, dish_id=dish_id)


@app.route('/delete_dish/<int:dish_id>', methods=['POST'])
def delete_dish(dish_id):
    menu = load_menu()
    menu.pop(dish_id)
    save_menu(menu)
    return redirect('/menu')


if __name__ == '__main__':
    app.run()
