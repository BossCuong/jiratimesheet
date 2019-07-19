from odoo import fields
from odoo.tools import date_utils
from datetime import datetime
from dateutil import tz

def to_UTCtime(timeStr):
    timeOdoo = fields.Datetime.to_datetime(timeStr[:timeStr.find(".")].replace("T"," "))

    #hh:mm
    utcDistance = timeStr[-4:]

    utcOp = timeStr[-5]

    if utcOp == "+":
        timeOdoo = date_utils.subtract(timeOdoo,hours = int(utcDistance[:2]),minutes = int(utcDistance[2:]))
    else:
        timeOdoo = date_utils.add(timeOdoo, hours =int(utcDistance[:2]), minutes= int(utcDistance[2:]))

    return timeOdoo

def to_localTime(utcTime,timeZone):
    if not timeZone:
        timeZone = 'Asia/Ho_Chi_Minh'

    from_zone = tz.tzutc()

    to_zone = tz.gettz(timeZone)

    utcTime = utcTime.replace(tzinfo=from_zone)

    central = utcTime.astimezone(to_zone)

    return central









