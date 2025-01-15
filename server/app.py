#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


# @app.route("/")
# def index():
#     return "<h1>Code challenge</h1>"


class Restaurants(Resource):
    def get(self):
        rests= [rest.to_dict(only=("address", "id", "name")) for rest in 
        Restaurant.query.all()]
        return make_response(rests, 200)
    
class RestaurantById(Resource):
   def get(self, id):
       rest = Restaurant.query.filter(Restaurant.id == id).first()
       if not rest:
           return make_response({"error": "Restaurant not found"}, 404)
       return make_response(rest.to_dict(only=("address", "id", "name", "restaurant_pizzas")), 200)
   
   def delete(self, id):
       rest = Restaurant.query.filter(Restaurant.id == id).first()
       if not rest:
           return make_response({"error": "Restaurant not found"}, 404)
       db.session.delete(rest)
       db.session.commit()
       return make_response('', 204)
    
api.add_resource(Restaurants, "/restaurants")
api.add_resource(RestaurantById, "/restaurants/<int:id>")

class Pizzas(Resource):
    def get(self):
        # Get all pizzas from the database
        pizzas = [pizza.to_dict(only=("id", "ingredients", "name")) for pizza in Pizza.query.all()]
        return make_response(pizzas, 200)

api.add_resource(Pizzas, "/pizzas")

class RestaurantPizzas(Resource):
  def get(self):
        restaurant_pizzas = [restaurant_pizza.to_dict() for restaurant_pizza in RestaurantPizza.query.all()]
        return restaurant_pizzas, 200

  def post(self):
        data = request.get_json()

        try:
            new_restaurant_pizza = RestaurantPizza(
                price=data['price'],
                pizza_id=data['pizza_id'],
                restaurant_id=data['restaurant_id']
            )

            db.session.add(new_restaurant_pizza)
            db.session.commit()

            return new_restaurant_pizza.to_dict(), 201
        except:
            return {'errors': ['validation errors']}, 400
    
api.add_resource(RestaurantPizzas, "/restaurant_pizzas")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
