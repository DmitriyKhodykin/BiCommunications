# Модуль выгрузки списка абенентов
# виртуальной АТС (ВАТС) в локальную базу данных
# для постоянного хранения и аналитики изменений
# python >= 3.7. PEP8


import requests
import json
import time
from datetime import date
import MySQLdb  # pip install mysqlclient


# Ресурс и данные для авторизации
token = '****'
url_abonents = 'https://vpbx.mts.ru/api/abonents'


def abonetns_dict():
    """Возвращает справочник абонентов ВАТС в формате:
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


# Код для работы с базой данных MySQL на стороне клиента ВАТС (SCHEMA "vats")
def insert_vats_db():
    """Обновляет базу данных номеров мобильных телефонов абонентов"""
    
    db_vats = MySQLdb.connect(host="****", user="****", passwd="****", db="vats", charset='utf8')
    # Используя метод cursor() получаем объект для работы с базой
    cursor = db_vats.cursor()
    
    # Исполняем SQL-запрос в цикле
    
    for i in abonetns_dict():
        # Определяем переменные и их значения
        entry_date = date.today()  # Дата сохранения списка в "vats"
        user_id = i['userId']
        user_name = i['firstName']
        user_departament = i['lastname']  # Стандартное поле департамента отсутсвует в API
        user_number = i['phoneNumber']
        user_ext = i['extension']

        # Задаем переменные, значения которых будут добавлены к таблице MySQL
        values = (entry_date, user_id, user_name, user_departament, user_number, user_ext)
        
        # Формируем запрос SQL к таблице базы данных со ссылкой на переменные
        cursor.execute("""
            INSERT INTO 
            vats_abonents (entry_date, user_id, user_name, user_departament, user_number, user_ext)
            VALUES 
                (%s, %s, %s, %s, %s, %s)
        """, values)

    # Применяем изменения к базе данных
    db_vats.commit()
    db_vats.close()


while True:
    insert_vats_db()
    time.sleep(86600)  # Раз в сутки обновляем справочник абонентов
    
