import os
from peewee import *
from dotenv import load_dotenv


load_dotenv()


db = PostgresqlDatabase(
    os.getenv('DB_NAME'),
    user = os.getenv('DB_USER'),
    password = os.getenv('DB_PASSWORD'),
    host = os.getenv('DB_HOST'),
    port = os.getenv('DB_PORT'),
    )

test_db = PostgresqlDatabase(
    os.getenv('TEST_DB_NAME'),
    user = os.getenv('TEST_DB_USER'),
    password = os.getenv('TEST_DB_PASSWORD'),
    host = os.getenv('TEST_DB_HOST'),
    port = os.getenv('TEST_DB_PORT'),
    )


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    vk_id = IntegerField(null=False)
    state = IntegerField(null=False)


class Section(BaseModel):
    name = CharField(null=False)


class Product(BaseModel):
    name = CharField(max_length=250, null=False)
    description = CharField(null=False)
    section = ForeignKeyField(Section, backref='products', on_delete='cascade')


def get_sections():
    return Section.select()


def get_products():
    return Product.select()
