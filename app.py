from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS, cross_origin
from flask_restful import Api, Resource
from flask_bcrypt import Bcrypt

from flask_pymongo import PyMongo

from flask_mail import Mail
from flask_mail import Message

import os
import numpy as np
import io
import logging

from utilities import *

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
app.logger.setLevel('INFO')
CORS(app)

bcrypt = Bcrypt(app)

app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
mongo = PyMongo(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


# -----------DB Models start--------------------

Users = mongo.db.users
Transcriptions = mongo.db.transcriptions

# -----------DB Models end--------------------


# -----------APIs start--------------------

@app.route('/test',methods=['GET'])
def test():
    try:
        subject = "Greetings from StudyPat!"
        sender = "studypatt@gmail.com"
        recipients = ["joy.almeida@spit.ac.in","kristen.pereira@spit.ac.in", "gaurav.parulekar@spit.ac.in" , "hrishikesh.lamdade@spit.ac.in"]

        msg = Message(subject = subject, sender = sender, recipients= recipients)
        msg.body = "Email Function is Working!"

        mail.send(msg)
        return {'message': 'Email sent'}, 200
    except Exception as e: 
        return {'message': 'Email sent'}, 200

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

@app.route('/create', methods=['POST'])
def create_notes():
    # Catch the image file from a POST request
    try:
        data = request.get_json()
        print("data: ", data)
        video_url = data["video_url"]
        user_id = str(data["user_id"])
        chapter_name = str(data["chapter_name"])
        subject_name = str(data["subject_name"])

        print(video_url)

        transcription,title = get_transcription(video_url)
        chunks = get_chunks(transcription['text'])

        summarries = []

        for para in chunks:
            summary = get_summary(para)
            summarries.append(summary)    
        obj = {'title':str(title),'chunks':str(chunks),'summary': str(summarries), 'user_id': user_id, 'chapter_name': chapter_name, 'video_url': video_url }
        Transcriptions.insert_one(obj)
        # Return on a JSON format
        # obj = {'title':str(title),'chunks':str(chunks),'summary': str(summarries), 'user_id': user_id, 'chapter_name': chapter_name, 'video_url': video_url }
        # print(obj)
        return {"message": "transcript generated successfully"}, 200
    except Exception as e:
        return {'message': 'Server Error' + str(e)}, 500

@app.route('/users', methods=['GET'])
def get_users():
    obj = Users.find_one({'email': 'user@gmail.com'})

    return obj
# -----------APIs end--------------------


if __name__ == '__main__':
  app.run(debug=True)