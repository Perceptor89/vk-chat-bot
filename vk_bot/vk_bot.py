import os
import vk_api
import logging
from vk_bot import logger
import sys

from vk_api import VkUpload
from vk_bot.bot_ORM import Section, Product, User, get_sections, get_products
from dotenv import load_dotenv
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id


logger.set_logger()

SECTIONS = get_sections()
PRODUCTS = get_products()


load_dotenv()
image_dir = os.getenv('IMAGES_DIR')
token = os.getenv('TOKEN')
group_id = os.getenv('GROUP_ID')
vk_session = vk_api.VkApi(token=token)
vk = vk_session.get_api()
upload = VkUpload(vk_session)


def processing_message(vk_id, message_text, inline_kb=False):
    user, _ = User.get_or_create(vk_id = vk_id, defaults = {'state': 0})
    logging.info(f'User state: {user.state}')
    section_names = [section.name for section in SECTIONS]
    product_names = [product.name for product in PRODUCTS]
    if user.state == 0:
        message = (f'Приветствую! Пока мы спешим с ответом, '
                   f'вы можете ознакомиться с витриной.')
        kb = VkKeyboard(one_time=False, inline=inline_kb)
        kb.add_button('Витрина', color=VkKeyboardColor.PRIMARY)
        message_send(vk_id, message, kb.get_keyboard())
        user.state = 1
        user.save()
    elif user.state == 1 and message_text == 'Витрина':
        message = 'Выберите раздел'
        kb = VkKeyboard(one_time=False, inline=inline_kb)
        for i, section in enumerate(SECTIONS):
            if i > 1 and (i % 2 == 0):
                kb.add_line()
            kb.add_button(section.name, color=VkKeyboardColor.PRIMARY)
        kb.add_line()
        kb.add_button('Покинуть витрину', color=VkKeyboardColor.SECONDARY)
        message_send(vk_id, message, kb.get_keyboard())
        user.state = 2
        user.save()
    elif user.state == 2 and message_text in section_names:
        # logging.info(f'User choosed {message_text} section')
        products = Product.select().join(Section).where(Section.name == message_text)
        kb = VkKeyboard(one_time=False, inline=inline_kb)
        for i, product in enumerate(products):
            if i > 1 and (i % 2 == 0):
                kb.add_line()
            kb.add_button(product.name, color=VkKeyboardColor.PRIMARY)
        kb.add_line()
        kb.add_button('Назад', color=VkKeyboardColor.SECONDARY)
        kb.add_button('Покинуть витрину', color=VkKeyboardColor.SECONDARY)
        message = 'Выберите продукт'
        message_send(vk_id, message, kb.get_keyboard())
        user.state = 3
        user.save()
    elif user.state == 3 and message_text in product_names:
        product = Product.get(Product.name == message_text)
        name = product.name
        description = product.description
        image_path = os.path.join(image_dir, name + '.jpg')
        response = upload.photo_messages(image_path)[0]
        owner_id = response['owner_id']
        photo_id = response['id']
        access_key = response['access_key']
        photo = f'photo{owner_id}_{photo_id}_{access_key}'
        message_send(vk_id, name)
        message_send(vk_id, description, attachment=photo)


def message_send(vk_id, message, kb=None, attachment=None):
    vk.messages.send(
        peer_id = vk_id,
        message = message,
        keyboard = kb,
        random_id = get_random_id(),
        attachment = attachment,
    )


def engine():
    # session = requests.Session()
    while True:
        longpoll = VkBotLongPoll(vk_session, group_id)
        logging.info('Listening for new messages...')
        for event in longpoll.listen():
            logging.info(f'New event {type(event)}')
            if event.type == VkBotEventType.MESSAGE_NEW:
                inline_kb = event.obj['client_info']['inline_keyboard']
                vk_id = event.obj['message']['peer_id']
                message_text = event.obj['message']['text']
                logging.info(f'New message from id {vk_id}')
                logging.info(f'User can read inline: {inline_kb}')
                processing_message(vk_id, message_text, inline_kb)
            

if __name__ == '__main__':
    try:
        engine()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as error:
        logging.info(error)
        logging.info('Rebooting bot...')
        pass

