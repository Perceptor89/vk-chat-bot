from vk_bot.bot_ORM import Section, Product, User
import logging
import prompt


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
                'description': 'Сметанный бисквит со сгущенным молоком, сметанный крем, шоколадный топпинг.',
                'section': 'Торты',
            },
            {
                'name': 'Наполеон',
                'description': 'Наш любимый домашний торт с заварным кремом и натуральной ванилью, украшенный свежей клубникой.',
                'section': 'Торты'
            },
            {
                'name': 'Фисташковый торт',
                'description': 'Невероятный ансамбль вкусов и текстур влюбит в себя с первой встречи.',
                'section': 'Торты',
            },
            {
                'name': 'Шоколадный торт',
                'description': 'Для тех, кто любит шоколад, и побольше, даже ещё больше, и создан этот оригинальный шоколадный торт.',
                'section': 'Торты',
            },
            {
                'name': 'Ягодный мусс',
                'description':'Тающий муссовый десерт с ярким ягодным вкусом.',
                'section': 'Пирожные',
            },
            {
                'name': 'Рикотта с грушей',
                'description':'Тающий во рту крем из рикотты на подушке из бисквита, с добавлением спелой груши.',
                'section': 'Пирожные',
            },
            {
                'name': 'Ягодный тарт',
                'description':'Нежный сливочный десерт в хрустящей корзинке с ароматными ягодами.',
                'section': 'Пирожные',
            },
            {
                'name': 'Клубничный капкейк',
                'description':'Классический десерт с воздушными сливками и жевательной карамелью.',
                'section': 'Пирожные',
            },
            {
                'name': 'Булочки с кунжутом',
                'description':'Румяные сдобные булочки с семенами кунжута.',
                'section': 'Хлеб',
            },
            {
                'name': 'Гренки с маслом',
                'description':'Пшеничная булочка, пряное масло, чеснок, перец чили, розмарин.',
                'section': 'Хлеб',
            },
            {
                'name': 'Фокачча с моцареллой',
                'description':'Фокачча, моцарелла, сливки, моцарелла со сливками, руккола.',
                'section': 'Хлеб',
            },
            {
                'name': 'Имбирный чай',
                'description':'Апельсиновый сок, лимон, апельсин, имбирь, специи, сахарный сироп, мёд. Магия ароматного вкуса.',
                'section': 'Напитки',
            },
            {
                'name': 'Капучино',
                'description':'Ароматный напиток из зерен рабусты и арабики.',
                'section': 'Напитки',
            },
            {
                'name': 'Клубничный милкшейк',
                'description':'Молочный охлаждающий напиток со свежей клубникой.',
                'section': 'Напитки',
            },
        ],
    },
    'user': {
        'model': User,
    },
}


def truncating_tables(data):
    for name in data:
        model = data[name]['model']
        if not model.table_exists():
            model.create_table()
            logging.info('Table {name} created.')
        else:
            model.truncate_table(
                restart_identity=True,
                cascade=True
            )
            logging.info('Table {name} truncated.')


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
    logging.info(f'Tables {table_names} are in demo state.')


def sure():
    sure = prompt.string(f'Install demodata to db (y/n)? ' 
                         f'WARNING: truncating "Section", '
                         f'"Product" and "User" tables): ')
    return sure.lower() in ['y', 'yes']


def install():
    if sure():
        truncating_tables(TABLES)
        write_data_to_db(['section', 'product'], TABLES)       


if __name__ == '__main__':
    install()
