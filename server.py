#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'DarkDescent'

import tornado.web
import tornado.ioloop
import tornado.httpserver
from elastic import Elastic

elas = Elastic("temp")

#класс отвечает за отображение главной страницы
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('templates/index.html')

#класс отвечает за создание нового файла в индексе ElasticSearch
class NewFileHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('templates/write.html')

    #если пользователь пытается сохранить файл, но при этом не добавил текста или даты, то ему выводится сообщение об ошибке; если все удачно, то пользователь получает об этом сообщение
    def post(self):
        if not(self.get_argument("text") and self.get_argument("date")):
            result_message = u"Для сохранения документа необходимо ввести текст и дату"
            self.render('templates/write.html', message=result_message)
        else:
            elas.create(self.get_argument("text"), self.get_argument("date"))
            result_message = u"Документ создан"
            self.render('templates/write.html', message=result_message)

#класс отвечает за поиск сообщения
class SearchHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('templates/search.html', isSearched=0)

    #пользователь вводит нужную информацию для поиска. после чего она отправляется на страницу поиска
    def post(self):
        searchResults =[]
        filesInfo = elas.search(self.get_argument("text"), self.get_argument("date_from"), self.get_argument("date_to"))
        for hit in filesInfo['hits']['hits']:
            #print("%(timestamp)s %(author)s: %(text)s" % hit["_source"])
            searchResults.append(hit["_source"])
        self.render('templates/search.html', results=searchResults, isSearched=1)

#оформляем Tornado application
application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/file", NewFileHandler),
    (r"/search", SearchHandler)
])

#запускаем сервер
if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()