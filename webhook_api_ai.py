from __future__ import print_function
import json
import os
import random

import time
from dateutil import parser

from flask import Flask
from flask import request
from flask import make_response

from onlicar_sdk import *

app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print(" ===========  Request ============")
    print(json.dumps(req, indent=4))

    res = process_request(req)

    res = json.dumps(res, indent=4)
    print(" ============ Response =============")
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def choose_phrase(action):
    return random.choice(open(os.path.join("phrases",action),"r").read().split("\n"))

def process_request(req):
    action = req.get("result").get("action")

    name = None
    source = None

    if "originalRequest" in req:
        source = req.get("originalRequest").get("source")
        user_id = req["originalRequest"]["data"]["event"]["user"]

        if source == "slack":
            name = slack_name(user_id)

    if action == "input.welcome":
        if name is not None:
            return {"followupEvent": {"name": "user_id", "data": {"name": name}}}
        return {}

    if action == "mileage_q":
        if source is not None:
            imei = get_imei(name, source)
        else:
            imei = "868500020025128"

        date = req["result"]["parameters"]["time"]["date-time"]
        datetime = parser.parse(date)
        time_epoch = int(datetime.strftime('%s'))

        current_time = time.time()

        if time_epoch > current_time:
            return response_output("I can do many things, but I can't look into the future! (yet)")


        mileage_type = req["result"]["parameters"]["mileage_type"]

        mileage = get_mileage_by_type(imei,time_epoch,mileage_type)

        mileage_types = ["total","business","personal"]

        if mileage_type not in mileage_types:
            response = "Not sure which type of mileage you requested. Your overall mileage was {}".format(mileage)
            return response_output(response)

        params = {
            "mileage": round(mileage,1),
            "date" : date,
            "type" : mileage_type,
        }

        response = "Your {type} mileage on {date} is {mileage}.".format(**params)
        #choose_phrase(action).format(**params)

        return response_output(response)

    if action == "mileage":
        if source is not None:
            imei = get_imei(name, source)
        else:
            imei = "868500020025128"

        date = req["result"]["parameters"]["time"]["date-time"]
        datetime = parser.parse(date)
        time_epoch = int(datetime.strftime('%s'))

        current_time = time.time()

        if time_epoch > current_time:
            return response_output("I can do many things, but I can't look into the future! (yet)")


        mileage_type = req["result"]["parameters"]["mileage_type"]

        mileage = get_mileage_by_type(imei,time_epoch,mileage_type)

        mileage_types = ["total","business","personal"]

        if mileage_type not in mileage_types:
            response = "Not sure which type of mileage you requested. Your overall mileage was {}".format(mileage)
            return response_output(response)

        params = {
            "mileage": round(mileage,1),
            "date" : date,
            "type" : mileage_type,
        }

        response = "Your {type} mileage on {date} is {mileage}.".format(**params)
        #choose_phrase(action).format(**params)

        return response_output(response)

    print("unknown action",action)

    return response_output("Hmm.. looks like something went wrong there. Can you try again for me? ")

def response_output(message): return {
            "speech": message,
            "displayText": message,
            "source": "apiai-mileage-webhook-onlicar"
        }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0')