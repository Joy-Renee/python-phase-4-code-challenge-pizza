#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request,  jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db, render_as_batch=True)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants', methods= ['GET'])
def restaurants():
    if request.method == 'GET':
        restaurants = []
        for restaurant in Restaurant.query.all():
            restaurant_dict = {
                "address" : restaurant.address,
                "id" : restaurant.id,
                "name" : restaurant.name
            }
            restaurants.append(restaurant_dict)

        return jsonify(restaurants), 200
    
    
@app.route('/restaurants/<int:id>', methods = ('GET', 'DELETE'))
def get_restaurant_id(id):
    restaurant = db.session.get(Restaurant, id)
    if request.method == 'GET':
        if restaurant:
            restaurant_dict = {
                "id" : restaurant.id,
                "address": restaurant.address,
                "name": restaurant.name,
                "restaurant_pizzas" : [ {

                    "pizza_id" : restaurant_pizzas.pizza_id,
                    "price" : restaurant_pizzas.price,
                    "restaurant_id" : restaurant_pizzas.restaurant_id,
                    "pizza" : {
                        "name" : restaurant_pizzas.pizza.name,
                        "ingredients" : restaurant_pizzas.pizza.ingredients
                    }
                }
                for restaurant_pizzas in restaurant.restaurant_pizzas
                ]
            }
            return jsonify(restaurant_dict), 200
            
        else:
            return jsonify({"error": "Restaurant not found"}), 404
            

    elif request.method == 'DELETE':
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return jsonify(''),204
         
        else:
            return jsonify({"error": "Restaurant not found"}, 404)
          
        
@app.route('/pizzas', methods= ['GET'])
def pizzas():
    if request.method == 'GET':
        pizzas = []
        for pizza in Pizza.query.all():
            pizza_dict = {
                "id": pizza.id,
                "ingredients" : pizza.ingredients,
                "name" : pizza.name
            }
            pizzas.append(pizza_dict)

        return jsonify(pizzas), 200
        
        
@app.route('/restaurant_pizzas', methods=['GET', 'POST'])
def create_restaurant_pizzas():
    if request.method == 'GET':
        try:
            restaurant_pizzas = []
            for restaurant_pizza in RestaurantPizza.query.all():
                restaurant_pizza_dict = {
                    "id": restaurant_pizza.id,
                    "price": restaurant_pizza.price,
                    "pizza_id": restaurant_pizza.pizza_id,
                    "restaurant_id": restaurant_pizza.restaurant_id,
                    "pizza": restaurant_pizza.pizza.to_dict(only=("id", "name", "ingredients")),
                    "restaurant": restaurant_pizza.restaurant.to_dict(only=("id", "name", "address"))
                }
                restaurant_pizzas.append(restaurant_pizza_dict)

            return jsonify(restaurant_pizzas), 200
           

        except Exception as error:
            return jsonify({"errors": [str(error)]}), 500
            

    elif request.method == 'POST':
        try:
            data = request.get_json()

            pizza_id = data.get("pizza_id")
            restaurant_id = data.get("restaurant_id")
            price = data.get("price")

            if price is None or not (1 <= price <= 30):
                return jsonify({"errors": ["validation errors"]}), 400

            pizza = db.session.get(Pizza, pizza_id)
            restaurant = db.session.get(Restaurant, restaurant_id)

            if not pizza:
                return jsonify({"errors": ["Invalid pizza_id"]}), 400
                
            if not restaurant:
                return jsonify({"errors": ["Invalid restaurant_id"]}), 400

            new_restaurant_pizza = RestaurantPizza(
                price=price,
                pizza_id=pizza_id,
                restaurant_id=restaurant_id
            )
            db.session.add(new_restaurant_pizza)
            db.session.commit()

            restaurant_pizza_dict = {
                "id": new_restaurant_pizza.id,
                "price": new_restaurant_pizza.price,
                "pizza_id": new_restaurant_pizza.pizza_id,
                "restaurant_id": new_restaurant_pizza.restaurant_id,
                "pizza": new_restaurant_pizza.pizza.to_dict(only=("id", "name", "ingredients")),
                "restaurant": new_restaurant_pizza.restaurant.to_dict(only=("id", "name", "address"))
            }

            return jsonify(restaurant_pizza_dict),201

        except Exception as error:
            return jsonify({"errors": [str(error)]}), 500

if __name__ == "__main__":
    app.run(port=5555, debug=True)
