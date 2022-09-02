import os
import vk_api
import prompt
import logging
import logger
import sys

from vk_api import VkUpload
from bot_ORM import db, Section, Product, User
from dotenv import load_dotenv
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id


load_dotenv()
logger.set_logger()
token = os.getenv('TOKEN')
group_id = os.getenv('GROUP_ID')
vk_session = vk_api.VkApi(token=token)
vk = vk_session.get_api()
upload = VkUpload(vk_session)


def processing_message(vk_id, message_text):
    user, _ = User.get_or_create(vk_id = vk_id, defaults = {'state': 0})
    logging.info(f'Состояние: {user.state}')
    if user.state == 0:
        message = (f'Приветствую! Пока мы спешим с ответом, '
                   f'вы можете ознакомиться с витриной.')
        kb = VkKeyboard(one_time=False, inline=True)
        kb.add_button('Витрина', color=VkKeyboardColor.PRIMARY)
        kb.get_keyboard()
        message_send(vk_id, message, kb)
        user.state = 1
        user.save()
    else:
        pass
    # elif user.state == 1 and message_text = 'Витрина':


def message_send(vk_id, message, kb=None):
    vk.messages.send(
        peer_id = vk_id,
        message = message,
        keyboard = kb,
        random_id = get_random_id(),
    )


def engine():
    # session = requests.Session()
    try:
        longpoll = VkBotLongPoll(vk_session, group_id)
        logging.info('Listening for new messages...')
        for event in longpoll.listen():
            print(event.type)
            if event.type == VkBotEventType.MESSAGE_NEW:
                vk_id = event.obj['message']['peer_id']
                message_text = event.obj['message']['text']
                logging.info(f'Новое сообщение от {vk_id}')
                print(event)
                processing_message(vk_id, message_text)
    except Exception as error:
        logging.info(error)
        logging.info('Бот перезапущен')
            

if __name__ == '__main__':
    try:
        engine()
    except KeyboardInterrupt:
        sys.exit(0)
