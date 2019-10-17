#coding=utf-8
from threading import Thread
from server import runserver
from http.server import HTTPServer
from analyze import *

#Steam parser v1.1

ANALYZE_DELAY = 3600 * 8# second in hour * hours
HOST = "localhost"
PORT = 80

#Использованны потоки а не процессы т.к. Gil не дает конфилктов БД и работает быстрее в данном случае(Т.К нет больших расчетов)

analyze =  Thread(target = analyze_loop,args = (ANALYZE_DELAY,) )
analyze.start()


runserver(HOST,PORT,)


analyze.join()
