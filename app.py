import time
import firebase_admin
import requests
import json
from firebase_admin import credentials, db

cred = credentials.Certificate("ServiceAccountKey.json")
firebase_admin.initialize_app(cred, {'databaseURL': 'https://cowin-alert-2c184-default-rtdb.firebaseio.com/'})
ref = db.reference('tokens')
reff = db.reference('alerts')
serverToken = 'AAAAhqrLgjQ:APA91bECbIZ17cBTmBt8pm0tQcrQbAmbpOpJ6bEUW1-LIpHAay9wZQ0Z-cQMZbJYDACqQg5hpXKnJH7' \
              '-5C46dmDZhqLPcx24RiuViDy9O--rNl5ksfBf6z-hNy23uGs3Zge4HRqYS-IT'

'''deviceToken = 'device token here'''

snapshot = ref.get()
dataSnapshot = reff.get()


def notify(message):
    for key, val in snapshot.items():
        print('userId: {0} token: {1}'.format(key, val))
        print(val)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key=' + serverToken,
        }

        body = {
            'notification': {'title': 'Vaccine Alert !!!',
                             'body': message
                             },
            'to':
                val,
            'priority': 'high',
            #   'data': dataPayLoad,
        }
        response = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(body))
        print(response.status_code)

        print(response.json())


def checkIsAvailable(centers, center_name, user_id):
    for center in centers:
        if center['name'] == center_name:
            print("Available")
            if center['sessions'][0]['available_capacity'] > 0:
                print("New slot Available")
                print(center['sessions'][0]['date'])

                notify("New slot Available for " + center_name + " " + center['sessions'][0]['date'])
                print(dataSnapshot)
            else:
                print("No slot Available")
                print(center['sessions'][0]['date'])
                reff.child(user_id).child(center_name).update({'isAlerted': True})
                #notify("No slot Available for " + center_name + " " + center['sessions'][0]['date'])
                print(json.loads(dataSnapshot[user_id][center_name])['isAlerted'])


def getAlerts():
    if dataSnapshot is not None:
        for key1, val1 in dataSnapshot.items():
            print("Key {0} Value {1}".format(key1, val1))
            for dataKey, data in val1.items():
                json_user = json.loads(data)
                print(json_user['center_name'])
                print(json_user['district_url'])
                print(json_user['isAlerted'])
                print(json_user['user_id'])

                if json_user['isAlerted'] is False:
                    response_json = requests.get(json_user['district_url']).json()
                    # print(response_json['centers'])
                    checkIsAvailable(response_json['centers'], json_user['center_name'], json_user['user_id'])
                else:
                    print("Alerted")


while True:
    # Code executed here
    getAlerts()
    time.sleep(60)
