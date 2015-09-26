# -*- coding: utf-8 -*-
__author__ = 'Naptin'
import urllib
import urllib2
import requests

import myutils
import random

if False:
    from gluon import *
    from gluon.tools import request,response, session, cache, Auth, DAL, Service, Crud, PluginManager
    from gluon.contrib.appconfig import AppConfig

    #from myutils import sendSMS
    #from db import *
    myconf = AppConfig(reload=True)
    db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])
    auth = Auth(db)

import json
###sendSMS here formally


# my message interceptor
#@request.restful()
def getsms():

    response.view = 'generic.json'
    phone = request.vars['phone']
    msg = request.vars['text']
    smscenter = request.vars['smscenter']

    #split msg
    args = msg.split()
    if not args:
        raise HTTP(401, json.dumps({'msg': 'Bad Request'}))
    else:

        SA = 'EdoSRS'
        DA = str(phone)[1:]
        M = ''
        #Check Balance
        if args[0].upper() == 'BAL':
            # call getbalance api
            reventry = db.rev_wallet(revnumber=args[1])
            if not reventry:
                M = 'Balance Check unsuccessful; Wrong Revenue Card Number'
                rs = myutils.sendSMS(DA, SA, M)
                raise HTTP(401, json.dumps({'msg' : 'wrong revcard'}))
            else:

                M = 'Your Account Bal is NGN' + str(reventry['amount'])
                return dict(msg = reventry['amount'], result=myutils.sendSMS(DA, SA, M))

        # load RFID card
        elif args[0].upper() == 'LOAD':

            if not db.scratch_card(scratch_number=args[2]):
                M = 'Error loading account; Wrong Rechard Card Number'
                myutils.sendSMS(DA, SA, M)
                raise HTTP(401, json.dumps({'msg' : 'wrong recharge card'}))
            if not db.rev_wallet(revnumber = args[1]):
                M = 'Error loading account; wrong Revenue Card Number'
                myutils.sendSMS(DA, SA, M)

                raise HTTP(401, json.dumps({'msg' : 'wrong revcard'}))

            qryscratch = db.scratch_card.scratch_number == args[2]
            qryrev = db.rev_wallet.revnumber == args[1]
            scratch = db(qryscratch).select().first()
            rev = db(qryrev).select().first()
            rec = rev.update_record(amount = rev.amount + scratch.amount)

            M = 'Your Account Bal. is NGN' + str(db.rev_wallet(id = rec).amount)
            rs = myutils.sendSMS(DA, SA, M)
            return dict(record=rec, rs=rs)

        # Make Payment
        elif args[0].upper() == 'PAY':
            #check if Pay with TIN i.e 'pay tinNum scratchcardnumber
            #if len(args) == 3:
            qryrev = db.rev_wallet.revnumber == args[1]
            #Check Validity of pin
            if not db.rev_wallet(revnumber = args[1]):
                M = 'Invalid pin number'
                #rs = myutils.sendSMS(DA, SA, M)
                raise HTTP(404, json.dumps({'msg' : M}))
            else:
                #Post-charge
                revwallet = db(db.rev_wallet.revnumber == args[1]).select().first()
                ret=db.rev_charged.validate_and_insert(device=2,
                                                       wallet=revwallet.id,
                                                       amount=revwallet.amount,
                                                       time_charged='now',
                                                       reconcilled='no',
                                                       receipt_issued=1
                                                      )
                #raise HTTP(410, json.dumps({'ID':ret.id}))
                if ret.errors:
                    myutils.sendSMS(DA, SA, 'Error Paying; pls try again')
                    raise HTTP(401, json.dumps({'msg' : 'insert errors'}))
                else:
                    Tin = None
                    if len(args) == 3: Tin = args[2] # if it is pay with the TIN
                    result = myutils.reconcile(args[1])
                    gencode = random.randint(100000,999999)
                    confirm = db.confirmation.validate_and_insert(code=gencode,
                                                                  tin=Tin,
                                                                  pin=revwallet.id,
                                                                  amount=db.rev_charged(id=ret.id).amount,
                                                                  phone_no=DA,
                                                                 )



                    M = 'Your Smart Wallet code is ' + str(gencode) + '; with a balance of NGN' + str(db.rev_charged(id=ret.id).amount) + ' pls proceed to your service points to make your payment'
                    rs = myutils.sendSMS(DA, SA, M)
                    return dict(msg=M, rs=rs, code=str(gencode), amount=str(db.rev_charged(id=ret.id).amount))


        else:
            return dict(msg = 'Error in message sent')


    return locals() #dict(phone=phone, smscenter=smscenter, msg=msg)

