This guide is assuming you already have access to a Ubuntu 18.04 server and that you want to deploy the app to that server.

First, we need to import all the necessary files to the Ubuntu server machine.
To do this, use WinSCP. This allows to easily exchange files between your host machine and the server.

1. Open up WinSCP, connect to the server

2. Import all the files accompanied in the setup folder. Put the database file (dblatest.psql or dblatest.sql) and the anaconda environment (thesisenv_latest.yml) into the
server's home folder. Add the thesisanalyzer folder to the server as well.

IMPORTANT! Place the `libcg3.so.1` file into `/usr/lib/x86_64-linux-gnu/` folder

Now that all the necessary files are in the server, we start to setup the environment.

3. Use Putty to create a connection (SSH) to the server. Once successful, you see the terminal.

4. Install miniconda.
    ```wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
    chmod +x Miniconda3-latest-Linux-x86_64.sh
    ./Miniconda3-latest-Linux-x86_64.sh
    ```

5. You should now be able to use conda commands. Use
    ```
    conda env create -f thesisenv_latest.yml
    ```
        to import the premade conda environment.

6. Activate the environment with
    ```
    conda activate thesis-env-3.6
    ```

7. Install the missing packages.
    ```
    sudo apt install gunicorn
    conda install flask
    conda install flask-sqlalchemy
    ```

8. Install nginx. Use
    ```
    sudo apt-get update
    sudo apt install nginx
    sudo service nginx status
    ```

9. Use [this](https://www.keycdn.com/support/nginx-reverse-proxy) guide to configure nginx and set proxy_pass value to ```127.0.0.1:8000```

10. Restart nginx for changes to take effect.
    ```
    sudo service nginx reload
    sudo service nginx restart
    sudo service nginx status
    ```

11. Now we need to set up the database. Install Postgresql 11.
    ```
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apkt-key add -
    RELEASE=$(lsb_release -cs)
    echo "deb http://apt.postgresql.org/pub/repos/apt/ ${RELEASE}"-pgdg main | sudo tee  /etc/apt/sources.list.d/pgdg.list
    sudo apt update
    sudo apt -y install postgresql-11
    ```

12. Try to open up the psql terminal with the user postgres.
    ```
    sudo psql -U postgres
    ```
        if you can't login due to wrong password, use this guide to log in.
        https://stackoverflow.com/questions/14588212/resetting-password-of-postgresql-on-ubuntu
        Once you are logged in to the postgres user, enter:
    
    ```
    ALTER USER postgres PASSWORD 'yourpassword';
    ```
    

13. Create the analyzer database.
    ```
    createdb -h localhost -p 5432 -U postgres testdb
    ```

14. Exit from the psql terminal.
    ```
    \q
    ```

15. Import the database from the file.
    ```
    psql -U postgres analyzer < dblatest.sql
    ```

16. You should now have everything set up. Open up the project folder
    ```
    cd thesisanalyzer
    ```

17. Enter your database credentials to the db.py file
    ```
    sudo nano db.py
    ```

18. Run the program with:
    ```
    gunicorn wsgi:application --name thesisanalyzer --workers 4  --bind=127.0.0.1:8000 --timeout 900
    ```

19. If there are missing packages, install them with pip or conda.
20. Press `ctrl+c` to stop the program.
21. If you want to run the program as a daemon, enter
    ```
    gunicorn wsgi:application --name thesisanalyzer --workers 4  --bind=127.0.0.1:8000 --timeout 900 --daemon
    ```

    to stop the program, enter:
    ```
    pkill gunicorn
    ```
            


# Docker setup

1. Clone the code repository to your remote server via `git`.
2. Install `docker`.
3. In the `ThesisAnalyzer` folder, add a new file called `db.py`.
4. Add the variables `DB_PASS` and `DB_USER` with the corresponding database credentials to this file.
5. Add execute rights for 2 files with the following commands:
   1. `chmod +x ./run_docker.sh`
   2. `chmod +x ./ThesisAnalyzer/run_app.sh`
6. Run the `./run_docker.sh` file. This will set up and run the project.

    

    
