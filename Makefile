.PHONY: run stop docker-build

run:
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

stop:
	powershell -Command "$$conn = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1; if ($$conn) { Stop-Process -Id $$conn.OwningProcess -Force; Write-Host 'Stopped process on port 8000.' } else { Write-Host 'No process is listening on port 8000.' }"

docker-build:
	docker build -t stock-alert .
