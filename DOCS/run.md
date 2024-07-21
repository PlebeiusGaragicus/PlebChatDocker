# start database

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

# start langserver

```sh
cd langserver
uvicorn src.app:app --reload --port 8513

# curl -s http://localhost:5101/admin/invoices/ | jq
# curl -s http://localhost:5101/health | jq

```

# start frontend

```sh
cd admin_frontend
streamlit run app.py

# http://localhost:8501
```
