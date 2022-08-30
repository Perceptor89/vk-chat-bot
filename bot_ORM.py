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


class BaseModel(Model):
    class Meta:
        database = db


class Section(BaseModel):
    name = CharField(null=False)


class Product(BaseModel):
    name = CharField(max_length=250, null=False)
    description = CharField(null=False)
    section = ForeignKeyField(Section, backref='products')


def get_sections():
    return Section.select()


def get_products(section_id):
    return Product.select().where(Product.section == section_id)
