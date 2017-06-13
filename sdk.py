import requests

def get_total_mileage(imei):
    url = "https://xxx/get-total?imei=" + imei
    return requests.get(url).json()

def get_day_mileage(imei,time,sms_filter=0):
    url = "https://xxx/daymileage?imei={}&time={}&sms_filter={}".format(imei,time,sms_filter)
    print(url)
    return requests.get(url).json()

def driver_by_name(name):
    url = "https://xxx/vehicle?driver_name="+name
    return requests.get(url).json()

def get_mileage_by_type(imei,time_epoch,mileage_type):
    """
    if unknown type, return total as default
    :param imei:
    :param time_epoch:
    :param mileage_type:
    :return:
    """

    mileage_total = get_day_mileage(imei,time_epoch)

    if mileage_type == "total":
        return mileage_total

    mileage_business = get_day_mileage(imei,time_epoch,1)

    if mileage_type == "business":
        return mileage_business

    elif mileage_type == "personal":
        return mileage_total - mileage_business
    return mileage_total

def get_imei(user_id,channel):

    if channel == "slack":
        pass
    return "868500020025128"

from slacker import Slacker

def slack_name(user_id):

    slack = Slacker('xxx')

    ul = slack.users.list()

    users = ul.body['members']

    for c_user in users:
        if not c_user['deleted'] and c_user['id'] == user_id:
            return c_user['real_name']

    return "no name"