import json
import xmltodict
import pymongo
from datetime import datetime
import base64
import bson

log_dir = './logs'


def get_config():
    try:
        return json.loads(open("./config/config1.json", "r").read())
    except Exception as error:
        print("error - {}".format(error))
        make_log("error - {}".format(error))
        return 0


def connection(config):
    try:
        client = pymongo.MongoClient(config["db_ip"], config["db_port"])
        client.admin.authenticate(config["db_uname"], config["db_pass"])
        client = client[config["db_name"]]
        return client
    except Exception as error:
        print("error - {}".format(error))
        make_log("error - {}".format(error))
        return 0


def add_transaction(client, data, collection_name):
    collection = client[collection_name]
    try:
        insert_id = collection.insert_one(data)
        return insert_id
    except Exception as error:
        print("error while inserting into database - {}".format(error))
        make_log("error while inserting into database - {}".format(error))
        return 0


def xml_to_json(data):
    return xmltodict.parse(data)


def handle_alarm(config, alarm, alarm_type, request):
    try:
        if config[alarm_type]["read_type"] == 'xml':
            alarm = xml_to_json(alarm)
            if "EventNotificationAlert" in alarm.keys():
                alarm = alarm["EventNotificationAlert"]
        else:
            alarm = json.loads(alarm)
        alarm["dateTime"] = datetime.strptime(alarm["dateTime"], '%Y-%m-%dT%H:%M:%S%z')
        alarm.update(
            {
                "has_image": config[alarm_type]["has_image"],
                "image_attached": False,
                "alarm_name": alarm_type
            }
        )

        if alarm_type == 'faceCapture':
            alarm.update({
                "image_face": bson.binary.Binary(request.files['facePicture'].read()),
                "image_full": bson.binary.Binary(request.files['faceCapturePicture'].read()),
                "image_thermal": bson.binary.Binary(request.files['thermalPicture'].read())
            })

        if alarm_type == 'TMPA':
            alarm.update({
                "image_face": bson.binary.Binary(request.files['TMPA'].read())
            })

        if alarm_type == 'TMA':
            alarm.update({
                "image_face": bson.binary.Binary(request.files['TMA'].read())
            })

        _id = add_transaction(connection(config), alarm, 'transactions')

        if _id == 0:
            return 0
        else:
            print(_id.inserted_id)
            return _id
    except Exception as error:
        print("error while handling alarm")
        make_log("error while handling alarm - {}".format(error))
        return 0


def add_image(path, taginfo, config):
    try:
        with open(path, "rb") as image:
            encoded_image = base64.b64encode(image.read())
            taginfo.update({
                "image": encoded_image
            })
            mongo_conn = connection(config)
            if mongo_conn == 0:
                return 0
            obj_id = add_transaction(mongo_conn, taginfo, 'images')
            return obj_id
    except Exception as error:
        print("error - {}".format(error))
        return 0

def make_log(string):
    string += '\n'
    with open(log_dir + '/transaction_log.txt', 'a+') as log:
        log.write(string)

if __name__ == '__main__':
    add_transaction(connection(get_config()), {"hello": 1}, 'test')
