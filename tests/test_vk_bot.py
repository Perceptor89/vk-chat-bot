import pytest
import vk_bot
from  bot_ORM import test_db, User, Section, Product

MODELS = [User, Section, Product]


def test_get_state():
    with test_db.atomic():
        test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
        test_db.create_tables(MODELS)
        query = User.get_or_none(User.vk_id == 555)
        assert query == None
        state = vk_bot.get_state(555)
        assert state == 0
        query = User.get_or_none(User.vk_id == 555)
        assert query.vk_id == 555
        assert query.state == 0
        test_db.drop_tables(MODELS)
