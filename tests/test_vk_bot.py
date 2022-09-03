import peewee
import vk_bot.bot_ORM as bot_ORM
import unittest

from vk_bot.bot_ORM import test_db, User, Section, Product


MODELS = [User, Section, Product]


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
        test_db.connect()
        test_db.create_tables(MODELS)

    def test_get_sections(self):
        with test_db.atomic():
            section = Section.get_or_none(Section.name == 'Торты')
            assert section is None
            Section.create(name='Торты')
            section = bot_ORM.get_sections()
            assert type(section) == peewee.ModelSelect
            Section.drop_table(cascade=True)

    def test_get_section_names(self):
        with test_db.atomic():
            section = Section.get_or_none(Section.name == 'Торты')
            assert section is None
            Section.create(name='Торты')
            Section.create(name='Пирожные')
            names = bot_ORM.get_section_names()
            assert names == ['Торты', 'Пирожные']
            Section.drop_table(cascade=True)

    def test_get_products(self):
        with test_db.atomic():
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
        with test_db.atomic():
            user, is_created = User.get_or_create(vk_id=555, defaults={'state': 0})
            assert is_created is True
            assert user.state == 0
            bot_ORM.change_user_state(user, 1)
            user, is_created = User.get_or_create(vk_id=555, defaults={'state': 0})
            assert is_created is False
            assert user.state == 1
            User.drop_table(cascade=True)

    def tearDown(self):
        test_db.close()
