__author__ = 'Naptin'

if False:
    from gluon import *
    from gluon.tools import request,response, session, cache, Auth, DAL, Service, Crud, PluginManager
    from gluon.contrib.appconfig import AppConfig
    myconf = AppConfig(reload=True)
    db = DAL(myconf.take('db.uri'), pool_size=myconf.take('db.pool_size', cast=int), check_reserved=['all'])
    auth = Auth(db)
    service = Service()
    plugins = PluginManager()

@request.restful()
def addPayer():

    response.view = 'generic.json'
    def POST(tablename, **vars):
        #add code here
        return dict()

    return locals()

@request.restful()
def assignedWallet():
    response.view = 'generic.json'

    def POST(tablename, payerid):
        #assigned to the payer free wallet
        return dict()

    return locals()

@request.restful()
def getPayerList():
    response.view = 'generic.json'
    def GET(tablename):
        #list
        return dict()

    return locals()

@request.restful()
def deletePayer():
    response.view = 'generic.json'
    def POST(tablename, payerid):
        return dict()

    return locals()

@request.restful()
def chargeWallet():
    response.view = 'generic.json'
    def POST(tablename, payerid):
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


