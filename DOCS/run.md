# start database

```sh
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
