from flask import Flask, request, send_file, Response
from functions import *
from time import sleep
import os
from bson.objectid import ObjectId

app = Flask(__name__)
UPLOAD_FOLDER = os.getcwd() + '/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/hikdata', methods=['POST'])
def receive_data():
    if request.method == 'GET':
        print(request.data)
        return ''
    else:
        global config
        try:

            print(request.files)
            print(request.form)

            for alarm_type in config["allowed_alarms"]:
                if str(request.form.get(alarm_type)) != 'None':
                    print(alarm_type)
                    handle_alarm(config, request.form.get(alarm_type), alarm_type, request)
                    return ''
                else:
                    continue

        except Exception as e:
            print("error")
            print("{}".format(e))
        return ''


@app.route('/get_image/<image_type>/<_id>', methods=['GET'])
def get_image(_id, image_type):
    response = Response()
    try:
        response.headers['content-type'] = 'image/jpeg'
        conn = connection(get_config())
        collection = conn['transactions']
        results = collection.find_one({"_id": ObjectId(str(_id))})
        response.data = results[image_type]
        return response
    except Exception as err:
        response.headers['content-type'] = 'text/plain'
        print(err)
        response.data = err
        return 'error'


if __name__ == '__main__':
    global config

    if 'logs' not in os.listdir("./"):
        os.mkdir('./logs')

    while True:
        config = get_config()
        if config == 0:
            make_log("error while reading config file")
            print("error while reading config file")
        else:
            break
        sleep(3)

    app.run(host='0.0.0.0', port=int(config["port"]))
