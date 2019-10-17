#coding=utf-8
from peewee import *
from datetime import datetime, date


BASE = SqliteDatabase('aps.db')
#актуальные данные
class App_data_actual(Model):
    appid = PrimaryKeyField(primary_key=True,verbose_name = "app_id" )
    name = CharField()
    position = IntegerField(default=-1)
    releaseDate = DateField(default=None,null=True)
    reviewsTotal = IntegerField(default = 0)
    reviewsRecent = IntegerField(default = 0)
    achievements = IntegerField(default = 0)
    imageLink = CharField(default = None,null=True)
   

    new = BooleanField(default = True)
    
    class Meta:

        db_table = "App_data_actual"
        database = BASE  


#История
class History(Model):
    app = ForeignKeyField(App_data_actual, related_name='app', to_field='appid', on_delete='cascade',on_update='cascade')
    position = IntegerField(default=-1)
    name = CharField()
    date = DateField(default=datetime.date(datetime.now()))
    reviewsTotal = IntegerField(default = 0)
    reviewsRecent = IntegerField(default = 0)
    imageLink = CharField(default = None)
    achievements = IntegerField(default = 0)
    new = BooleanField(default = False)
    class Meta:
        db_table = "History"
        database = BASE




#Создание базы данных

if __name__ == "__main__":
    try:
        App_data_actual.create_table()
    except peewee.OperationalError:
        print ("App_data_actual table already exists!")
 
    try:
        History.create_table()
    except peewee.OperationalError:
        print ("History table already exists!")