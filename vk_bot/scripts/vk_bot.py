#!/usr/bin/env python3
import sys
import logging
from vk_bot import logger
from vk_bot import start_bot
from vk_bot.cli import get_args
from vk_bot import cafe_demo


def main():
    logger.set_logger()
    args = get_args()
    if args.demo is True:
        cafe_demo.install()
    try:
        start_bot()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as error:
        logging.info(error)
        logging.info('Rebooting bot...')
        pass


if __name__ == '__main__':
    main()
