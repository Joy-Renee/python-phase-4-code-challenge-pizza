#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
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
        response = make_response(
            jsonify(restaurants), 200
        )
        return response
    
@app.route('/restaurants/<int:id>', methods = ('GET', 'DELETE'))
def get_restaurant_id(id):
    restaurant = Restaurant.query.get(id)
    if request.method == 'GET':
        if restaurant:
            restaurant_dict = {
                "address": restaurant.address,
                "id" : restaurant.id,
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
            return  make_response(jsonify(restaurant_dict), 200)
        
        else:
            return  make_response(jsonify({"error": "Restaurant not found"}), 404)
        
        
    elif request.method == 'DELETE':
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
        
            return make_response(jsonify({"message": "Restaurant deleted"}), 204)
        
        else :
            return make_response(jsonify({"error": "Restaurant not found"}), 404)
             
        
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
        response = make_response(
            jsonify(pizzas), 200
        )
        return response
    
@app.route('/restaurant_pizzas', methods=['GET', 'POST'])
def restaurant_pizzas():
    if request.method == 'GET':
        restaurant_pizzas = []
        for restaurant_pizza in RestaurantPizza.query.all():
            restaurant_pizza_dict = {

                "id": restaurant_pizza.id,
                "pizza": {
                    "id": restaurant_pizza.pizza.id,
                    "ingredients": restaurant_pizza.pizza.ingredients,
                    "name": restaurant_pizza.pizza.name
                },
                "pizza_id": restaurant_pizza.pizza_id,
                "price": restaurant_pizza.price,
                "restaurant": {
                    "address": restaurant_pizza.restaurant.address,
                    "id": restaurant_pizza.restaurant.id,
                    "name": restaurant_pizza.restaurant.name
                },
                "restaurant_id": restaurant_pizza.restaurant_id
            }
            restaurant_pizzas.append(restaurant_pizza_dict)
        return make_response(jsonify(restaurant_pizzas), 200)
         
    
    elif request.method == 'POST':
        new_restaurant_pizza = RestaurantPizza(
            pizza_id=request.form.get("pizza_id"),
            restaurant_id = request.form.get("restaurant_id"),
            price=request.form.get("price")
        )
        db.session.add(new_restaurant_pizza)
        db.session.commit()
        restaurant_pizza_dict = new_restaurant_pizza.to_dict()
        return make_response(jsonify(restaurant_pizza_dict), 500)
         
    else:
        return make_response(jsonify({"errors": ["validation errors"]}), 201)
         
        


if __name__ == "__main__":
    app.run(port=5555, debug=True)
