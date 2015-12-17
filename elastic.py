#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'DarkDescent'

from elasticsearch import Elasticsearch
from datetime import datetime

#класс Elastic используется как оболочка для объекта Elasticsearch. В нем содержатся функции для создания документа и поиска по индексу
class Elastic:
    #конструктор
    def __init__(self, i):
        #ES_HOST = {"host" : "localhost", "port" : 9200}    #переменная сохраняет информацию о хосте и порте Elasticsearch
        self.eSearch = Elasticsearch()                      #объект класса Elasticsearch
        self.index = i                                      #переменная хранит название индекса в Elasticsearch
        self.doc_id = 0                                     #текущий номер последнего документа в Elasticsearch

    #создание нового файла в индексе
    def create(self, text, inputDate):
        #formatDate = datetime.strptime(inputDate, "%d.%m.%Y").strftime("%Y-%m-%d")  #переменная необходима для перевода даты в формат, с которым работает Elasticsearch при запросах
        self.doc_id += 1
        self.eSearch.index(index=self.index, doc_type="test", id=self.doc_id, body={'text': text, 'timestamp': inputDate})

    #поиск файла по индексу
    def search(self, searchtext, inputDateFrom, inputDateTo):
        if(inputDateTo == '' and inputDateFrom == ''):
            res = self.eSearch.search(index=self.index, body={"query": {"match": {"text":searchtext}}})
        else:
            #две переменные необходимы для перевода даты в формат, с которым работает Elasticsearch при запросах
            #formatDateFrom = datetime.strptime(inputDateFrom, "%d.%m.%Y").strftime("%Y-%m-%d")
            #formatDateTo = datetime.strptime(inputDateTo, "%d.%m.%Y").strftime("%Y-%m-%d")

            res = self.eSearch.search(index=self.index, body={"query": {
                "filtered": {
                    "query": {"match": {"text": {
                            "query": searchtext,
                            "zero_terms_query": "all"}}},
                    "filter": {
                        "range": {
                            "timestamp": {
                                "from": inputDateFrom,
                                "to": inputDateTo
                            }
                        }
                    }
                }
            }
            })
        return res