@request.restful()
def addPayer():

    response.view = 'generic.json'
    def POST(tablename, **vars):

        if not tablename == 'payer': raise HTTP(401, json.dumps({'message': 'Bad Request'}))
        #add code here
        ret = db.payer.validate_and_insert(**vars)

        if not ret: raise HTTP(401, json.dumps({'message': 'Error duplicate entry or wrong parameter is sent'}))
        if ret.errors: raise HTTP(404, json.dumps({'message':'Error duplicate entry or wrong parameter is sent'}))
        payer = db.payer(id=ret.id)
        wallet = db(db.rev_wallet.id == payer.wallet).select().first()
        rec = wallet.update_record(issued = 'yes')


        return dict(payer=payer)

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
def getFreeWalletID():
    response.view = 'generic.json'
    def POST(tablename):
        if not tablename == 'rev_wallet': raise HTTP(401, json.dumps({'message': 'Bad Request'}))
        rows = db(db.rev_wallet.issued == 'no').select(db.rev_wallet.id)
        if not rows:
            #raise HTTP(404, json.dumps({'message': 'resource not found'}))
            return dict(wallets='null')
        else:
            return dict(wallets=rows.first())

    return locals()

@request.restful()
def loadWallet():
    response.view = 'generic.json'
    def POST(walletid, wallet_amount, phone):
        wallet = db(db.rev_wallet.id == walletid).select().first()
        wallet.update_record(amount=wallet_amount)
        if wallet:
            DA=phone
            SA='EdoSRS'
            M='Your pin is; ' + wallet.revnumber + ' with balance of NGN' + wallet.amount
            if myutils.sendSMS(DA, SA, M) == 200:
                wallet.update_record(issued='yes')
            else: raise HTTP(301, json.dumps({'message': 'error sending sms'}))
        else: raise HTTP(402, json.dumps({'message': 'CBS fail to vend'}))
        return dict(message='NGN'+ wallet.amount + ' valued-pin was successfully sent to ' + phone )
    return locals()

def sendWallet():
    response.view = 'generic.json'
    def POST():
        return dict()
    return locals()

@request.restful()
def chargeWallet():
    response.view = 'generic.json'
    def POST(tablename,revnum): # error1
        revid = db.rev_wallet(revnumber=revnum).id

        if not tablename == 'payer':
            raise HTTP(401, json.dumps({'message': 'Bad Request'}))

        if not revid: #db.rev_wallet(revnumber=revnum):
            raise HTTP(301, json.dumps({'message': 'Invalid Revenue Card!'}))

        sumchg = db.rev_charged.amount.sum()
        totalcharges = db(db.rev_charged.wallet == revid)(db.rev_charged.reconcilled == 'no').select(sumchg).first()[sumchg] #error3 'no missing'
        if not totalcharges:
            totalcharges = 0.0

        qry = db.rev_wallet.revnumber == revnum
        card = db(qry).select().first()

        rec = db(qry).update(amount=(card.amount - totalcharges))
        chgset = db(db.rev_charged.wallet == revid)

        for charge in chgset.select():
            #charge.update(reconcilled = 'yes')
            charge.update_record(reconcilled = 'yes')


        return dict(revcard=db.rev_wallet(id=rec))

    return locals()

##### Begin utility #########

#######End utility ##############


@request.restful()
def getReceiptListByCollector():
    response.view = 'generic.json'
    def POST(tablename, auth_user):

        return dict()

    return locals()

@request.restful()
def getCards():
    response.view = 'generic.json'
    def POST(tablename):
        if not tablename == 'rev_wallet': raise HTTP(401, json.dumps({'message': 'Bad Request'}))
        allcards = db(db.rev_wallet.id > 0).select()

        return dict(cards=allcards)

    return locals()


@request.restful()
def getCardBal():
    response.view = 'generic.json'
    def POST(revnum):
        if not db.rev_wallet(revnumber=revnum):
            raise HTTP(301, json.dumps({'message': 'Revenue Card does not exist!'}))
        return dict(bal=db.rev_wallet(revnumber=revnum))

    return locals()

@request.restful()
def fundbyscratch():
    response.view = 'generic.json'
    def POST(revnum, scratchnum):
        # check if scratchnum exist
        if not db.scratch_card(scratch_number=scratchnum):
            raise HTTP(301, json.dumps({'message': 'Scratch Card Error!'}))
        # check if revnum exist
        if not db.rev_wallet(revnumber=revnum):
            raise HTTP(301, json.dumps({'message': 'Revenue Card does not exist!'}))
        # update the rev_wallet accordingly
        qryscratch = db.scratch_card.scratch_number == scratchnum
        qryrev = db.rev_wallet.revnumber == revnum
        scratch = db(qryscratch).select().first()
        rev = db(qryrev).select().first()
        rec = rev.update_record(amount = rev.amount + scratch.amount)





        return(dict(result = db.rev_wallet(id = rec)))

    return locals()

