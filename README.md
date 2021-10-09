# Provectus-Internship-Task
Provectus test task results by Mahmood Darwish. In this file I will explain how to run and test my solution to the test task. I will also explain some of the logic in the code. Reading this file plus the documentation in the code itself should be suffienct to understand how this code works. The solution to the theoretical questions will also be included in this file.

Note: The solution was only tested on Ubuntu 20.04 LTS. 



## Table of Contents
1. [ Data Processing ](#data)
2. [ Theoretical Questions ](#theo)


<a name="data"></a>
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
before you are allow to copy inside `src`. 

Inside `res` there will be a file called `output.csv` which is the same `output.csv` discribed in the the test task.

Now you should have a running service.


<a name="use"></a>
# 2. Using The Service

The services need some time to set up after building. You should wait for a few seconds after docker-compose builds all services to make sure everything is working. On slow laptops it will take some time for services to run after building.

After running docker-compose as specified in the previous step you should have multiple services running. One of them is a flask server. 

The flask server starts a scheduler that processes the input data in `src` every set amount of time (the default is 120 seconds and can be edited form `config.py` file) and puts the output data in `output.csv` and postgres DB.

You can interact with the flask server with the following requests:

* a POST request on http://localhost:5000/data to manually process the data in `src` instead of waiting for the schedular.
* a GET request on http://localhost:5000/data to return the data in the postgres DB.

The GET request can use a query string to give filters for the reterived data. The filters are `is_image_exists`, `min_age`, `and max_age`. For example:

* http://localhost:5000/data?is_image_exists=true&min_age=30.5 will return all users that have a photo and their age >= 30.5.
* http://localhost:5000/data?max_age=30.5 will return all users whose age <= 30.5 regardless of their photo status.
* http://localhost:5000/data?is_image_exists=false will return all users without a photo.

To check that the data is getting to the postgres DB correctly you can use the `pgadmin` service on http://localhost:5050 with the password `postgres`. Then make a connection to the postgres service on port 5432. Note that when you are making a connection to the postgres service the hostname/address is `db` and not `localhost` since docker images have their own dns names. The username and password for the connection are `postgres`.

<a name="code"></a>
# 3. Understanding The Code

The `main.py` file is the launching point of the web serivce. Starting from there and following the code plus the documentation in the code should be enough to understand the logic. 

Very important note: You should notice that the web service connects to minio on `minio:9000` and not `localhost:9000` and for the postgres DB the host is `db` and not `localhost`. This is because when adding the web serivce to the docker-compose file it will need to use the dns names of the images in the docker-compose file. If we removed the web service from docker-compose file and ran the docker-compose file without it and wanted to use the `main.py` file to connect with the services launched from docker-compose then in the `config.py` file we should change `db_host = "db"` to `db_host = "localhost"` and `minio_host = "minio"` to `minio_host = "localhost"`.


<a name="theo"></a>
# Theoretical Questions

## Table of Contents
1. [ SQL ](#sql)
2. [ Algorithms And Data Structures ](#dsa)
3. [ Linux Shell ](#linux)


<a name="sql"></a>
# 1. SQL
  
  1.

  2. Here we changed the table name from `user` to `users`
  
  ```
  SELECT lastname FROM users 
  GROUP BY lastname 
  HAVING count(lastname) > 1
  ```
  
  3. Here we changed the table name from `user` to `users`
  
  ```
  SELECT username, salary FROM 
  (salary JOIN users ON salary.id = users.id)
  ORDER BY salary DESC LIMIT 1 OFFSET 1
  ```

<a name="dsa"></a>
# 2. Algorithms And Data Structures

  1.

```
def count_connections(list1: list, list2: list) -> int:
	ans = 0

	count = {}

	for i in list1:
		if i in count:
			count[i] += 1
		else:
			count[i] = 1

	for i in list2:
		if i in count:
			ans += 1

	return ans
```

  2. 
  The time complexity for this solution is O(N) since dictionaries are hashmaps and we only loop over the string and do nothing else.
  
  The memory complexity is O(1) since we use a constant number of variables. `last_idx` would have at max 26 values inside it, therefore, constant memory.
```
def calc(s: str) -> int:
	last_idx = {}
	ans = 0
	start_idx = 0

	for i in range(len(s)):
		if s[i] in last_idx:
			start_idx = max(start_idx, last_idx[s[i]] + 1)

		ans = max(ans, i - start_idx + 1)

		last_idx[s[i]] = i

	return ans
```
  3.
  ```
def bs(nums: list, target: int) -> int:
	ans = r + 1

	l = 0
	r = len(nums) - 1
	while l <= r:
	mid = (l + r) // 2
	if nums[mid] == target:
	    return mid
	elif nums[mid] > target:
	    ans = mid
	    r = mid - 1
	else:
	    l = mid + 1

	return ans
  ```

<a name="linux"></a>
# 3. Linux Shell

  1. `sudo lsof -i :80 ; lsof -i :443`
  
  2. `cat /proc/PID/environ | tr '\0' '\n'`
  
  3.
  
  To run in the background:
  
  `nohup python /path/to/my_program.py &`
  
  To close first you have to find the PID using this:
  
  `ps ax | grep my_program.py`
  
  and then kill the process with:
  
  `kill PID`
