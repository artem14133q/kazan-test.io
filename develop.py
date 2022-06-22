import os
import time

FILE_NAME = "index.template.html"

def get_timestamp() -> int:
    return int(str(os.path.getmtime(FILE_NAME)).split('.')[0])

def start_build():
    os.system('python3 build.py')

last_changed_date = get_timestamp()

while True:
    time.sleep(1)
    current_changed_date = get_timestamp()

    if current_changed_date != last_changed_date:
        start_build()
        print('Build suceess!')
        print('=============================')

        last_changed_date = current_changed_date
