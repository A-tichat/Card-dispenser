import mysql.connector

def servInit():
    global cur, con
    con = mysql.connector.connect(host='demo2.nellehliving.com',
                                database='keydispenser2',
                                user='cpe_user2',
                                password='W@rtP@ssw0rd')
    cur = con.cursor()

def servClose():
    cur.close()
    con.close()

def getroom_number(PIN):
    if (PIN=="" or ' ' in PIN):
        return None
    sqlCode = ("""select b.slot, room_number
            from kd_room as a inner join kd_keylogger as b on(a.slot=b.slot)
            where keylog='%s'""" % PIN)
    cur.execute(sqlCode)
    return  cur.fetchall()

def setkeylog(PIN):
    if (PIN=="" or ' ' in PIN):
        return None
    cur.execute("update kd_keylogger set keylog=Null where keylog='%s'" % PIN)
    con.commit()

def getroomByMRZ(personNum):
    if not personNum.isdigit():
        return None
    cur.execute("""select name_room
            from kd_checkin
            where passport=%s""" % personNum)
    return  cur.fetchall()
