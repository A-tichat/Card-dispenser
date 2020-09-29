class passportScan:
    TD = "3"

    def __init__(self, data):
        data = data.replace('\n', '')
        if (len(data) > 88):
            data = data.replace(' ', '')
        firstline = data[:44]
        secoundline = data[-44:]
        # to check type of passport
        if (firstline[0] != "P"):
            raise ValueError("There is another type")

        #Ptype = firstline[1:2]

        # to check country
        self.country = firstline[2:5]
        if not checkAlpha(self.country):
            raise ValueError("Country error!")

        # to keep name and surname
        fullname = firstline[5:44]
        try:
            splitNum = fullname.index('<<')
        except ValueError:
            splitNum = len(fullname)
        self.surname = fullname[:splitNum].strip('<').replace('<', ' ')
        self.name = fullname[splitNum+2:].strip('<').replace('<', ' ')

        # to line 2 keep passport's number

        self.passportNum = secoundline[:9]
        self.c_passportNum = secoundline[9]
        if not checkDigit(self.passportNum, self.c_passportNum):
            raise ValueError("Passport number error!")

        # to keep nationality
        self.nationality = secoundline[10:13]
        if not checkAlpha(self.nationality):
            raise ValueError("Nationality error!")

        # to keep dateOfBirth
        self.dateOfBirth = secoundline[13:19]
        self.c_dateOfBirth = secoundline[19]
        if not checkDigit(self.dateOfBirth, self.c_dateOfBirth):
            raise ValueError("Birth day error!")

        # to keep sex
        self.sex = secoundline[20]
        if not checkAlpha(self.sex):
            raise ValueError("Gender error!")

        # to keep expiration date of passport
        self.expiry = secoundline[21:27]
        self.c_expiry = secoundline[27]
        if not checkDigit(self.expiry, self.c_expiry):
            raise ValueError("Expiration date error!")

        # to keep Personal number
        self.personalNum = secoundline[28:42]
        self.c_personalNum = secoundline[42]
        if not checkDigit(self.personalNum, self.c_personalNum):
            raise ValueError("Personal error!")

        # to check digit for positions
        last = secoundline[:10]+secoundline[13:20]+secoundline[21:43]
        self.checksum = secoundline[43]
        if not checkDigit(last, self.checksum):
            raise ValueError("Chacksum error!")
        print("Successfull!!")

    def detail(self):
        print("Type = "+self.TD)
        print("Name = "+self.name)
        print("Surname = "+self.surname)
        print("Passport number = "+self.passportNum.strip('<'))
        print("Nationality = "+self.nationality)
        yy = self.dateOfBirth[:2]
        mm = self.dateOfBirth[2:4]
        dd = self.dateOfBirth[4:]
        print("Date of birth = "+yy+" "+mm+" "+dd)
        print("Sex = "+self.sex)
        yy = self.expiry[:2]
        mm = self.expiry[2:4]
        dd = self.expiry[4:]
        print("Expiration date = "+yy+" "+mm+" "+dd)
        print("Personal number = "+self.personalNum.strip('<'))


def checkDigit(data, checker):
    cnum = 0
    posi = 0
    size = len(data)
    if not checker.isdigit():
        return False
    for n in data:
        value = 0
        if (n.isalpha()):
            value = ord(n)-55
        elif (n.isdigit()):
            value = int(n)
        elif (n == '<'):
            value = 0
        elif (n == ' '):
            continue
        else:
            return False

        if(posi % 3 == 0):
            cnum += value*7
        elif(posi % 3 == 1):
            cnum += value*3
        elif(posi % 3 == 2):
            cnum += value
        posi += 1
    if (int(checker) == cnum % 10):
        return True
    else:
        return False


def checkAlpha(checker):
    if checker == "D<<":
        return True
    for c in checker:
        if c == " ":
            continue
        if not c.isalpha():
            return False
    return True
