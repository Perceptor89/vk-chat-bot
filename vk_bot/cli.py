import argparse


def get_args():
    parser = argparse.ArgumentParser(description='Start vk_bot')
    parser.add_argument(
        '-d',
        '--demo',
        help='writes demo data to database',
        action='store_true',
    )
    args = parser.parse_args()
    return args
