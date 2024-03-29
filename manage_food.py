from flask import Flask, request, jsonify
from flask_cors import CORS
import os, sys
from os import environ
from invokes import invoke_http
from invoke_activity import activity_log

# sys.path.append('../microservices/food_announcement')
# import sys
# sys.path.insert(0, '../microservices/food_announcement/')

# from food_announcement import amqp_setup
# import amqp_setup

# from amqp_setup import amqp_setup
import pika
import json

app = Flask(__name__)
CORS(app)

create_post_URL = environ.get("create_food_post_URL") or 'http://127.0.0.1:1112/create_post'
user_URL = environ.get("user_URL") or "http://127.0.0.1:1111/profile"
publish_msg_URL = "http://127.0.0.1:5100/send_notif"

'''DOCUMENTATION HERE
User posts a new food post
input(json): 
{
    "username": "actual_username",
    "post_name": "actual_postname",
    "latitude": 1.296568,
    "longitude": 103.852119,
    "address": "81 Victoria St, Singapore 188065",
    "description": "long_description",
    "end_time" : "YYYY-MM-DD HH:MM:SS",
    "diets_available": ["prawn-free", "halal", "nut-free"]
    "is_available": 1
}
output(json):
{
    code: type int <- tells you the server code, 404 if error
    msg: details of the post if successful
}
'''
@app.route("/post", methods=['POST'])
def post_food():
    print('\n-----Invoking food_info microservice-----')

    if request.is_json:
        try:
            data = request.get_json()
            username = data['username']
            post_result = invoke_http(create_post_URL, method='POST', json=request.json)
            code = post_result["code"]
        
            if code not in range(200, 300):

                activity_log("food_info error")
                return {
                    "code": 500,
                    "data": {"post_result": post_result},
                    "message": "Error creating post."
                }

            # when it is successful send user details + food details

            url = user_URL + '/' + username
            print('\n-----Invoking user_info microservice-----')
            user_result = invoke_http(url, method='GET', json=request.json)
            print(user_result)
            username = user_result['data']['username']
            number = user_result['data']['number']
            email = user_result['data']['email']
            email_notif = user_result['data']['email_notif']
            sms_notif = user_result['data']['sms_notif']

            user = {

                "name": username,
                "number":number,
                "email":email,
                "email_notif": email_notif,
                "sms_notif": sms_notif
            }

            output = {

                "food": data,
                "user": user,
                "post_type": "food"
            }

            # return output
            print(f"\n this is the OUTPUT: {output} \n")
            print(f"\nthis is the output DATATYPE: {type(output)}\n")

            print('\n-----Invoking publish_message microservice-----')
            msg_result = invoke_http(publish_msg_URL, method='POST', json= output)

            return jsonify({
                "code": 201,
                "data": {
                    "Post_result": post_result,
                }
            })
        
        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            activity_log("food_info error")
            return jsonify({
                "code": 500,
                "message": "manage_food.py internal error: " + ex_str
            }), 500
    
    activity_log("post food is not json error")
    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400
    

if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
          " for managing food posts...")
    app.run(host="0.0.0.0", port=5102, debug=True)