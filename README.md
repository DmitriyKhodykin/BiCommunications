# BI-communications
## Designing BI analytics of the communication activity of the organization’s employees: MTS VATS + MySQL + Power BI

<b>TARGET</b> - building BI-analytics of communication activity of employees of a commercial organization for:
- prevention of decline in activity by key customers
- effective distribution of customer base among employees
- analysis of the structure of employee activity in the internal / external social environment
- etc.

Within the framework of the project, a number of modules in the Python programming language have been developed that are able to collect, pre-process and store information from various sources, such as:
- organization web services
- virtual аutomatic telephone exchange (VATE) from MTS (russian mobile provider)

into a single local database - for subsequent operational analysis on the MS Power BI platform https://powerbi.microsoft.com/ru-ru/

![PIPELINE](https://downloader.disk.yandex.ru/preview/04ae3ff657d47a5c0a49b28f964f28bd83457d02d1b8f11c54553e2bdbb69854/5e715499/JFsqCvxIsN3HRKAMTNXce63rvt4OiXCrUtMBJEWaHz8Up6P6rUti2VtsEJjTMyj5lN3EP5ffj6N4f1ISgTec5Q==?uid=0&filename=REP_pipeline.png&disposition=inline&hash=&limit=0&content_type=image%2Fpng&tknv=v2&owner_uid=181432056&size=2048x2048)

The repository contains the following blocks of program code:
- auth.py - resource for authorization for various services / databases
- get_abonents_dict.py - module for uploading a list of subscribers of a VATE to the local database (see SCHEMA_vats.txt)
- get_callHistory.py - module for loading call history from the VATE to the local database with a given frequency
- get_db_maxdatetime.py - a helper module that returns the maximum date-time, which is stored in the SCHEMA "vats"
- get_clients_numbers.py - a module that demonstrates work with a SOAP service that delivers data from an accounting ERP system 
- compilation_modules.py - instructions for compiling code (if necessary)
- test_call_history.py - testing the functionality of the call history upload modules

The result of the project is an interactive reporting system, for example:

![PBI](https://gcits.com/wp-content/uploads/PowerBIDashboardPhoneCalls.png)
