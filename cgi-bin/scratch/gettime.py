#!/usr/bin/python
import datetime

def gettime():
    utc_datetime = datetime.datetime.utcnow()
    timeStamp = utc_datetime.strftime("%Y%m%dT%H%M%S")
    return timeStamp

