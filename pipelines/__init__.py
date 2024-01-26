from hashlib import sha256

def clean_str(str):
    newval= str.replace('"', '""')
    if newval == '':
       return "NULL"
    if newval == 'True':
        newval = 1
    if newval == 'False':
        newval = 0
    return "\"{0}\"".format(newval)

def create_id(played_at, artist, title, source): 
    key = "{0}{1}{2}{3}".format(played_at, artist, title, source)
    m = sha256()
    m.update(key.encode("UTF-8"))
    return m.hexdigest()