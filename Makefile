.PHONY: test 
lines := 1000
compose := docker compose

init: init-envs pre-commit

init-envs:
	cp env.example .env
	cp config.example.yaml config.yaml
	cp fixtures.example.yaml fixtures.yaml
	mkdir -p logs

test:
	sudo $(compose) -f test.yml up --build --abort-on-container-exit

build:
	sudo $(compose) up --build -d 

down:
	sudo $(compose) down

stop:
	sudo $(compose) stop

ps:
	sudo $(compose) ps

full-migrate: makemigrations migrate

makemigrations:
	sudo $(compose) exec web ./manage.py makemigrations
migrate:
	sudo $(compose) exec web ./manage.py migrate

shell:
	sudo $(compose) exec web ./manage.py shell_plus

collectstatic:
	sudo $(compose) exec web ./manage.py collectstatic

admin:
	sudo $(compose) exec web ./manage.py createsuperuser

web-build:
	sudo $(compose) up --build -d web

web-logs:
	sudo $(compose) logs --tail $(lines) -f web

all-logs:
	sudo $(compose) logs --tail $(lines) -f

rates-build:
	sudo $(compose) up --build -d rates_checker

rates-logs:
	sudo $(compose) logs --tail $(lines) -f rates_checker

rates-stop:
	sudo $(compose) stop rates_checker

pre-commit:
	pip install pre-commit --upgrade
	pre-commit install

redis-cli:
	sudo $(compose) exec redis redis-cli

pg-shell:
	sudo $(compose) exec db bash
	
codegen:
	python3 run_codegen.py

fixtures:
	sudo $(compose) exec web ./manage.py create_fixtures