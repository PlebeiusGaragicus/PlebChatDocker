Chill vibes - https://www.youtube.com/watch?v=8KO2p6gPuAk

Open WebUI Docker - http://localhost:3000

LangSmith - https://smith.langchain.com/


# database

generated endpoint docs - http://localhost:5101/docs#/

```sh
# NOTE: initual setup ONLY
# sudo mkdir -p /usr/local/var/mongodb                  
# sudo chown -R $(whoami) /usr/local/var/mongodb
# mongosh
#   rs.initiate()
#   rs.status()

# mongod --replSet "rs0" --dbpath /usr/local/var/mongodb

cd database
uvicorn src.app:app --reload --port 5101
```

# langserver

```sh
cd langserver
uvicorn src.app:app --reload --port 8513

# curl -s http://localhost:5101/admin/invoices/ | jq
# curl -s http://localhost:5101/health | jq

```

# frontend

Streamlit - http://localhost:8501

```sh
cd admin_frontend
streamlit run app.py
```
