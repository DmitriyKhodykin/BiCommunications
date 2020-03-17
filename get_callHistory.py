# The call history on the server is stored for 3 months, 
# it is necessary to periodically reload information from the VATE to the local database

# GET request parameters to the server https://vpbx.mts.ru
# История вызовов:
# "abonentId" - Caller ID for which the call history is uploaded (required)
# "callDirection" - call direction, may take the following values:
#     = "ORIGINATING" - outgoing call
#     = "TERMINATING" - incoming call
#     = null - no filter
# "callStatus" - call status, may take the following values:
#     = "PLACED" - held call
#     = "MISSED" - missed call
#     = null - no filter
# "calledNumber" - outgoing number, null - no filter
# "callingNumber" - incoming number, null - no filter
# "dateFrom" - start date of filtering, in the format unixtimestamp
# "dateTo" - end date of filtering, in the format unixtimestamp
# Dates can be null, in this case the call history for the last day is returned

# Python >= 3.7. PEP8

import requests
import MySQLdb  # Local database - MySQL
import json
import datetime
import get_db_maxdatetime as mdt
import get_abonents_dict as gad
import auth


def get_user_id():
    """Returns the Id list of VATE users"""

    user_ids = []  # Список Id абонентов ВАТС
    for abonent in gad.abonetns_dict():
        user_ids.append(abonent['userId'])
    return user_ids


def call_history(uid, date_from, date_to):
    """Returns the history of calls"""

    payload = f'''{{"abonentId": {uid}, 
                    "callDirection": null, 
                    "callStatus": null, 
                    "calledNumber": null, 
                    "callingNumber": null, 
                    "dateFrom": {date_from}, 
                    "dateTo": {date_to}}}'''

    headers = {
        'Content-Type': 'application/json',
        'cache-control': 'no-cache',
        'X-AUTH-TOKEN': auth.token
    }

    response = requests.request("GET", url_callHistory, headers=headers, data=payload)
    return json.loads(response.text.encode('utf8'))


# Setting the date-time of the start of the call history upload period
unix_from = int(mdt.get_db_maxdatetime()[0] + 1)


def insert_vats_db():
    """Updates the call history of employees in the local database"""
    
    db_vats = MySQLdb.connect(
        host=auth.host_vats, user=auth.user_vats,
        passwd=auth.passwd_vats, db=auth.db_vats, charset='utf8'
    )
    
    # Using the cursor () method to get an object for working with the database
    cursor = db_vats.cursor()
    
    # Using SQL query in a loop
    for idi in get_user_id():
        result = call_history(idi, f'{unix_from}000', 'null')  # 13 digit UnixTime
        for i in result:
            user_id = i['userId'][:10]
            call_time = datetime.datetime.fromtimestamp(
                int(str(i['callTime'])[:10])
            ).strftime('%Y-%m-%d %H:%M:%S')
            calling_number = i['callingNumber'][1:]
            called_number = i['calledNumber'][1:]
            duration = i['duration']
            direction = i['direction']
            status = i['status']
            answer_duration = i['answerDuration']
            termination_cause = i['terminationCause']
            ext_tracking_id = i['extTrackingId']

            # Defining variables whose values will be added to the MySQL table
            values = (
                user_id, call_time, calling_number, called_number, duration, direction, status, answer_duration,
                termination_cause, ext_tracking_id
            )
            # Generating a SQL query on a database table with reference to variables
            cursor.execute("""
                INSERT INTO
                call_history (userId, callTime, callingNumber, calledNumber, duration, direction, status, 
                answerDuration, terminationCause, extTrackingId)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, values)

    # Apply changes to the database
    db_vats.commit()
    db_vats.close()


while True:  # Addition of call history every 3 hours in the local database
    insert_vats_db()
    time.sleep(10800)
    
