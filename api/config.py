import os




class Config:

    SECRET_KEY = "9292837272892jdbndnckajbcajcajkcbkjbkjb"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOG_FILE = "api.log"  # where logs are outputted to
    CONNECTION_URL = 'postgresql://tyicrzrtsdcphp:257b4fedf9600a993d0d61eaeb942c9b206d62ae3150aa3b2cf48d143c3020ac@ec2-52-6-178-202.compute-1.amazonaws.com:5432/db57vjpfs577v8'


class DevelopmentConfig(Config):

    url = Config.CONNECTION_URL
    SQLALCHEMY_DATABASE_URI = url
    DEBUG = True


class ProductionConfig(Config):

    SQLALCHEMY_DATABASE_URI = Config.CONNECTION_URL
    DEBUG = False


class DockerDevConfig(Config):

    SQLALCHEMY_DATABASE_URI = Config.CONNECTION_URL
    DEBUG = True


# way to map the value of `FLASK_ENV` to a configuration
config = {"dev": DevelopmentConfig, "prod": ProductionConfig, "docker": DockerDevConfig}