@request.restful()
def postcharge():
    response.view = 'generic.json'
    def POST(tablename, revnum, **fields):
        if not tablename == 'rev_charged': raise HTTP(401, json.dumps({'message': 'Bad Request'}))
        #test for revcard
        if not db.rev_wallet(revnumber=revnum):
            raise HTTP(404, json.dumps({'message': 'Invalid revcard'}))
        if (db.rev_wallet(revnumber=revnum).amount < float(request.vars.amount)):
            raise HTTP(402, json.dumps({'message':'insuficient fund'}))

        ret=db.rev_charged.validate_and_insert(wallet=db.rev_wallet(revnumber=revnum).id, **fields)
        if ret.errors:
            raise HTTP(401, json.dumps(ret.errors.as_dict()))
        # reconcille account
        reconcilled = myutils.reconcile(revnum)

        return dict(message='Charge successfully posted!', charge=db.rev_charged(id=ret.id))

    return locals()
@request.restful()
def getTotalCharges():
    response.view ='generic.json'
    def POST(tablename):
        if not tablename == 'rev_charged':
            raise HTTP(401, json.dumps({'message': 'Bad Request'}))
        totalvar = db.rev_charged.amount.sum()
        total = db(db.rev_charged.id > 0).select(totalvar).first()[totalvar]

        return dict(total=total)
    return locals()

@request.restful()
def runBilling():
    response.view ='generic.json'
    rs = None
    def POST(code, mdatype, amount):
        #if not tablename == 'mda_sweep_account':
        if not db.confirmation(code=code):
            raise HTTP(404, json.dumps({'msg': 'Confirmation code doesnt exist'}))
        if not db.typeMDA(mdatype):
            raise HTTP(404, json.dumps({'msg': 'MDA-Type doesnt exist'}))

        confirm = db(db.confirmation.code == code).select().first()
        if confirm.amount < float(amount):raise HTTP(404, json.dumps({'msg': 'insufficient fund!'}))
        rs = myutils.credit(mdatype, confirm.id, myutils.debit(confirm.id, float(amount)))
        if rs == -1 : raise HTTP(401, json.dumps({'msg':'failed to credit account'}))
        DA = confirm.phone_no
        SA = 'EdoSRS'
        M = 'your code account ' + str(confirm.code) + ' is successfully charged; NGN' + amount + ', by ' + db.typeMDA(mdatype).name + '; your bal. is NGN' + str(confirm.amount - float(amount))
        res = myutils.sendSMS(DA, SA, M)
        return dict(msg=M, res='res')

    return locals()

@request.restful()
def getMDAList():
    pass

@request.restful()
def getMDAType():
    response.view = 'generic.json'
    def GET():

        return dict(alltypes=db(db.typeMDA.id > 0).select(db.typeMDA.id, db.typeMDA.name))

    return locals()

@request.restful()
def getMdaAccount():
    response.view = 'generic.json'
    def POST(mdaId):
        sweeps = None
        if mdaId > 0:
            sweeps = db(db.mda_sweep_account.mda_type == mdaId).select()
            return dict(accounts=sweeps)
        elif mdaId == -1:
            sweeps = db(db.mda_sweep_account.id > 0).select()
            return dict(accounts=sweeps)
        else: raise HTTP(404, json.dumps({'msg': 'account not found'}))




            #rows = [r for r in sweeps]
        #return dict(accounts=sweeps)


    return locals()

@request.restful()
def getAllMDAAcounts():
    response.view = 'generic.json'
    def GET():

        return dict(accounts=db(db.mda_sweep_account.id > 0).select())
    return locals()

@request.restful()
def getMDAAccountSummary():
    response.view = 'generic.json'
    def POST():
        s = db.mda_sweep_account.amount.sum()
        result1 = db(db.mda_sweep_account.id > 0).select(db.mda_sweep_account.mda_type, s, groupby = db.mda_sweep_account.mda_type)
        #result2 = {x['_extra'] : x['mda_sweep_account'] for x in result1}
        #result3 = { x['_extra'] for x in result1}
        #result4 = { x['SUM(mda_sweep_account.amount)'] for x in result3}
        #rs = {}
        #for acc in result1:

        return dict(rst=result1)

    return locals()
@request.restful()
def getCode():
    response.view = 'generic.json'

    def GET(myid):
        cnf = db.confirmation(id=int(myid))
        if cnf:
            conf=db(db.confirmation.id == int(myid)).select().first()

            return dict(conf=conf)

        else:
            return dict(conf=None)

    return locals()

@request.restful()
def getMDAByType():
    response.view = 'generic.json'
    def POST(myid):
        mda = db.typeMDA(id=int(myid))
        if mda:
            mdaselect = db(db.typeMDA.id == int(myid)).select().first()

            return dict(Mda=mdaselect)

        else:
            return dict(Mda=None)

    return locals()
