generate:
	poetry export -f requirements.txt --output requirements.txt
container:
	poetry run docker build -t vk_chat_bot .
start:
	poetry run vk_bot
test:
	poetry run pytest
test-coverage:
	poetry run pytest --cov=page_loader --cov-report xml
demo:
	poetry run vk_bot --demo
lint:
	poetry run flake8 vk_bot
build_and_install:
	poetry build
	python3 -m pip install --user --force-reinstall dist/*.whl
install:
	poetry install
