# A self-hostable LangGraph agent and Open WebUI pipeline


## How to run for development

```sh
"uvicorn server.app:app --reload --port 8513
```




https://github.com/open-webui/pipelines/pull/158/files


### ignore this
```sh
# read -p "Enter the name for your image: " construct_name
# echo "\n\nWhat is this construct's name?"
# read construct_name

# build and name your image
# docker build -t $construct_name .
# docker build -t OpenWebUI-langserve-pipeline .

# run container
# docker run -d --name $construct_name-container -p 8510:8510 --restart always $construct_name
# docker run -d -p 8510:8510 --restart always OpenWebUI-langserve-pipeline
```
