#coding=utf-8
from http.server import BaseHTTPRequestHandler,HTTPServer
from urllib.parse import urlparse
from datetime import date,datetime,timedelta
from peewee import *
from models import *
import json

class HttpProcessor(BaseHTTPRequestHandler):
    

    def do_GET(self):
        
        parsed_path =  urlparse(self.path)
        query = {}

        query_str = parsed_path.query
        if not query_str=="":
            query_str = query_str.split("&")
            for i in query_str:
                i = i.split("=")
                query[i[0]] = i[1]
        try:
            if parsed_path.path ==  "/history":
                self.history_view(query)
            elif parsed_path.path ==  "/app":
                self.app_view(query)
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write("Not found".encode())
        except:
            self.send_response(404)
            self.end_headers()
            self.wfile.write("Not found".encode())        


    #Представление при запросах по /history
    def history_view(self,query):
        today = True
        date=query.get("date")
        # Наличие необходимых данных в запросе  
        if date ==None:
            return"null".encode()
        #Проверяем сегодняшняя ли дата и отдаем соответствующий кверисет
        date = datetime.date(datetime.strptime(date, '%d.%m.%Y'))
        if date ==datetime.date(datetime.now()):
            queryset = App_data_actual.select()
        else:
            queryset = History.select().where(History.date == date)
            today = False       
        #Формируем Json
        json_list = []
        for i in queryset:
            appid= 0
            if today:
                appid=i.appid
            else:
                appid=i.app.appid
            dict  = {
                    "id":appid,
                    "name":i.name,
                    "image":i.imageLink,
                    "link":"https://store.steampowered.com/app/{}".format(appid),
                    "position":i.position,
                    "new":i.new,
                }
            try:
                deltaPosition = i.position-History.select().where(History.date == datetime.date(datetime.now() - timedelta(days=1))).join(App_data_actual).where(App_data_actual.appid==dict["id"]).get().position
                if(deltaPosition>0):
                    deltaPosition = "+{}".format(deltaPosition) 
                else:
                      deltaPosition = str(deltaPosition)  
                dict["deltaPosition"] = deltaPosition
            except DoesNotExist :    
                pass

            json_list.append(dict)
        self.send_response(200) 
        self.send_header('content-type','application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"results":json_list}).encode())

    #Представление при запросах по /app
    def app_view(self,query):
        #Определяем фильтры запроса
        releaseDate=[query.get("filter[releaseDate][0]"),query.get("filter[releaseDate][1]")]
        try:
            releaseDate[0] = datetime.date(datetime.strptime(releaseDate[0], '%d.%m.%Y'))
        except :
            releaseDate[0] = date(1970,1,1)

        try:
            releaseDate[1] = datetime.date(datetime.strptime(releaseDate[1], '%d.%m.%Y'))
        except :
            releaseDate[1] = date(2099,1,1)

        minReviewsTotal = query.get("filter[minReviewsTotal]")
        try:
            minReviewsTotal = int(minReviewsTotal)
        except TypeError:
            minReviewsTotal = 0
        except ValueError:   
            minReviewsTotal = 0
        hasAchievements= query.get("filter[hasAchievements]")
        # Делаем запрос к базе
        if hasAchievements =="true":
            queryset = App_data_actual.select().where(App_data_actual.releaseDate >=releaseDate[0],App_data_actual.releaseDate <=releaseDate[1],App_data_actual.reviewsTotal >=minReviewsTotal,App_data_actual.achievements >0)
        elif hasAchievements =="false":
            queryset = App_data_actual.select().where(App_data_actual.releaseDate >=releaseDate[0],App_data_actual.releaseDate <=releaseDate[1],App_data_actual.reviewsTotal >=minReviewsTotal,App_data_actual.achievements ==0)
        else:
            queryset = App_data_actual.select().where(App_data_actual.releaseDate >=releaseDate[0],App_data_actual.releaseDate <=releaseDate[1],App_data_actual.reviewsTotal >=minReviewsTotal)
        #Формируем Json
        json_list = []
        for i in queryset:
            if i.achievements>0:
                achievements = True
            else:
                achievements = False
            dict  = {
                        "id":i.appid,
                        "name":i.name,
                        "image":i.imageLink,
                        "link":"https://store.steampowered.com/app/{}".format(i.appid),
                        "reviewsTotal":i.reviewsTotal,
                        "reviewsRecent":i.reviewsRecent,
                        "releaseDate":"{}.{}.{}".format(i.releaseDate.day,i.releaseDate.month,i.releaseDate.year),
                        "hasAchievements":achievements
                    }
            json_list.append(dict)
        self.send_response(200) 
        self.send_header('content-type','application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"results":json_list}).encode())



def runserver(host,port):
    serv = HTTPServer((host,port),HttpProcessor)
    serv.serve_forever()


if __name__ == '__main__':
    runserver("localhost",80)