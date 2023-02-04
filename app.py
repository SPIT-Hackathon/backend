from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS, cross_origin
from flask_restful import Api, Resource
from flask_bcrypt import Bcrypt

from flask_pymongo import PyMongo

import os

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app)

bcrypt = Bcrypt(app)

app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
mongo = PyMongo(app)

# -----------DB Models start--------------------

Users = mongo.db.users

# -----------DB Models end--------------------


# -----------APIs start--------------------

@app.route('/register',methods=['POST'])
def registerUser():
    try:
        data = request.get_json()
        obj = Users.find_one({'email': data['email']})
        if obj is None:
            obj = {
                'email': data['email'],
                'password': data['password'],
                'name': data['name'],
                'mobile': data['mobile'],
            }
            Users.insert_one(obj)
            return {
                'email': data['email'],
                'message': 'User Created Successfully'
            }, 200
        return {'message': 'User Alredy Exist'}, 401
    except Exception as e:
        return {'message': 'Server Error' + str(e)}, 500



@app.route('/login',methods=['POST'])
def loginUser():
    try:
        data = request.get_json()
        obj = Users.find_one({'email': data['email']})
        print("User : ",str(obj['_id']))

        if obj is None:
            return {'message': 'User doesn\'t exist.'}
        if obj['password'] == data['password']:
            return {
                'email': obj['email'],
                'user_id': str(obj['_id']),
                'user_name': obj['name'],
                'mobile': obj['mobile']
            }, 200
        return {"message": 'Invalid credentials'}, 401
    except Exception as e:
        return {'message': 'Server Error' + str(e)}, 500


# -----------APIs end--------------------


if __name__ == '__main__':
  app.run(debug=True)