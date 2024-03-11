import time

from settings import LOGFILE_PATH, DEBUGFILE_PATH

CURRENT_HOUR = lambda: time.localtime().tm_hour
CURRENT_MIN = lambda: time.localtime().tm_min

CURRENT_TIME = lambda: f"[{time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec}]"
CURRENT_DATE = lambda: f"[{time.localtime().tm_mon}/{time.localtime().tm_mday}/{time.localtime().tm_year}]"

def log(*content, timestamp = True, datestamp = True, sep = " ", logfile = DEBUGFILE_PATH):
    content = sep.join(content)
    if timestamp:
        content = CURRENT_TIME() + " " + str(content)
    if datestamp:
        content = CURRENT_DATE() + " " + str(content)
        
    print(content)
            
    open(logfile, "a").write(
        str(content) + "\n"
    )
