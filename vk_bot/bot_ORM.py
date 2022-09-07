import os
from peewee import (PostgresqlDatabase, Model,
                    IntegerField, CharField, ForeignKeyField)
from dotenv import load_dotenv
import logging


load_dotenv()


db = PostgresqlDatabase(
    os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    )

db_test = PostgresqlDatabase(
    os.getenv('TEST_DB_NAME'),
    user=os.getenv('TEST_DB_USER'),
    password=os.getenv('TEST_DB_PASSWORD'),
    host=os.getenv('TEST_DB_HOST'),
    port=os.getenv('TEST_DB_PORT'),
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


def get_section_names():
    return (section.name for section in get_sections())


def get_section_from_product(product):
    return Section.select(Section.name).where(Section.id == product.section)


def get_products(section=None):
    if section:
        return Product.select().join(Section).where(Section.name == section)
    else:
        return Product.select()


def get_product(product_name):
    return Product.get_or_none(Product.name == product_name)


def get_product_names(section=None):
    return (product.name for product in get_products(section=section))


def get_user(vk_id):
    return User.get_or_create(vk_id=vk_id, defaults={'state': 0})[0]


def change_user_state(user, value):
    query = User.update({User.state: value}).where(User.id == user.id)
    query.execute()
    logging.info(f'User status was changed to {value}')
