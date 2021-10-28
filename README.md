# Provectus-Internship-Task

This is my solution for the Provectus internship task, I decided to change it a little bit and put it as a personal data processing project. You can find the task description in the file `task.md`.

In this file I will explain how to run and test my solution to the test task. I will also explain some of the logic in the code. Reading this file plus the documentation in the code itself should be sufficient to understand how this code works. The solution to the theoretical questions will also be included in this file.

Note: The solution was only tested on Ubuntu 20.04 LTS. 

# Data Processing Level 3

## Table of Contents
1. [ Installing The Service ](#install)
2. [ Using The Service ](#use)
3. [ Understanding The Code ](#code)

<a name="install"></a>
# 1. Installing The Service

First clone this repo somewhere on your machine. From now on we will call the path to where you cloned the repo {installation path}.

Then inside the repo run
```
sudo docker-compose up --build
```
This will run and create some folders in {installation path}. Namely it will create {installation path}/minio, {installation path}/pgadmin, and {installation path}/postgres-data.

After it creates these folders docker-compose will keep crashing and restarting. Stop and the services with `Ctrl+C` and run:
```
sudo docker-compose down
```

The docker-compose crashes since it needs access permissions to these folders but these folders are created without the permissions. To fix this problem one can do something like
```
sudo chmod 777 minio/
sudo chmod 777 pgadmin/
sudo chmod 777 postgres-data/
```

Now running

```
sudo docker-compose up 
```
Will run everything without crashing.

If you wait some time until docker-compose runs the web service then inside the {installation path}/minio you should have 2 folders named `src` and `res`.

When the service wants to read input data it will only look inside `src` so if you want to add input data for processing then you need to copy it inside `src` and since this folder is created without permissions to copy you might need to do

```
sudo chmod 777 minio/src/
```
before you are allowed to copy inside `src`. 

Inside `res` there will be a file called `output.csv` which is the same `output.csv` described in the the test task.

Now you should have a running service.


<a name="use"></a>
# 2. Using The Service

The services need some time to set up after building. You should wait for a few seconds after docker-compose builds all services to make sure everything is working. On slow laptops it will take some time for services to run after building.

After running docker-compose as specified in the previous step you should have multiple services running. One of them is a flask server. 

The flask server starts a scheduler that processes the input data in `src` every set amount of time (the default is 900 seconds and can be edited form `config.py` file) and puts the output data in `output.csv` and postgres DB.

You can interact with the flask server with the following requests:

* a POST request on http://localhost:5000/data to force it to process the data in `src` instead of waiting for the schedular.
* a GET request on http://localhost:5000/data to return the data in the postgres DB.

The GET request can use a query string to give filters for the retrieved data. The filters are `is_image_exists`, `min_age`, and `max_age`. For example:

* http://localhost:5000/data?is_image_exists=true&min_age=30.5 will return all users that have a photo and their age >= 30.5.
* http://localhost:5000/data?max_age=30.5 will return all users whose age <= 30.5 regardless of their photo status.
* http://localhost:5000/data?is_image_exists=false will return all users without a photo.

To check that the data is getting to the postgres DB correctly you can use the `pgadmin` service on http://localhost:5050 with the password `postgres`. Then make a connection to the postgres service on port 5432. Note that when you are making a connection to the postgres service the hostname/address is `db` and not `localhost` since docker images have their own dns names. The username and password for the connection are `postgres`.

<a name="code"></a>
# 3. Understanding The Code

The `main.py` file is the launching point of the web service. It starts by making a connection with the `minio` and `postgres` services. It then creates 2 buckets in `minio` if they don't exist. The names of these buckets are taken from `config.py` file. After that, `main.py` starts a flask server which can be found in `app.py`. 

The flask server starts a scheduler to process the input data periodically and has two end-points as defined in "Using The Service". Processing the input data, whether that is done because of scheduler or a call to the end-point, happens by making a call to a function called `process` in the script `image_path_finder.py` which handles the updating. All the previous scripts make use of helper functions defined in `util.py` and from environment variables defined in `config.py`.

Also, whenever the app needs to interact with the postgres DB it will use some of the functions in `db_handler.py`. For example, when sending the output from `output.csv` to the postgres DB it will use the function `handle_row` inside `db_handler.py`.

### Different DNS Names In The Containers

In the dockerfile you will notice that we define an environment variable called `IS_DOCKER`. This environment variable will tell the web service if it is running from docker or not. When the web service is running it will look at that variable and depending on it, the service will either connect to `minio:9000` or `localhost:9000` for establishing the connection to `minio` service. That is because if the web service is running from inside the container then it needs to use the dns names for the containers instead of `localhost`. The same thing will happen for connecting with the database. It will either use `db` or `localhost`.

### Running The Web Service Without Docker

Due to handling the dns names as defined above you can actually launch the service from outside the docker without problems.

First go you `docker-compose.yml` and comment out or delete everything related to the web service. Then run 
```
sudo docker-compose up
```
Now you can use the service from the terminal or any IDE and it will work as expected provided that docker-composed finished building and setting up. This is helpful if you wanted to use a debugger on the code. Make sure you have all the dependencies in `requirements.txt` installed.

### Safety Note
The `config.py` shouldn't actually be uploaded to the git repo and `dockerfile` shouldn't use explicit values in the `ENV` statement in a production environment because they contain passwords, account names, environment variables. It was done this way to ease the use of this repo since this is just a test task. 

The proper way of handling that is creating a `.env` file that defines all those variables and use it in `dockerfile` and the web service itself and gitignoring that file when pushing to the repo.
