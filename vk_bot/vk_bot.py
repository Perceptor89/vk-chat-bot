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


IMAGE_DIR = os.getenv('IMAGES_DIR')
TOKEN = os.getenv('TOKEN')
GROUP_ID = os.getenv('GROUP_ID')
VK_SESSION = vk_api.VkApi(token=TOKEN)
vk = VK_SESSION.get_api()
upload = VkUpload(VK_SESSION)


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
        logging.info(f'Photo uploaded: {photo}')
        return photo
    except Exception:
        logging.info(f'Photo upload from {image_path} failed')
        return None


def to_state_one(user, inline=False):
    if user.state == 0:
        message = ('Приветствую! Пока мы спешим с ответом, '
                   'вы можете ознакомиться с витриной.')
        kb = make_keyboard({'Витрина': VkKeyboardColor.PRIMARY}, inline=inline)
    else:
        message = 'Вы вышли из витрины.'
        kb = make_keyboard({'Витрина': VkKeyboardColor.PRIMARY})
    message_send(user.vk_id, message, kb.get_keyboard())
    bot_ORM.change_user_state(user, 1)


def to_state_two(user, inline=False):
    if user.state == 1:
        kb = VkKeyboard.get_empty_keyboard()
        message_send(user.vk_id, 'Вы зашли в витрину.', kb)
    message = 'Выберите раздел'
    sections = bot_ORM.get_section_names()
    btts = {section: VkKeyboardColor.PRIMARY for section in sections}
    kb = make_keyboard(btts, inline=inline, back=True)
    message_send(user.vk_id, message, kb.get_keyboard())
    bot_ORM.change_user_state(user, 2)


def to_state_three(user, message_text, inline=False):
    if user.state == 3:
        product = bot_ORM.get_product(message_text)
        description = product.description
        img_path = os.path.join(IMAGE_DIR, product.name + '.jpg')
        photo = upload_photo(img_path) if os.path.exists(img_path) else None
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


def get_answer_type(message_text):
    sections = bot_ORM.get_section_names()
    products = bot_ORM.get_product_names()
    types = {
        sections: 'section',
        products: 'product',
        ('Витрина',): 'showcase',
        ('Назад',): 'back',
    }
    for key, value in types.items():
        if message_text in key:
            logging.info(f'{message_text} has \'{value}\' type')
            return value
    else:
        logging.info(f'Uknown message type for \'{message_text}\'')
        return None


def processing_message(vk_id, event):
    user = bot_ORM.get_user(vk_id)
    logging.info(f'User state: {user.state}')
    client_inline = event.obj['client_info']['inline_keyboard']
    message_text = event.obj['message']['text']
    logging.info(f'User texted \'{message_text}\'')
    if user.state == 0:
        to_state_one(user, inline=client_inline)
        return
    answer_type = get_answer_type(message_text)
    states_tree = {
        1: {
            'showcase': (to_state_two, (user,), {'inline': client_inline}),
        },
        2: {
            'section': (to_state_three, (user, message_text), {
                'inline': client_inline,
            }),
            'back': (to_state_one, (user,), {'inline': client_inline}),
        },
        3: {
            'product': (to_state_three, (user, message_text), {
                'inline': client_inline
            }),
            'back': (to_state_two, (user,), {'inline': client_inline}),
        },
    }
    machine_reaction = states_tree.get(user.state).get(answer_type)
    logging.info(f'Machine reaction is: {machine_reaction}')
    if machine_reaction:
        func, args, kwargs = machine_reaction
        func(*args, **kwargs)


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
        try:
            longpoll = VkBotLongPoll(VK_SESSION, GROUP_ID)
            logging.info('Listening for new messages...')
            for event in longpoll.listen():
                logging.info(f'New event {type(event)}')
                if event.type == VkBotEventType.MESSAGE_NEW and event.from_user:
                    vk_id = event.obj['message']['peer_id']
                    logging.info(f'New message from id {vk_id}')
                    processing_message(vk_id, event)
        except Exception as error:
            # raise error
            logging.info(error)
            logging.info('Rebooting bot...')
            continue
