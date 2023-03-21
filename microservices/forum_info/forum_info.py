#!/usr/bin/env python3
# import relevant dependencies
import os
import haversine as hs
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# INITIALISING APP
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

if os.name == "nt":
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/forum_db'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost:3306/forum_db'

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)
CORS(app)

# DECLARING DATABASE CLASS
class forum_db(db.Model):
    __tablename__ = 'forum_table'
    forum_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.VARCHAR(64), nullable=False)
    title =  db.Column(db.VARCHAR(64), nullable=False)
    description = db.Column(db.VARCHAR(1000))
    datetime = db.Column(db.VARCHAR(19), nullable=False)
    

    def __init__(self, forum_id, username, title, description,datetime):
        self.forum_id = forum_id
        self.username = username
        self.title = title
        self.description = description
        self.datetime = datetime


    def json(self):
        forum = {
            'forum_id': self.forum_id,
            'username': self.username,
            'title': self.title,
            'description': self.description,
            'datetime': self.datetime
        }
        return forum
    
class comments_table(db.Model):
    tablename = 'comments_table'
    forum_id = db.Column(db.Integer, db.ForeignKey('forum_table.forum_id'), primary_key=True)
    commentor_username = db.Column(db.VARCHAR(64), nullable=False, primary_key=True)
    comment =  db.Column(db.VARCHAR(1000), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False, primary_key=True)
    
    def init(self, forum_id, commentor_username, comment, datetime):
        self.forum_id = forum_id
        self.commentor_username = commentor_username
        self.comment = comment
        self.datetime = datetime


    def json(self):
        forum = {
            'forum_id': self.forum_id,
            'commentor_username': self.commentor_username,
            'comment': self.comment,
            'datetime': self.datetime
        }
        return forum
    
@app.route("/")
def test():
    return 'welcome to forum page'

# SHOW ALL FORUM POSTS
@app.route("/all")
def all():
    forum_list = forum_db.query.all()
    if len(forum_list):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "forum": [forum.json() for forum in forum_list]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no forum posts."
        }
    ), 404

# RETRIEVE SPECIFIC FORUM POST
@app.route("/search/<int:forum_id>")
def search(forum_id):
    forum = forum_db.query.filter_by(forum_id=forum_id).first()

    #if forum exists, return forum json
    if forum:
        return jsonify(
            {
                "code": 200,
                "data": forum.json()
            }
        )
    
    #else, return error message
    return jsonify(
        {
            "code": 404,
            "message": "Post not found."
        }
    ), 404

# CREATE A FORUM POST
@app.route("/create", methods=['POST'])
def create(forum_id):

    # think can ignore
    #check if forum post is already in the db
    # if(forum_db.query.filter_by(forum_id=forum_id).first()):
    #     return jsonify(
    #         {
    #             "code": 400,
    #             "data": {
    #                 "forum_id": forum_id
    #             },
    #             "message": "Post already exists."
    #         }
    #     ), 400
    
    #else, carry on making the post
    data = request.get_json()
    forum = forum_db(**data)

    #attempt to add post into db
    try:
        db.session.add(forum)
        db.session.commit()

    #if post cannot be made, return error message
    except Exception as e:
        return jsonify(
            {
                "code":500,
                "data":{
                    "forum_id":forum_id
                },
                "message": "An error occurred when creating a post. System Error Message: " + str(e)
            }
        ), 500
    
    #if no errors, return success message
    return jsonify(
        {
            "code": 201,
            "data": forum.json(),
            "message": "Post created successfully."
        }
    ), 201

# DELETE A FORUM POST
@app.route("/delete/<int:forum_id>", methods=['DELETE'])
def delete(forum_id):
    forum = forum_db.query.filter_by(forum_id=forum_id).first()

    #check if post exists
    if forum:

        #attempt to delete post from db
        try:
            db.session.delete(forum)
            db.session.commit()

        #if post cannot be deleted, return error message
        except Exception as e:
             return jsonify(
            {
                "code": 500,
                "data": {
                    "forum_id": forum_id
                },
                "message": "An error occurred when deleting the post. System Error Message: " + str(e)
            }
        ), 500

        #if no errors, return success message
        return jsonify(
            {
                "code": 201,
                "data": forum.json(),
                "message":"Post successfully deleted."
            }
        ), 201
        
    #else, notify that the post doesn't exist
    return jsonify(
        {
            "code": 404,
            "data": {
                "forum_id": forum_id
            },
            "message": "Post not found."
        }
    )

# EDIT A POST (SEND A JSON WITH UPDATED PARTICULARS)
@app.route("/edit/<int:forum_id>", methods=['PUT'])
def edit(forum_id):
    
    forum = forum_db.query.filter_by(forum_id=forum_id).first()

    #check if post exists
    if forum:

        #attempt to edit
        try:
            data = request.get_json()

            #update fields
            forum.title = data['title']
            forum.description = data['description'] 
            forum.datetime = data['datetime'] 

            #commit changes
            db.session.commit()

            #if no errors, return success message
            return jsonify(
                {
                    "code": 200,
                    "data": forum.json(),
                    "message": "Post edited successfully. See above for updated post details."
                }
            ), 200
        
        #if post cannot be edited, return error message
        except Exception as e:
            return jsonify(
                {
                    "code": 500,
                    "data": {
                        "forum_id": forum_id
                    },
                    "message": "An error occurred while updating the post. " + str(e)
                }
            ), 500
            
    #else, notify that post does not exist
    return jsonify(
        {
            "code": 404,
            "data": {
                "forum_id": forum_id
            },
            "message": "Post not found."
        }
    ), 404



# FOR COMMENTS ROUTES
# this is to add comments to the specific post
@app.route("/comment/<int:forum_id>", methods=['GET','POST'])
def create_comment(forum_id):

    print(forum_id)
    #check if forum post is already in the db
    if(comments_table.query.filter_by(forum_id=forum_id).first()):
    
        data = request.get_json()
        forum = comments_table(**data)

        #attempt to add post into comment table
        try:
            db.session.add(forum)
            db.session.commit()

        #if post cannot be made, return error message
        except Exception as e:
            return jsonify(
                {
                    "code":500,
                    "data":{
                        "forum_id":forum_id
                    },
                    "message": "An error occurred when creating comment. System Error Message: " + str(e)
                }
            ), 500
        
        #if no errors, return success message
        return jsonify(
            {
                "code": 201,
                "data": forum.json(),
                "message": "Comment created successfully."
            }
        ), 201
        
    else:
        # forum post do not exist so ERROR 
        #else, carry on making the post
        return jsonify(
            {
                "code": 404,
                "data": {
                    "forum_id": forum_id
                },
                "message": "The forum post exists."
            }
        ), 404

if __name__ == '__main__':
    app.run(port=1113, debug=True)