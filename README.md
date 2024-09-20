***To Start Local***
**Join to api folder**
```
cd api
```
**Create virtual env**
```
python3 -m venv .venv
```
**Joint to virtual env**
```
source .venv/bin/activate
```
**Install requirements**
```
pip install -r requirements.txt
```
**Run fastapi localy**
```
uvicorn main:app --reload
```