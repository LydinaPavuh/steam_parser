#coding=utf-8
from threading import Thread
import requests
from lxml import html
import re
import random
import time
from peewee import *
from models import *
import os.path
from datetime import date,datetime


PAUSES = True
#Юзер агенты с ними намного меньше банит, также принимаем и отправляем куки
#При использовании хороших впн или прокси (без дисконектов) банов не будет даже с отключенными задержками
#Без впн количество непросмотренных приложений зависит от частоты запросов (при частоте раз в сутки больших серий банов быть не должно),необходимо использование рандомых пауз между запросами
#Пропущенные страницы востанавливаются после завершения основного парсинга

USER_AGENTS = [
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0",
"Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0",
"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:68.0) Gecko/20100101 Firefox/68.0"
]


ID_CONTAINER ="onmouseover"#Тег содержащий ID  приложения
bad_elems =[]
# Записываем в базу
def Write_in_database(app):
    app_data = App_data_actual.get_or_none(App_data_actual.appid == app["id"])
    if app_data is None:
        try:#Бывают несколько форматов
            date = datetime.date(datetime.strptime(app["release_date"], '%d %b, %Y'))
        except ValueError:
            try: # Как выяснилось некоторые даты релиза вообще не читаемы (названия месяцев бывают на разных языках(Польский,Японский и другие нечитабельные) либо вообще не существующие)
                date = datetime.date(datetime.strptime(app["release_date"], '%b %d, %Y'))
            except ValueError:
                date = None    
        #Если совпадает с насоящий датой - новое
        if date == datetime.date(datetime.now()):
            new =True
        else:
            new = False            
        App_data_actual.create(
                        appid = app["id"],
                        name=app["name"].encode('utf-16', 'surrogatepass').decode('utf-16').encode('utf-8'),# Встречаются сурогатные пары
                        position = app["pos"],
                        releaseDate=date,
                        reviewsTotal = app["reviews_overal"],
                        reviewsRecent = app["reviews_recent"],
                        imageLink = app["image"],
                        achievements = app["achievements"],
                        new = new
                        )
    else:#Если уже имеется
        History.create(
                    app = app_data,
                    name =  app_data.name,
                    position = app_data.position,
                    reviewsTotal = app_data.reviewsTotal,
                    reviewsRecent = app_data.reviewsRecent,
                    imageLink = app_data.imageLink,
                    achievements = app_data.achievements,
                    new = app_data.new
                    )
        name = app["name"].encode('utf-16', 'surrogatepass').decode('utf-16').encode('utf-8')
        

        app_data.name =name
        app_data.reviewsTotal = app["reviews_overal"]
        app_data.reviewsRecent = app["reviews_recent"]
        app_data.imageLink = app["image"]
        app_data.achievements = app["achievements"]

        app_data.new = False
        app_data.save()

#Получаем данные отдельного приложения
def Get_app_data(element,pos):
    global bad_elems
    info = {}
    null = 0
    
    sess = requests.Session()
    info["id"]=re.search(r'"id":\w+',element.get(ID_CONTAINER)).group(0).split(":")[-1]
    info["pos"] = pos+1
    #Иногда пустой ответ приходит
    while True:
        if PAUSES:
            time.sleep(random.randrange(1,4))
        #основная инфа   
        app_info = sess.get("https://store.steampowered.com/api/appdetails?appids={}".format(info["id"]),headers ={'User-Agent':random.choice(USER_AGENTS)})
        if PAUSES:
            time.sleep(random.randrange(1,4))
        #Отзывы хранятся отдельно    
        rev_info = sess.get("https://store.steampowered.com/appreviewhistogram/{}?l=all&review_score_preference=1".format(info["id"]),headers ={'User-Agent':random.choice(USER_AGENTS)})
        text = app_info.text.replace("true","True")    
        if text != "null" and app_info.status_code==200:
            break
        elif app_info.status_code==403:
            bad_elems.append((element,pos))
            return
        
    text = text.replace("false","False")
    text = text.replace("null","0")

    text_rev = rev_info.text.replace("true","True")
    text_rev = text_rev.replace("false","False")
    text_rev = text_rev.replace("null","0")
    try:# является ли json-ом
        app_reviews = eval(text_rev)
        app = eval(text)
        # а также  иногда БД стима возвращает 200 но в json пишет неудачный запрос
        info["name"] = app[info["id"]]["data"]["name"]  
        info["image"] = app[info["id"]]["data"]["header_image"].replace("\\","")
        info["release_date"] = app[info["id"]]["data"]["release_date"]["date"]
    except :
        bad_elems.append((element,pos))
        return
        
    try:# Сервера стима иногда закрывают доступ к ачивкам
        info["achievements"] = app[info["id"]]["data"]["achievements"]["total"]
    except KeyError: 
        info["achievements"] = 0

    
   
        
    info["reviews_overal"] = 0
    info["reviews_recent"] = 0 
    try:#Отзывы бывают закрыты
        for i in app_reviews["results"]["rollups"]:
            info["reviews_overal"]+= i['recommendations_up']+i['recommendations_down']
        for i in app_reviews["results"]["recent"]:
            info["reviews_recent"]+= i['recommendations_up']+i['recommendations_down']    
    except KeyError:
        pass    
    
    Write_in_database(info)


