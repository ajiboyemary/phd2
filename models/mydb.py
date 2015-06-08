__author__ = 'Naptin'
if False:
    from gluon import *
    from time import ctime
    from datetime import date, datetime
    from gluon.tools import request,response, session, cache, DAL
    from gluon.tools import Auth, Service, PluginManager
    from gluon.contrib.appconfig import AppConfig
    myconf = AppConfig(reload=True)
    db = DAL(myconf.take('db.uri'), pool_size=myconf.take('db.pool_size', cast=int), check_reserved=['all'])
    auth = Auth(db)
    service = Service()
    plugins = PluginManager()

    ## create all tables needed by auth if not custom tables
    #auth.define_tables(username=False, signature=False)

db.define_table('rev_wallet',
                Field('number', requires=IS_LENGTH(16, 16)),
                Field('month_issued', int, requires=IS_INT_IN_RANGE(1, 12)),
                Field('year_issued', int, requires=IS_INT_IN_RANGE(2015, 2099)),
                Field('month_expired', int, requires=IS_INT_IN_RANGE(1, 12)),
                Field('year_expired', int, requires=IS_INT_IN_RANGE(2015, 2099)),
                Field('amount', float),
                Field('owner', 'reference payer', default=None),
                #format()
                )
db.define_table('device',
                Field('name'),
                Field('deviceuid'),
                Field('owner','reference auth_user'),
                )
db.define_table('payer',
                Field('surname'),
                Field('firstname'),
                Field('sex', requires=IS_IN_SET(['Male', 'Female'])),
                Field('wallet', 'reference rev_wallet')

                )
db.define_table('rev_charged',
                Field('wallet', 'reference rev_wallet'),
                Field('device', 'reference device'),
                Field('amount', float),
                Field('timestamp', default=ctime())
                )

db.define_table('scratch_card',
                Field('number', requires=IS_LENGTH(16, 8)),
                Field('month_expired', int, requires=IS_INT_IN_RANGE(1, 12)),
                Field('year_expired', int, requires=IS_INT_IN_RANGE(2015, 2099)),
                Field('amount', float, requires=IS_FLOAT_IN_RANGE(0.0, 100000.0)),
                Field('status', requires=IS_IN_SET(['used', 'not-used']), default='not-used'),
                Field('used_by_who', 'reference payer', default=None),

                )