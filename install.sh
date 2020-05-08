apt-get update
apt-get install gnupg python3 python3-dev python3-pip image
pip3 install flask pymongo
wget -qO - https://www.mongodb.org/static/pgp/server-4.2.asc | apt-key add -
echo "deb http://repo.mongodb.org/apt/debian buster/mongodb-org/4.2 main" | tee /etc/apt/sources.list.d/mongodb-org-4.2.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo service mongod start
sudo service mongod status
sudo tail /var/log/mongodb/mongod.log  | grep "waiting for con"

# https://docs.mongodb.com/manual/tutorial/install-mongodb-on-debian/
# https://www.w3schools.com/python/python_mongodb_find.asp
# https://realpython.com/flask-google-login/