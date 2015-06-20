# -*- coding: utf-8 -*-
__author__ = 'Naptin'
if False:
    from gluon import *

    from datetime import date, datetime

    from gluon.tools import request,response, session, cache, DAL,Auth, Service, PluginManager
    #from gluon.tools import
    from gluon.contrib.appconfig import AppConfig
    myconf = AppConfig(reload=True)
    db = DAL(myconf.take('db.uri'), pool_size=myconf.take('db.pool_size', cast=int), check_reserved=['all'])
    auth = Auth(db)
    service = Service()
    plugins = PluginManager()
    from db import *

    ## create all tables needed by auth if not custom tables
    #auth.define_tables(username=False, signature=False)
from time import ctime

db.define_table('rev_wallet',
                Field('revnumber', requires=IS_LENGTH(16, 16)),
                Field('month_issued', 'integer', requires=IS_INT_IN_RANGE(1, 12)),
                Field('year_issued', 'integer', requires=IS_INT_IN_RANGE(2015, 2099)),
                Field('month_expired', 'integer', requires=IS_INT_IN_RANGE(1, 12)),
                Field('year_expired', 'integer', requires=IS_INT_IN_RANGE(2015, 2099)),
                Field('amount', 'float'),

                )
db.define_table('device',
                Field('name'),
                Field('deviceuid'),
                Field('assigned_to','reference auth_user'),
                )
db.define_table('payer',
                Field('surname'),
                Field('firstname'),
                Field('sex', requires=IS_IN_SET(['Male', 'Female'])),
                Field('wallet', 'reference rev_wallet')

                )

db.define_table('receipt',
                Field('serial_no'),
                Field('date_gen', default=ctime()),
                Field('date_exp','date'),
                Field('ownby', 'reference auth_user'),
                Field('status', requires=IS_IN_SET(['sold', 'loaded', 'expired']))
                )

db.define_table('rev_charged',
                Field('wallet', 'reference rev_wallet'),
                Field('device', 'reference device'),
                Field('amount', 'float'),
                Field('time_charged', default=ctime()),
                Field('receipt_issued', 'reference receipt')
                )

db.define_table('scratch_card',
                Field('scratch_number', requires=IS_LENGTH(16, 8)),
                Field('serial_number'),
                Field('month_expired', 'integer', requires=IS_INT_IN_RANGE(1, 12)),
                Field('year_expired', 'integer', requires=IS_INT_IN_RANGE(2015, 2099)),
                Field('amount', 'float', requires=IS_FLOAT_IN_RANGE(100.0, 5000.0 )),
                Field('status', requires=IS_IN_SET(['used', 'not-used']), default='not-used'),
                Field('used_by_who', 'reference payer', default=None),

                )

db.define_table('cards',
                Field('cardNo'),
                Field('amount', 'float')

                )
