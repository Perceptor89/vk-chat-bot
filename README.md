# VK_bot
VK chatbot for demonstrating showcase to customers
#
[![Python CI](https://github.com/Perceptor89/python-project-lvl3/actions/workflows/pyci.yml/badge.svg)](https://github.com/Perceptor89/python-project-lvl3/actions/workflows/pyci.yml)
#

## Installation:
1. Clonning repository
```bash
    $ git clone https://https://github.com/Perceptor89/vk-chat-bot.git
```
2. Install dependencies by poetry
```bash
    $ make install
```
3. You need to change '.env_example' to '.env' and write in your keys
4. Start bot

```bash
    $ make start demo
```
WARNING: demo will rewrite database tables after asking,
make sure you answer no, or use command without demo. Actually, you need yor database filled with data. To exit use:
```bash
    Ctrl + C
```