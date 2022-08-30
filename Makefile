generate:
	poetry export -f requirements.txt --output requirements.txt
container:
	poetry run docker build -t vk_chat_bot .
start:
	poetry run python -m main
