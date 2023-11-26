The following tools were used in the backend part of the project:

- FastAPI
- SQLAlchemy
- Alembic

The infrastructure part used:
- MySQL
- Docker
- Uvicorn

# 🚀 Project installation
Install Docker and docker-compose:
```sh
sudo apt-get update
sudo apt install docker.io
sudo apt-get install docker-compose-plugin
```
Clone repository:
```sh
git clone git clone git@github.com:gufin/delta_test.git
```
##### 🐳 Running Docker containers
When deploying to a server, you need to create a file with the values of the .env variables in the docker_compose folder.
```sh
sudo docker-compose  up -d --build
```

[Api documentation](http://localhost:8080/api/openapi)

To identify the user, the request header must contain user_id with a value of type int.


# :smirk_cat: Authors
Drobyshev Ivan

