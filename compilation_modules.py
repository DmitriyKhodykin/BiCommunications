# Pyinstaller builds a python application and all the dependencies in one package
# In case you want to collect the code in binary format and run it on the server, 
# then Pyinstaller can help

# pip install pypiwin32
# pip install pyinstaller

pyinstaller --onefile --icon=name.ico --noconsole myscript.py

# name.ico - binary distribution icon (in the project folder)
# --nonconsole - running the program in the background
