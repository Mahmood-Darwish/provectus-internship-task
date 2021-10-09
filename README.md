# Provectus-Internship-Task
Provectus test task results by Mahmood Darwish. In this file I will explain how to run and test my solution to the test task. I will also explain some of the logic in the code. Reading this file plus the documentation in the code itself should be suffienct to understand how this code works. The solution to the theoretical questions will also be included in this file.


# Data Processing Level 3

## Table of Contents
1. [ Understanding The Code ](#code)
2. [ How To Run The Code ](#run)
3. [ Goal ](#goal)
4. [ Authors ](#auth)

<a name="code"></a>
# 1. Understanding The Code
This explaination assumes that the 
The main launching point for the code is the `main.py` file. This file first establishes a connection with a minio service running on `localhost:9000`. Then it connects to a postgres service running on `localhost:5432`. The services can be running from docker-compose or without it but there is an important difference that needs to be addressed if they are running from docker-compose, we will discuss that difference later. 

After creating those connection, the program will create 2 buckets inside minio called `src` and `res` if they don't exist and inside `res` the program will put the file `output.csv` if it doesn't exists. Then it will run a flask server on `localhost:5000`.

The flask server starts a scheduler that processes the input data in `src` every set amount of time and puts the output data in `output.csv` and postgres DB.

You can interact with the flask server with the following requests:

* a POST request on [http://localhost:5000/data](http://localhost:5000/data) to manually process the data in `src` instead of waiting for the schedular.
* a GET request on [http://localhost:5000/data](http://localhost:5000/data) to return the data in the postgres DB.

The GET request can use a query string to give filters for the reterived data. The filters are `is_image_exists`, `min_age`, and `max_age`. 
For example:

* [http://localhost:5000/data?is_image_exists=true&min_age=30.5](http://localhost:5000/data?is_image_exists=true&min_age=30.5) will return all users that have a photo and their age >= 30.5 
* [http://localhost:5000/data?max_age=30.5](http://localhost:5000/data?max_age=30.5) will return all users whose age <= 30.5 regardless of their photo status.
* [http://localhost:5000/data?is_image_exists=false](http://localhost:5000/data?is_image_exists=false) will return all users without a photo.


How to add input data will be discussed in the following section.

<a name="run"></a>
# 2. How To Run The Code

## config file
There are some addresses, password, account names, and so on defined in config.py. This file shouldn't be uploaded on the repo in a production environment since it has secret information but since this is a test task it is done to ease testing.

Since docker images have different dns names than localhost some attention must be paid to the config file depnding how you are running main.py. If you are running main.py as a normal python script then db_host and minio_host in config.py should be localhost, regardless if you are running minio and postgres from docker or not.

If you are running main.py and minio and postgres from the docker-compose file in this repo then you should be 