#Выбираем из страниц отдельные приложения 
#ВАЖНО: Выборка в рандомном порядке, иначе моментальный бан
def Get_id(start,session):
    url = "https://store.steampowered.com/contenthub/querypaginated/tags/NewReleases/render/?query=&start={}&count=15&cc=RU&l=russian&v=4&tag=%D0%9F%D1%80%D0%B8%D0%BA%D0%BB%D1%8E%D1%87%D0%B5%D0%BD%D0%B8%D0%B5".format(start)
    request = session.get(url,headers ={'User-Agent':random.choice(USER_AGENTS)})
    text  = request.text.replace("true","True")
    request.text.replace("false","False")
    try:
        di = eval(text)
    except SyntaxError:
        time.sleep(4)
        Get_id(start,session)
        return
    root = html.document_fromstring(di["results_html"])
    el = root.find_class("tab_item")
    pos = start
    random.shuffle(el)
    jobs = []
    for i in el :    
        if PAUSES:
            time.sleep(random.randrange(1,4))
        t = Thread(target=Get_app_data, args=(i,pos))
        t.start()
        jobs.append(t);
        pos += 1
    for i in jobs:
        i.join()
  

# Основное кольцо парсинга. Получаем общее количество приложение в топе и раскидываем страницы по потокам    
def analyze_loop(delay):
    while True:
        print("Начинаю парсинг")
        global bad_elems
        delay_time = delay
        url = "https://store.steampowered.com/contenthub/querypaginated/tags/NewReleases/render/?query=&start=0&count=15&cc=RU&l=russian&v=4&tag=%D0%9F%D1%80%D0%B8%D0%BA%D0%BB%D1%8E%D1%87%D0%B5%D0%BD%D0%B8%D0%B5"
        s = requests.Session()
        request = s.get(url,headers ={'User-Agent':random.choice(USER_AGENTS)})
        text  = request.text.replace("true","True")
        try:
            di = eval(text)
        except SyntaxError :
            print("Список не получен, повтор через 10 минут")
            time.sleep(600)
            continue
        
        total =di["total_count"]
        tasks = [i for i in range(0,total,15)]
        random.shuffle(tasks)
        jobs = []
        
        for i in tasks :
            t = Thread(target=Get_id, args=(i,s))
            t.start()
            jobs.append(t)
        for i in jobs:
            i.join()
        while len(bad_elems)>0:
            print("Ссылки без доступа:{}, повторный запрос через 3 минуты".format(len(bad_elems)))
            time.sleep(180)
            print("Cборка заблокированных страниц")
            bads = bad_elems #Записываем отдельно чтоб не обновлялся в ходе цикла
            for i in bads:
                time.sleep(random.randrange(2,4))
                t = Thread(target=Get_app_data, args=(i[0],i[1]))
                t.start()
                jobs.append(t);
                bad_elems.remove(i)
        print("Парсинг окончен")           
        time.sleep(delay_time)


if __name__ == '__main__':
    
    delay =3600*8
    analyze_loop(delay)