from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
import sys, os
from os import environ
from invokes import invoke_http
from invoke_activity import activity_log
app = Flask(__name__)
CORS(app)

forum_URL = 'http://localhost:1115/all'
create_forum_URL = environ.get("create_URL") or 'http://localhost:1115/create'
find_forum_URL = environ.get("find_URL") or 'http://localhost:1115/search_id'
user_URL = environ.get("user_URL") or 'http://localhost:1111/profile'
create_comment_URL = environ.get("create_comment_URL") or 'http://localhost:1115/create_comment'
notification_URL = environ.get("notification_URL") or 'http://localhost:5100/send_notif' 


'''
Function: to create a post in forum
Input: 
{          
    "username": "tommy",
    "title": "free french fries",
    "description": "I had a party just now! You are welcome to join.",
    "datetime": "2021-01-01 15:10:10",
    "is_available": 1,
}
Output: 
return jsonify(result), result["code"]
and result is 
return {
        "code": 201,
        "data": {
            "forum_result": 
                 {
                    "code": 201,
                    "data": 
                        {
                            'forum_id': forum_id,
                            'commentor_username': commentor_username,
                            'comment': comment,
                            'datetime': datetime
                        },
                    "message": "Post created successfully."
                }
        }
    }
    
'''
@app.route("/create_post", methods=['POST'])
def create_forum_post():
    print("create_post route accessed! ==============")
    if request.is_json:
        try:
            post_details = request.get_json()
            print("\nReceived post details in JSON:", post_details)

            # do the actual work
            print(post_details)
            result = create_post(post_details)
            return jsonify(result), result["code"]

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)
            activity_log("food_info error")

            return jsonify({
                "code": 500,
                "message": "manage_forum.py internal error: " + ex_str
            }), 500

    # if reached here, not a JSON request.
    activity_log("create post is not json error")
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400


# create forum post function
def create_post(post_details):

    print('\n-----Invoking forum microservice-----')
    print(post_details)
    # url = create_forum_URL + '/create/' + str(post_details['post_id'])

    forum_result = invoke_http(create_forum_URL, method='POST', json=post_details)
    activity_log("forum_info") #to put in activity log
    print('forum_result:', forum_result)

    # Check the food result; if a failure, send it to the error microservice.
    code = forum_result["code"]
    if code not in range(200, 300):
        activity_log("forum_info_error")
        return {
            "code": 500,
            "data": {"forum_result": forum_result},
            "message": "Retrieve forum failure sent for error handling."
        }
    
    return {
        "code": 201,
        "data": {
            "forum_result": forum_result
        }
    }


'''
Function: create comments
Input: {
    forum_id: 1,
    commentor_username: "SJB123",
    comment: "This is a coment",
    datetime: "2021-01-01 15:10:10"
}
Output: 
return jsonify(result), result["code"]
and result is 
return {
        "code": 201,
        "data": {
            "forum_result": 
                 {
                    "code": 201,
                    "data": 
                        {
                            'forum_id': forum_id,
                            'commentor_username': commentor_username,
                            'comment': comment,
                            'datetime': datetime
                        },
                    "message": "Post created successfully."
                }
        }
    }
'''

@app.route("/create_comment", methods=['POST'])
def create_comment():
    # Breaks if no json given
    if not request.is_json:
        print("create comment is not json")

        return jsonify({
            "code": 400,
            "message": "Invalid JSON input: " + str(request.get_data())
        }), 400
    
    # If json given
    try:
        print("Valid JSON passed, running create_comment()")
        comment_details = request.get_json()
        print("\nReceived post details in JSON:", comment_details)

        print("'\n-----Invoking forum microservice-----'")
        # invoke forum info to push to DB
        result = push_new_comment(comment_details)
        print(result)
        #invoke forum info to get forum information
        forum_id = result["data"]["data"]["forum_id"]
        url = find_forum_URL + "/" + str(forum_id)  
        forum_json = invoke_http(url,method='GET')

        print("Forum Json: ", forum_json)

        username = forum_json["data"]["username"]
        print(' username of poster is')
        print(username)
        forum_info = forum_json["data"]
        print("'\n-----Username Retrieved-----'")

        #invoke user info to get user information 
        print("'\n-----Invoking user microservice-----'")
        username_URL = user_URL + "/" + username
        user_json = invoke_http(username_URL, method='GET')
        print("'\n-----User information retrieved-----'")
        print("User Info: ", user_json)


        print('user json below')
        print(user_json)
        #invoke notification
        #prepare information for notification service
        json_to_send = {
            "post": forum_info,
            "comment": comment_details,
            "user":{
                "name":username,
                "number": user_json["data"]["number"],
                "email": user_json["data"]["email"],
                "sms_notif": user_json["data"]["sms_notif"],
                "email_notif":user_json["data"]["email_notif"]

            },
            "post_type": "forum"
        }

        #invoke notification
        print("'\n-----Invoking notification microservice-----'")
        success = invoke_http(notification_URL,method='POST',json=json_to_send)
        print(success)

        print(json_to_send)
        return jsonify(result['data']), result["code"]

    except Exception as e:
        # Unexpected error in code
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
        print(ex_str)
        activity_log("forum_info error")

        return jsonify({
            "code": 500,
            "message": "manage_forum.py internal error: " + ex_str
        }), 500
    
def push_new_comment(comment_details):
    print("push_new_comment(", comment_details, '"')

    create_comment_result = invoke_http(create_comment_URL, method='POST', json = comment_details)
    activity_log("forum") #to put in activity log

    print('checkout create comment')
    print(create_comment_result)
    # If a failure, send it to the error microservice
    code = create_comment_result["code"]
    
    if code not in range(200, 300):
        # 7. Return error
        activity_log("forum_info error")
        return {
            "code": 500,
            "data": create_comment_result,
            "message": "Retrieve forum failure sent for error handling."
        }
    else:
        return {
            "code": 201,
            "data": create_comment_result,
        }

if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
          " for managing forum posts...")
    app.run(host="0.0.0.0", port=5103, debug=True)