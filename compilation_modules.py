# Pyinstaller собирает python-приложение и все зависимости в один пакет.
# В случае, если вы захотите собрать код в бинарном формате и запустить
# его на сервере, то помочь в этом может Pyinstaller.

pip install pypiwin32
pip install pyinstaller

pyinstaller --onefile --icon=name.ico --noconsole myscript.py

# name.ico - иконка бинарного дистрибутива (в папке проекта)
# --nonconsole - запуск программы в фоновом режиме
