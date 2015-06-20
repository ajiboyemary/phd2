# -*- coding: utf-8 -*-
__author__ = 'Naptin'

if False:
    from gluon import *
    from gluon.tools import request,response, session, cache, Auth, DAL, Service, Crud, PluginManager
    from gluon.contrib.appconfig import AppConfig
    #from db import *
    myconf = AppConfig(reload=True)
    #db = DAL(myconf.take('db.uri'), pool_size=myconf.take('db.pool_size', cast=int), check_reserved=['all'])
    db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])
    auth = Auth(db)



import json


@request.restful()
def addPayer():

    response.view = 'generic.json'
    def POST(tablename, **vars):

        if not tablename == 'payer': raise HTTP(401, json.dumps({'message': 'Bad Request'}))
        #add code here


        return dict()

    return locals()

@request.restful()
def assignedWallet():
    response.view = 'generic.json'

    def POST(tablename, payerid):
        #assigned to the payer free wallet
        if not tablename == 'payer': raise HTTP(401, json.dumps({'message': 'Bad Request'}))
        return dict()

    return locals()

@request.restful()
def getPayerList():
    response.view = 'generic.json'
    def GET(tablename):
        #list
        if not tablename == 'payer': raise HTTP(401, json.dumps({'message': 'Bad Request'}))
        return dict()

    return locals()

@request.restful()
def deletePayer():
    response.view = 'generic.json'
    def POST(tablename, payerid):
        if not tablename == 'payer': raise HTTP(401, json.dumps({'message': 'Bad Request'}))
        return dict()

    return locals()

@request.restful()
def chargeWallet():
    response.view = 'generic.json'
    def POST(tablename, payerid):

        if not tablename == 'rev_wallet': raise HTTP(401, json.dumps({'message': 'Bad Request'}))
        # 1. issue receipt from the POS terminal
        #2. call this api from the POS terminal (Post_Param: ---> payerid, receipt_no, timestamp, amount)
            # a) get the payer's wallet and charge the amount (from the api)
            # b) return updated updated data -----update changes.

        return dict()

    return locals()

@request.restful()
def getReceiptListByCollector():
    response.veiw = 'generic.json'
    def POST(tablename, auth_user):

        return dict()

    return locals()

@request.restful()
def getCards():
    response.veiw = 'generic.json'
    def POST(tablename):
        if not tablename == 'cards': raise HTTP(401, json.dumps({'message': 'Bad Request'}))
        allcards = db(db.cards.id > 0).select(db.cards.cardNo, db.cards.amount)
        
        return  dict(allcards=allcards)

    return locals()


