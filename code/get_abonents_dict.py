# Module for loading a list of VATE subscribers to a local database
# for permanent storage and change analysis
# python >= 3.7. PEP8


import requests
import json
import time
from datetime import date
import MySQLdb  # pip install mysqlclient
import auth


def abonetns_dict():
    """Returns the dict of subscribers in the format:
    [{'serviceProviderId': 8888888888, 'groupId': 8888888888, 'userId': 8888888888,
    'firstName': 'Анна Ивановна', 'lastname': 'Иванова ', 'phoneNumber': '8888888888',
    'extension': '172', 'callingLineIdPhoneNumber': '8888888888', 'department':
    'Наименование', 'email': ''}...]"""
    
    payload_abonents = {
        'X-AUTH-TOKEN': auth.token,
        'cache-control': 'no-cache'
    }
    r_abonents = requests.get(url_abonents, params=payload_abonents).text
    abonents_dict = json.loads(r_abonents)

    return abonents_dict


# Code for working with MySQL database on the VATE client side (SCHEMA "vats")
def insert_vats_db():
    """Updates the database of mobile phone numbers of subscribers"""
    
    db_vats = MySQLdb.connect(
        host=auth.host_vats, user=auth.user_vats, 
        passwd=auth.passwd_vats, db=auth.db_vats, charset='utf8'
    )
    # Using the cursor () method, we get an object for working with the database
    cursor = db_vats.cursor()
    
    # Execute the SQL query in a loop
    for i in abonetns_dict():
        # Define variables and their values
        entry_date = date.today()  # Date the list was saved in "vats"
        user_id = i['userId']
        user_name = i['firstName']
        user_departament = i['lastname']
        user_number = i['phoneNumber']
        user_ext = i['extension']

        # Set the variables whose values will be added to the MySQL table
        values = (entry_date, user_id, user_name, user_departament, user_number, user_ext)
        
        # Form the SQL query to the database table with reference to the variables
        cursor.execute("""
            INSERT INTO 
            vats_abonents (entry_date, user_id, user_name, user_departament, user_number, user_ext)
            VALUES 
                (%s, %s, %s, %s, %s, %s)
        """, values)

    # Apply changes to the database
    db_vats.commit()
    db_vats.close()


while True:
    insert_vats_db()
    time.sleep(86600)  # Once a day we update the dict of subscribers
    
