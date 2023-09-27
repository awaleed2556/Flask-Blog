
class Config:
    SECRET_KEY = '6ff6a0c5d95bd1f2301207db9632eeef'
    SQLALCHEMY_DATABASE_URI= 'sqlite:///site.db'                            # this specifies where the database is located but here this is sql lite database which easy to run
                                                                                           # the 3 slashes '///' above is the relative path from the current file so the 'site.db' file will be created in our directory
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'wadi2163@gmail.com'
    MAIL_PASSWORD = 'voibtkjqdrzmximp'