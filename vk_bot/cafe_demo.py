from vk_bot.bot_ORM import Section, Product, User
import logging
import prompt
import os


TABLES = {
    'section': {
        'model': Section,
        'rows': [
            {'name': 'Торты'},
            {'name': 'Пирожные'},
            {'name': 'Хлеб'},
            {'name': 'Напитки'},
        ]
    },
    'product': {
        'model': Product,
        'rows': [
            {
                'name': 'Сметанник',
                'description': ('Сметанный бисквит со сгущенным молоком, '
                                'сметанный крем, шоколадный топпинг.'),
                'section': 'Торты',
            },
            {
                'name': 'Наполеон',
                'description': ('Наш любимый домашний торт с заварным кремом '
                                'и натуральной ванилью, украшенный '
                                'свежей клубникой.'),
                'section': 'Торты'
            },
            {
                'name': 'Фисташковый торт',
                'description': ('Невероятный ансамбль вкусов и текстур влюбит'
                                ' в себя с первой встречи.'),
                'section': 'Торты',
            },
            {
                'name': 'Шоколадный торт',
                'description': ('Для тех, кто любит шоколад, и побольше, даже '
                                'ещё больше, и создан этот оригинальный '
                                'шоколадный торт.'),
                'section': 'Торты',
            },
            {
                'name': 'Ягодный мусс',
                'description': ('Тающий муссовый десерт с ярким '
                                'ягодным вкусом.'),
                'section': 'Пирожные',
            },
            {
                'name': 'Рикотта с грушей',
                'description': ('Тающий во рту крем из рикотты на подушке из '
                                'бисквита, с добавлением спелой груши.'),
                'section': 'Пирожные',
            },
            {
                'name': 'Ягодный тарт',
                'description': ('Нежный сливочный десерт в хрустящей корзинке'
                                ' с ароматными ягодами.'),
                'section': 'Пирожные',
            },
            {
                'name': 'Клубничный капкейк',
                'description': ('Классический десерт с воздушными сливками '
                                'и жевательной карамелью.'),
                'section': 'Пирожные',
            },
            {
                'name': 'Булочки с кунжутом',
                'description': 'Румяные сдобные булочки с семенами кунжута.',
                'section': 'Хлеб',
            },
            {
                'name': 'Гренки с маслом',
                'description': ('Пшеничная булочка, пряное масло, чеснок, '
                                'перец чили, розмарин.'),
                'section': 'Хлеб',
            },
            {
                'name': 'Фокачча с моцареллой',
                'description': ('Фокачча, моцарелла, сливки, моцарелла со '
                                'сливками, руккола.'),
                'section': 'Хлеб',
            },
            {
                'name': 'Имбирный чай',
                'description': ('Апельсиновый сок, лимон, апельсин, имбирь, '
                                'специи, сахарный сироп, мёд. '
                                'Магия ароматного вкуса.'),
                'section': 'Напитки',
            },
            {
                'name': 'Капучино',
                'description': 'Ароматный напиток из зерен рабусты и арабики.',
                'section': 'Напитки',
            },
            {
                'name': 'Клубничный милкшейк',
                'description': ('Молочный охлаждающий напиток со '
                                'свежей клубникой.'),
                'section': 'Напитки',
            },
        ],
    },
    'user': {
        'model': User,
    },
}


def recreating_tables(data):
    for name in data:
        model = data[name]['model']
        if not model.table_exists():
            model.create_table()
            logging.info(f'Table {name} created.')
        else:
            model.drop_table(cascade=True)
            model.create_table()
            logging.info(f'Table {name} recreated.')


def get_joints(rows, key_model):
    for key in key_model.keys():
        for i, row in enumerate(rows):
            model = key_model[key]
            rows[i][key] = model.select().where(model.name == rows[i][key])
    return rows


def write_data_to_db(table_names, data):
    for name in table_names:
        model_obj = data[name]['model']
        demo_rows = data[name]['rows']
        if name == 'product':
            demo_rows = get_joints(demo_rows, {'section': Section})
        for kwargs in demo_rows:
            model_obj.create(**kwargs)
    logging.info(f'Tables {table_names} are filled.')


def photo_check(dir_path):
    names = [product.name for product in Product.select()]
    for name in names:
        img_path = os.path.join(dir_path, name + '.jpg')
        exists = os.path.isfile(img_path)
        if not exists:
            logging.info(f'Image {name}.jpg does not exist at \'image/\'')


def sure():
    logging.info('WARNING: rewriting \'Section\', \'Product\' '
                 'and \'User\' tables)!')
    sure = prompt.string('Install demodata to DATABASE? (y/n) ')
    return sure.lower() in ['y', 'yes']


def install():
    if sure():
        recreating_tables(TABLES)
        write_data_to_db(['section', 'product'], TABLES)
        photo_check('images/')


if __name__ == '__main__':
    install()
