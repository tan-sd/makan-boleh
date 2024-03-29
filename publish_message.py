from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys

import requests

import amqp_setup
import pika
import json

app = Flask(__name__)
CORS(app)

# #book_URL = "http://localhost:5000/book"
# order_URL = "http://localhost:5001/order"
# shipping_record_URL = "http://localhost:5002/shipping_record"
#activity_log_URL = "http://localhost:5003/activity_log"
#error_URL = "http://localhost:5004/error"


@app.route("/send_notif", methods=['POST'])

def send_notif():
    # data = request.get_data()
    msg_json = request.get_json()
    message_to_publish = json.dumps(request.get_json())
    print(request.get_json())

    post_type = msg_json['post_type']

    sms_notif = request.get_json()['user']['sms_notif']
    email_notif = request.get_json()['user']['email_notif']

    if post_type == "food":
        if ((sms_notif == 1) and (email_notif == 1)):
            print(sms_notif)
            print(email_notif)
            key = "smth.sms.food.email.food.smth"
        elif (sms_notif == 1):
            print(sms_notif)
            print(email_notif)
            key = "smth.sms.food.smth"
        elif (email_notif == 1):
            print(sms_notif)
            print(email_notif)
            key = "smth.email.food.smth"
    elif post_type == "forum":
        if ((sms_notif == 1) and (email_notif == 1)):
            print(sms_notif)
            print(email_notif)
            key = "smth.sms.forum.email.forum.smth"
        elif (sms_notif == 1):
            print(sms_notif)
            print(email_notif)
            key = "smth.sms.forum.smth"
        elif (email_notif == 1):
            print(sms_notif)
            print(email_notif)
            key = "smth.email.forum.smth"
   

    amqp_setup.channel.basic_publish(exchange="notification", routing_key=key, 
    body=message_to_publish, properties=pika.BasicProperties(delivery_mode = 2)) 

    success = {"code":131, "message":"the function works u fk but pls check the output"}
    return success

# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + " for placing an order...")
    app.run(host="0.0.0.0", port=5100, debug=True)
    # Notes for the parameters: 
    # - debug=True will reload the program automatically if a change is detected;
    #   -- it in fact starts two instances of the same flask program, and uses one of the instances to monitor the program changes;
    # - host="0.0.0.0" allows the flask program to accept requests sent from any IP/host (in addition to localhost),
    #   -- i.e., it gives permissions to hosts with any IP to access the flask program,
    #   -- as long as the hosts can already reach the machine running the flask program along the network;
    #   -- it doesn't mean to use http://0.0.0.0 to access the flask program.
