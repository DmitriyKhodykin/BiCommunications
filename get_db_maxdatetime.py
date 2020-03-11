# Модуль возвращает максимальную дату-время,
# которая хранится в истории вызовов SCHEMA "vats"
# Python >= 3.7. PEP8

import MySQLdb  # pip install mysqlclient
import time
import datetime


def convert_ut_to_dt(ut):
    """Конвертирует UnixTime в DateTime"""
    dt = datetime.datetime.fromtimestamp(
        ut
    ).strftime('%Y-%m-%d %H:%M:%S')
    return dt


def get_db_maxdatetime():
    """Возвращает максимальную дату-время в истории вызовов,
    которая хранится в локальной базе данных (SCHEMA "vats")"""
    
    db_vats = MySQLdb.connect(
        host="****", user="****", passwd="****", db="vats", charset='utf8'
    )
    
    # Используя метод cursor() получаем объект для работы с базой
    cursor = db_vats.cursor()
    
    # Формируем SQL запрос к базе данных
    cursor.execute("""
        SELECT max(callTime)
        FROM call_history
    """)

    db_vats.commit()
    db_vats.close()

    maxdatetime = cursor.fetchall()
    maxdatetime_unix = int(
        time.mktime(maxdatetime[0][0].timetuple())
    )
    maxdatetime_dt = convert_ut_to_dt(
        maxdatetime_unix
    )

    return maxdatetime_unix, maxdatetime_dt
    
