from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    jwt_required,
    get_jwt,
    get_jwt_identity
)
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

    @jwt_required(fresh=True)
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

    @jwt_required()
    def delete(self, name):
        claims = get_jwt()
        if not claims['is_admin']:
            return {'message': 'Admin privilege required.'}, 401
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
    @jwt_required(optional=True)
    def get(self):
        user_id = get_jwt_identity()
        items = [item.json() for item in ItemModel.find_all()]
        if user_id:
            return {'items': items}, 200
        return {
            'items': [item['name'] for item in items],
            'message': 'More data available if you log in.'
            }, 200
