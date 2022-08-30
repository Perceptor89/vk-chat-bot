import os
import vk_api

from bot_ORM import db, Section, Product
from dotenv import load_dotenv

from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id


load_dotenv()


token = os.getenv('TOKEN')
vk_session = vk_api.VkApi(token=token)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, '215573932', wait=25)


def message_send(user_id, message_text, kb=None):
    vk.messages.send(
        user_id = user_id,
        random_id = get_random_id(),
        # keyboard=open(kb, 'r', encoding='UTF-8').read(),
        message = message_text)


if __name__ == '__main__':
    db.connect()
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_id = event.obj['message']['peer_id']
            message_text = event.obj['message']['text']
            message_send(user_id, message_text)

    # for event in longpoll.listen():
    #     print('событие')
    #     kb = VkKeyboard()
    #     kb.add_button('button', VkKeyboardColor.PRIMARY)
    #     answer(chat, event, kb)