# Различные версии 1С все-еще являются популярными
# поставщиками данных в организациях, в том числе
# через SOAP-сервисы, возвращающие в ответ на запрос
# структурированный XML-файл.

# Несмотря на то, что структура выдачи в каждом отдельно
# взятом случае будет различной, рассмотрим алгоритм
# работы с SOAP-сервисом, т.к. информации в открытых
# источниках по данной теме - не много.

# Документация модуля Zeep
# https://python-zeep.readthedocs.io/en/master/
# Python >=3.7. PEP8

from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Settings, Client  # pip install zeep
from zeep.transports import Transport
import MySQLdb  # pip install mysqlclient
from datetime import date
import ast
import re
import auth


def get_soap_client_number():
    """Возвращает справочник контактов клиентов из SOAP-сервиса"""
    wsdl = auth.wsdl
    user = auth.user_soap
    password = auth.password_soap

    settings = Settings(
        strict=True
        # raw_response=True  # ответ без обработки lxml-модулем
        # force_https=False
        # xml_huge_tree=True  # ограничение глубины xml-дерева
        # forbid_dtd=True
        # forbid_entities=False
        # xsd_ignore_sequence_order=True
    )

    session = Session()
    session.auth = HTTPBasicAuth(user, password)

    client = Client(
        wsdl=wsdl,
        settings=settings,
        transport=Transport(session=session)
    )

    request = client.service.ExecProcJSON('Service', params)
    result = ast.literal_eval(request)  # Предобразование строки в список словарей

    return result


def insert_vats_db():
    """Обновляет базу данных номеров клиентов (SCHEMA "vats") """
    db_vats = MySQLdb.connect(
        host=auth.host_vats, user=auth.user_vats,
        passwd=auth.passwd_vats, db=auth.db_vats, charset='utf8'
    )
    
    # Используя метод cursor() получаем объект для работы с базой
    cursor = db_vats.cursor()

    # Исполняем SQL-запрос в цикле
    for i in get_soap_client_number():
        # Определяем переменные и их значения
        entry_date = date.today()  # Дата сохранения списка в БД vats
        fio = i['ФИО']
        client = i['Контрагент']
        client_tel = re.sub(
            r"[()#%!@*-/' ']", "",
            i['Представление'][-10:]
        )

        # Задаем переменные, значения которых будут добавлены к таблице MySQL
        values = (entry_date, fio, client, client_tel)

        # Формируем запрос SQL к таблице базы данных со ссылкой на переменные
        cursor.execute("""
            INSERT INTO 
            client_number (entry_date, fio, client, client_tel)
            VALUES 
                (%s, %s, %s, %s)
        """, values)

    # Применяем изменения к базе данных
    db_vats.commit()
    db_vats.close()


insert_vats_db()
