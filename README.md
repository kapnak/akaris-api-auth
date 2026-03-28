# Auth API


## Getting started

#### Prepare python environment

```shell
python -m venv .venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Add env vars

See `.env.template`.
By default, the file `.env` is used. 
If a var `ENV` is set the file `.env.$ENV` will be used.

#### Generate a new key

```shell
.venv/bin/python -m app.crypto.kp
```

#### Start the app

```shell
python -m app
```


## Help

#### Compute public key PEM in base64

```shell
openssl ec -in store/auth_privkey.pem -pubout | openssl base64 -A; echo
```
