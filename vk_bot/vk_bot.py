import os
import vk_api
import logging

from vk_api import VkUpload
from vk_bot import bot_ORM
from dotenv import load_dotenv
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id


load_dotenv()


image_dir = os.getenv('IMAGES_DIR')
token = os.getenv('TOKEN')
group_id = os.getenv('GROUP_ID')
vk_session = vk_api.VkApi(token=token)
vk = vk_session.get_api()
upload = VkUpload(vk_session)


def make_keyboard(buttons, one_time=False, inline=False, columns=2, back=False):
    kb = VkKeyboard(one_time=False, inline=inline)
    count = 0
    for button, color in buttons.items():
        if count > 0 and (count % columns == 0):
            kb.add_line()
        kb.add_button(button, color=color)
        count += 1
    if back:
        kb.add_line()
        kb.add_button('Назад', color=VkKeyboardColor.SECONDARY)
    return kb


def upload_photo(image_path):
    try:
        response = upload.photo_messages(image_path)[0]
        owner_id = response['owner_id']
        photo_id = response['id']
        access_key = response['access_key']
        photo = f'photo{owner_id}_{photo_id}_{access_key}'
        return photo
    except Exception:
        logging.info(f'Photo upload from {image_path} failed')
        return None


def to_state_one(user, inline=False):
    if user.state == 0:
        message = ('Приветствую! Пока мы спешим с ответом, '
                   'вы можете ознакомиться с витриной.')
    else:
        message = 'Вы вышли из витрины.'
    kb = make_keyboard({'Витрина': VkKeyboardColor.PRIMARY}, inline=inline)
    message_send(user.vk_id, message, kb.get_keyboard())
    bot_ORM.change_user_state(user, 1)


def to_state_two(user, inline=False):
    message = 'Выберите раздел'
    sections = bot_ORM.get_section_names()
    btts = {section: VkKeyboardColor.PRIMARY for section in sections}
    kb = make_keyboard(btts, inline=inline, back=True)
    message_send(user.vk_id, message, kb.get_keyboard())
    bot_ORM.change_user_state(user, 2)


def to_state_three(user, message_text, inline=False, is_product=None):
    if is_product:
        product = bot_ORM.get_product(message_text)
        description = product.description
        img_path = os.path.join(image_dir, product.name + '.jpg')
        photo = upload_photo(img_path) if os.path.exists(img_path) else None
        print(f'photo: {photo}')
        message_send(user.vk_id, description, attachment=photo)
        section = bot_ORM.get_section_from_product(product)
        message = 'Что еще показать?'
    else:
        section = message_text
        message = 'Выберите продукт'
    products = bot_ORM.get_product_names(section)
    btts = {product: VkKeyboardColor.PRIMARY for product in products}
    kb = make_keyboard(btts, inline=inline, back=True)
    message_send(user.vk_id, message, kb.get_keyboard())
    bot_ORM.change_user_state(user, 3)


def processing_message(vk_id, event):
    user = bot_ORM.get_user(vk_id)
    logging.info(f'User state: {user.state}')
    client_inline = event.obj['client_info']['inline_keyboard']
    message_text = event.obj['message']['text']
    logging.info(f'User texted {message_text}')
    if user.state == 0:
        to_state_one(user, inline=client_inline)
    elif user.state == 1 and message_text == 'Витрина':
        to_state_two(user, inline=client_inline)
    elif user.state == 1 and message_text == 'Назад':
        to_state_one(user, inline=client_inline)
    elif user.state == 2 and message_text in bot_ORM.get_section_names():
        to_state_three(user, message_text, inline=client_inline)
    elif user.state == 2 and message_text == 'Назад':
        to_state_one(user, inline=client_inline)
    elif user.state == 3 and message_text in bot_ORM.get_product_names():
        to_state_three(
            user,
            message_text,
            inline=client_inline,
            is_product=True,
        )
    elif user.state == 3 and message_text == 'Назад':
        to_state_two(user, inline=client_inline)


def message_send(vk_id, message, kb=None, attachment=None):
    vk.messages.send(
        peer_id=vk_id,
        message=message,
        keyboard=kb,
        random_id=get_random_id(),
        attachment=attachment,
    )


def start_bot():
    while True:
        longpoll = VkBotLongPoll(vk_session, group_id)
        logging.info('Listening for new messages...')
        for event in longpoll.listen():
            logging.info(f'New event {type(event)}')
            if event.type == VkBotEventType.MESSAGE_NEW and event.from_user:
                vk_id = event.obj['message']['peer_id']
                logging.info(f'New message from id {vk_id}')
                processing_message(vk_id, event)
