import time
from datetime import date
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




def notify(message, userId):
    snapshot = ref.get()
    for key, val in snapshot.items():
        print('userId: {0} token: {1}'.format(key, val))
        if key == userId:
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


def checkIsAvailable(centers, center_name, user_id, _date):
    for center in centers:
        if center['name'] == center_name:
            print("Available")
            # today = date.today()
            # d1 = today.strftime("%d/%m/%Y")
            if center['sessions'][0]['available_capacity'] > 0 or center['sessions'][0]['date'] > _date:
                print("New slot Available")
                print(center['sessions'][0]['date'])
                reff.child(user_id).child(center_name).update(
                    {'isAlerted': True,
                     'slotsAvailable': center['sessions'][0]['available_capacity']
                     })
                notify("New slot Available for " + center_name + " " + center['sessions'][0]['date'], user_id)
                # print(dataSnapshot)
            else:
                print("No slot Available")
                print(center['sessions'][0]['date'])
                # notify("No slot Available for " + center_name + " " + center['sessions'][0]['date'],user_id)
                # print(json.loads(reff.child(center_name).child(user_id)))
        else:
            # print("Center not found")
            print(" ")


def getAlerts():
    dataSnapshot = reff.get()
    count = 0
    if dataSnapshot is not None:
        for key1, val1 in dataSnapshot.items():
            count = count+1
            print("Key {0} Value {1} Count {2}".format(key1, val1,count))
            for dataKey, data in val1.items():

                json_user = data
                centerName = json_user['center_name']
                userId = json_user['user_id']
                _date = json_user['date_created']
                print(json_user)
                print(centerName)
                print(json_user['district_url'])
                print(json_user['isAlerted'])
                print(userId)

                if json_user['isAlerted'] is False:
                    response_json = requests.get(json_user['district_url']).json()

                    # print(response_json['centers'])
                    checkIsAvailable(response_json['centers'], centerName, userId, _date)
                else:
                    print("Alerted")
            if count > 98:
                break

    else:
        print("No active alerts")


while True:
    getAlerts()
    time.sleep(60)
