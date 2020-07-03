import sqlite3
class Tag:
    @classmethod
    def getTags(cls, station):
        return [cls.gradeTag(station.grade),cls.typeTag(station['type']),cls.exitTag(station['exit'])]
    @classmethod
    def typeTag(cls,_type):
        _text=f"類別:{_type}"
        if _type=="活動":
            _class="badge badge-success badge-pill"
        else:
            _class="badge badge-dark badge-pill"
        return cls.makeTag(_class, _text)

    @classmethod
    def gradeTag(cls, grade):
        _text = f"等級:{grade}"
        if grade == "特殊站":
            _class = "badge badge-danger badge-pill"
        else:
            _class = "badge badge-primary badge-pill"
        return cls.makeTag(_class, _text)

    @classmethod
    def exitTag(cls, exit):
        _text=f"出口:{exit}"
        _class= "badge badge-warning"
        return cls.makeTag(_class, _text)

    @staticmethod
    def makeTag(_class,text):
        return {'class':_class,'text':text}
class Line:
    @staticmethod
    def toEN(line_name_zh):
        conn=get_db_connection()
        ENname=conn.execute(f"SELECT lineEN FROM line_name WHERE lineZH='{line_name_zh}'").fetchone()['lineEN']
        return ENname
    @classmethod
    def getLine(cls,lineList):
        return [{'name':line,'imgSRC':f'img/{cls.toEN(line)}.png'} for line in lineList]
def get_db_connection():
    conn=sqlite3.connect('stations.sqlite')
    conn.row_factory=sqlite3.Row
    return conn