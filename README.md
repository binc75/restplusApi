# RestPLUS Flask RestAPI POC
Simple RestAPI POC using ***flask-restplus*** with authentication capabilities, JWT (JSON Web Token) management and python decorators.

Out of the box this library provide a Swagger interface!


![Alt text](img/RestAPI_POC.png?raw=true "Swagger POC")

## Usage
Launch the ***restplusApiJWT.py*** and visit http://127.0.0.1:8080

## Installation
### with virtualenv
Install **python3-virtualenv** on your machine, then
``` bash
git clone git@github.com:binc75/restplusApi.git
cd restplusApi/
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt --no-cache
./restplusApiJWT.py
```

