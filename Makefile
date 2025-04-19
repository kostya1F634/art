all: web

web:
	uv run streamlit run art/app.py 

test:
	PYTHONPATH=art uv run pytest

