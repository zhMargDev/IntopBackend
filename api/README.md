API From Intop.uz

start/
    python3 venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    uvicorn main:app --reload