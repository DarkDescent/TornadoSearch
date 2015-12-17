#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'DarkDescent'
import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.gen
from tornado_elasticsearch import AsyncElasticsearch

currentIndex = "temp"
elas = AsyncElasticsearch()


#класс отвечает за отображение главной страницы
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('templates/index.html')

#класс отвечает за создание нового файла в индексе ElasticSearch
class NewFileHandler(tornado.web.RequestHandler):

    def get(self):
        self.render('templates/write.html')

    #если пользователь пытается сохранить файл, но при этом не добавил текста или даты, то ему выводится сообщение об ошибке; если все удачно, то пользователь получает об этом сообщение
    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        if not(self.get_argument("text") and self.get_argument("date")):
            result_message = u"Для сохранения документа необходимо ввести текст и дату"
            self.render('templates/write.html', message=result_message)
        else:
            result = yield elas.index(index=currentIndex, doc_type="test", body={'text': self.get_argument("text"), 'timestamp': self.get_argument("date")})
            result_message = u"Документ создан"
            self.render('templates/write.html', message=result_message)
            self.finish(result)

#класс отвечает за поиск сообщения
class SearchHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('templates/search.html', isSearched=0)

    #пользователь вводит нужную информацию для поиска. после чего она отправляется на страницу поиска
    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        searchResults = []
        result_message = u""
        if(self.get_argument("date_from") == '' and self.get_argument("date_to") == ''):
            filesInfo = yield elas.search(index=currentIndex, body={"query": {"match": {"text": self.get_argument("text")}}})
            result_message = u"Получили следующие результаты:"
        elif (self.get_argument("date_from") == '' or self.get_argument("date_to") == ''):
            result_message = u"Для фильтрации дат необходимо внести обе даты"
            self.render('templates/search.html', isSearched=0, message=result_message)
            return
        else:
            filesInfo = yield elas.search(index=currentIndex, body={"query": {
                "filtered": {
                    "query": {"match": {"text": {
                            "query": self.get_argument("text"),
                            "zero_terms_query": "all"}}},
                    "filter": {
                        "range": {
                            "timestamp": {
                                "from": self.get_argument("date_from"),
                                "to": self.get_argument("date_to")
                            }
                        }
                    }
                }
            }
            })
        for hit in filesInfo['hits']['hits']:
            searchResults.append(hit["_source"])
        result_message = u"Получили следующие результаты:"
        self.render('templates/search.html', results=searchResults, isSearched=1, message=result_message)
        self.finish(filesInfo)

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