class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:1111@localhost:5432/LABAP'
    SECRET_KEY = 'secret_key_for_lab'
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Set to suppress a warning


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestConfig(Config):
    TESTING = True
