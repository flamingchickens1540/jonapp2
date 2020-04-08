FROM mongo

RUN apt-get update -y && \
    apt-get install -y gnupg python3 python3-dev python3-pip && \
    pip3 install flask pymongo

# https://docs.mongodb.com/manual/tutorial/install-mongodb-on-debian/
# https://www.w3schools.com/python/python_mongodb_find.asp
# https://realpython.com/flask-google-login/

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY v2 /app

ENTRYPOINT [ "python" ]

CMD [ "app.py" ]
