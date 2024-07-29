# Setup for development

Chill vibes - https://www.youtube.com/watch?v=8KO2p6gPuAk

Open WebUI Docker - http://localhost:3000

LangSmith - https://smith.langchain.com/

## OpenWebUI and Pipelines containers

```sh
# Open WebUI Docker
# docker run -d -p 3000:8080 -e -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main
docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main

# Pipelines
docker run -d -p 9099:9099 --add-host=host.docker.internal:host-gateway -v pipelines:/app/pipelines --name pipelines --restart always ghcr.io/open-webui/pipelines:main
# http://host.docker.internal:9099
# Refer to: https://docs.openwebui.com/pipelines/
```

# MongoDB

Ensure MongoDB is running locally
```sh
mongod --replSet "rs0" --dbpath /usr/local/var/mongodb
```

# Database FastAPI

generated endpoint docs - http://localhost:5101/docs#/

```sh
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
