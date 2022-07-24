import re
import sqlite3
from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from models.item import ItemModel


class Item(Resource):
    parser = reqparse.RequestParser()
    
    parser.add_argument('price',
        type=float,
        required=True,
        help="This field can't be left blank!")

    parser.add_argument('store_id',
        type=int,
        required=True,
        help="Every item needs a store id.")

    @jwt_required()
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        else:
            return {'message': 'Item not found'}, 404


    def post(self, name):
        if ItemModel.find_by_name(name):
            return {'message': f'An item with name {name} already exists'}, 400

        request_data = Item.parser.parse_args()
        item = ItemModel(name, **request_data)
        print(item)

        try:
            item.save_to_db()
        except:
            return {'message': f'An error occurred inserting the item {name}'}, 500 # internal server error

        return item.json(), 201


    def delete(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()

        return {'message': f'Item {name} deleted'}


    def put(self, name):
        request_data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)
    
        if not item:
           item = ItemModel(name, **request_data)
        else:
            item.price = request_data['price']
            item.store_id = request_data['store_id']
            
        item.save_to_db()
        return item.json()


class Items(Resource):
    def get(self):
        return {'items': [item.json() for item in ItemModel.find_all()]}
