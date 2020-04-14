# Тестирование работы функционала модулей
# выгрузки истории вызовов

import pandas as pd
import get_db_maxdatetime as mdt
import get_callHistory as hst

unix_from = int(mdt.get_db_maxdatetime()[0] + 1)

print(
    'Максимальное время вызова в локальной базе::',
    '( UnixTime:', mdt.get_db_maxdatetime()[0],
    'DateTime:', mdt.get_db_maxdatetime()[1], ') ',
    'Выгрузка истории вызовов с:', unix_from
)

dict_calls = []

for idi in hst.get_user_id():
    result = hst.call_history(idi, f'{unix_from}000', 'null')  # API ВАТС требует 13-ти значного формата unixTime

    for i in result:
        dict_calls.append(i)

data = pd.DataFrame(dict_calls)
print(
    'Минимальное время в выгрузке истории::',
    '( UnixTime:', str(min(data['callTime']))[:10],
    'DateTime:', mdt.convert_ut_to_dt(
        int(str(min(data['callTime']))[:10])
    ), ') '
)
