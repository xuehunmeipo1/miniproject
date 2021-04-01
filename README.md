# Mini Project for Cloud Computing

The project is a prototype of a cloud application to demonstrate REST-based services built with python Flask. The project focuses on the doamin of movie and reviews management supporting multiple CRUD operations to query data. The user can retrieve movies information from the third-party library (https://www.themoviedb.org/?language=en-US) through the app and then build his own movie database. Also, the user can publish movie reviews and modify the review at any time based on his need. The project relies on the RDBS provided by AWS and adopts MySQL to store persistent information. Furthermore, the project also supports basic authentication scheme and hased based management using third-party libraries. And the app is served over https using self-signed SSL Certificate.

## Setup

You can choose to run the app directly or run using docker locally.

1. Run locally

   * Create virtual environment and activate the environment

   ```
   virtualenv -p python3 .cloudEnv
   source .cloudEnv/bin/activate
   ```

   * Install necessary packages

   ```
   pip install -r requirements.txt
   ```

   * Run the app

   ```
   python start.py
   ```

2. Run using docker

   * Build image using the dockerfile
   * Start docker container and publish the port to host 5000

   ```
   docker build -t cloudapp .
   docker run -p 5000:5000 -d cloudapp
   ```

### Note
1. Credentials Info is stored in the config file for reference.
2. Initial running could be slow sometimes
3. Sample post request json can be found under resources 




