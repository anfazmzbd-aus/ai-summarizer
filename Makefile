test:
pytest

api:
uvicorn app.main:app --reload

lint:
ruff check .

format:
black .

validate:
python scripts/validate_runtime.py
