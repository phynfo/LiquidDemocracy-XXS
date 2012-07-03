from time import strptime
from datetime import datetime
import re


def date_diff(older, newer):
    """
    Returns a humanized string representing time difference

    The output rounds up to days, hours, minutes, or seconds.
    4 days 5 hours returns '4 Tage'
    0 days 4 hours 3 minutes returns '4 Stunden', etc...
    """
    timeDiff = newer - older
    days = timeDiff.days
    hours = timeDiff.seconds/3600
    minutes = timeDiff.seconds%3600/60
    seconds = timeDiff.seconds%3600%60
    str = ""
    tStr = ""
    if days > 0:
        if days == 1:   tStr = "Tag"
        else:           tStr = "Tagen"
        str = str + "%s %s" %(days, tStr)
        return str
    elif hours > 0:
        if hours == 1:  tStr = "Stunde"
        else:           tStr = "Stunden"
        str = str + "%s %s" %(hours, tStr)
        return str
    elif minutes > 0:
        if minutes == 1:tStr = "Minute"
        else:           tStr = "Minuten"           
        str = str + "%s %s" %(minutes, tStr)
        return str
    elif seconds > 0:
        if seconds == 1:tStr = "Sekunden"
        else:           tStr = "Sekunde"
        str = str + "%s %s" %(seconds, tStr)
        return str
    else:
        return None

def compact(s): 
  ''' return the first few words of the text s in order to produce 
      a short description of an entry's or comment's text '''
  s2 = filter(lambda c: c!='\n', s)
  return re.match(r'.*\s',s2).string + ' ... '


