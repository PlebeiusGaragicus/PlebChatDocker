# setup for development



## create python environment

```sh
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

pip install -r langserver/requirements.txt
pip install -r database/requirements.txt
pip install -r admin_frontend/requirements.txt
```


## setup MongoDB to be a replicated (something)

```sh
sudo mkdir -p /usr/local/var/mongodb                  
sudo chown -R $(whoami) /usr/local/var/mongodb
mongosh
  rs.initiate()
  rs.status()
```
