import peewee
import vk_bot.bot_ORM as bot_ORM
import unittest

from vk_bot.bot_ORM import db_test, User, Section, Product


MODELS = [User, Section, Product]


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        db_test.bind(MODELS, bind_refs=False, bind_backrefs=False)
        db_test.connect()
        db_test.create_tables(MODELS)

    def test_get_sections(self):
        with db_test.atomic():
            section = Section.get_or_none(Section.name == 'Торты')
            assert section is None
            Section.create(name='Торты')
            section = bot_ORM.get_sections()
            assert type(section) == peewee.ModelSelect
            Section.drop_table(cascade=True)

    def test_get_section_names(self):
        with db_test.atomic():
            section = Section.get_or_none(Section.name == 'Торты')
            assert section is None
            Section.create(name='Торты')
            Section.create(name='Пирожные')
            names = list(bot_ORM.get_section_names())
            assert names == ['Торты', 'Пирожные']
            Section.drop_table(cascade=True)

    def test_get_products(self):
        with db_test.atomic():
            section = Section.create(name='Торты')
            Product.create(
                name='Медовик',
                description='медовый',
                section=section.id,
            )
            Product.create(
                name='Наполеон',
                description='низкий',
                section=section.id,
            )
            Product.create(
                name='Муравейник',
                description='нестабильный',
                section=section.id,
            )
            products = bot_ORM.get_products(section='Торты')
            assert type(products) == peewee.ModelSelect
            names = [product.name for product in products]
            assert names == ['Медовик', 'Наполеон', 'Муравейник']
            Section.drop_table(cascade=True)
            Product.drop_table(cascade=True)

    def test_change_user_state(self):
        with db_test.atomic():
            user, is_created = User.get_or_create(vk_id=555, defaults={'state': 0})
            assert is_created is True
            assert user.state == 0
            bot_ORM.change_user_state(user, 1)
            user, is_created = User.get_or_create(vk_id=555, defaults={'state': 0})
            assert is_created is False
            assert user.state == 1
            User.drop_table(cascade=True)

    def tearDown(self):
        db_test.close()
