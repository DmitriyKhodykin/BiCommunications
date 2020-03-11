# Поскольку история вызовов на сервере МТС хранится 3 мес,
# то необходимо периодически перегружать информацию из ВАТС
# в локальную базу данных (находящуюся на стороне пользователя ВАТС)

# Параметры GET-запроса к серверу https://vpbx.mts.ru
# История вызовов:
# "abonentId" - идентификатор абонента для которого выгружается история вызовов (обязательный параметр)
# "callDirection" - направление вызова, может принимать значения:
#     = "ORIGINATING" - исходящий звонок
#     = "TERMINATING" - входящий звонок
#     = null - фильтр отсутствует
# "callStatus" - статус вызова, может принимать значения:
#     = "PLACED" - состоявшийся звонок
#     = "MISSED" - пропущенный звонок
#     = null - фильтр отсутствует
# "calledNumber" - исходящий номер, null - фильтр отсутствует
# "callingNumber" - входящий номер, null - фильтр отсутствует
# "dateFrom" - начальная дата фильтрации, в формате unixtimestamp
# "dateTo" - конечная дата фильтрации, в формате unixtimestamp
# Даты могут быть null, в таком случае возвращается история вызовов за последние сутки

# Python >= 3.7. PEP8

import requests
import MySQLdb  # Локальная база данных - MySQL
import json
import datetime
import time
import get_db_maxdatetime as mdt

# Ресурс и данные для авторизации
token = '****'
url_abonents = 'https://vpbx.mts.ru/api/abonents'
url_callHistory = 'https://vpbx.mts.ru/api/callHistory'


def abonetns_dict():
    """Возвращает справочник абонентов ВАТС МЖД в структуре:
    [{'serviceProviderId': 8888888888, 'groupId': 8888888888, 'userId': 8888888888,
    'firstName': 'Анна Ивановна', 'lastname': 'Иванова ', 'phoneNumber': '8888888888',
    'extension': '172', 'callingLineIdPhoneNumber': '8888888888', 'department':
    'Наименование', 'email': ''}...]"""
    
    payload_abonents = {
        'X-AUTH-TOKEN': token,
        'cache-control': 'no-cache'
    }
    r_abonents = requests.get(url_abonents, params=payload_abonents).text
    abonents_dict = json.loads(r_abonents)
    return abonents_dict


def get_user_id():
    """Возвращает перечень Id абонентов ВАТС МТС"""
    
    user_ids = []  # Список Id абонентов ВАТС
    for abonent in abonetns_dict():
        user_ids.append(abonent['userId'])
    return user_ids


def call_history(uid, date_from, date_to):
    """Возвращает историю вызовов в разрезе абонентов ВАТС МТС"""

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
        'X-AUTH-TOKEN': token
    }

    response = requests.request("GET", url_callHistory, headers=headers, data=payload)
    return json.loads(response.text.encode('utf8'))


# Установка даты-времени начала периода выгрузки истории вызовов
# максимальное время вызова, уже содержащееся в локальной базе данных
# + 1 секунда в формате UnixTime
unix_from = int(mdt.get_db_maxdatetime()[0] + 1)


def insert_vats_db():
    """Обновляет историю вызовов сотрудников в ВАТС МТС в локальной базе"""
    
    db_vats = MySQLdb.connect(host="****", user="****", passwd="****", db="****", charset='utf8')
    
    # Использование метода cursor() для получения объекта для работы с базой
    cursor = db_vats.cursor()
    
    # Использование SQL-запроса в цикле
    for idi in get_user_id():
        result = call_history(idi, f'{unix_from}000', 'null')  # API ВАТС требует 13-ти значного формата unixTime
        for i in result:
            user_id = i['userId'][:10]  # Приведение в соотв. с номером абонента ВАТС (без +7)
            call_time = datetime.datetime.fromtimestamp(
                int(str(i['callTime'])[:10])  # Выделение 10-ти значного кода unixTime для конвертации в datetime
            ).strftime('%Y-%m-%d %H:%M:%S')
            calling_number = i['callingNumber'][1:]
            called_number = i['calledNumber'][1:]
            duration = i['duration']
            direction = i['direction']
            status = i['status']
            answer_duration = i['answerDuration']
            termination_cause = i['terminationCause']
            ext_tracking_id = i['extTrackingId']

            # Определение переменных, значения которых будут добавлены к таблице MySQL
            values = (
                user_id, call_time, calling_number, called_number, duration, direction, status, answer_duration,
                termination_cause, ext_tracking_id
            )
            # Формирование запроса SQL к таблице базы данных со ссылкой на переменные
            cursor.execute("""
                INSERT INTO
                call_history (userId, callTime, callingNumber, calledNumber, duration, direction, status, 
                answerDuration, terminationCause, extTrackingId)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, values)

    # Применение изменений к базе данных
    db_vats.commit()
    db_vats.close()


while True:  # Дополнение истории вызовов каждые 3 часа в локальной базе
    insert_vats_db()
    time.sleep(10800)
    
