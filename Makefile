.PHONY: run stop docker-build

run:
	python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

docker-build:
	docker build -t stock-alert .
