generate:
	poetry export -f requirements.txt --output requirements.txt
container:
	poetry run docker build -t vk_chat_bot .
start:
	poetry run python -m vk_bot
test:
	poetry run pytest
empty:
	poetry run python -m send_empty
