# PlebChatDB




```sh
streamlit run frontend/app.py --server.port=5252

uvicorn server.app:app --reload --port 5101
```






---






```sh
streamlit run frontend/app.py
...
uvicorn server.app:app --reload
```




```sh
docker-compose up --build
```


## run locally

```sh
# uvicorn app.main:app --reload
uvicorn server.app:app --reload

```




## build/run docker image

```sh
docker build -t fastapi-mongo-app .

docker run -d -p 8000:8000 --name fastapi_app fastapi-mongo-app
```


