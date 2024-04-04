import os, gridfs, pika, json
from flask import Flask, request, send_file
from flask_pymongo import PyMongo
# packages that will be created and modules to be imported
from auth import validate
from auth_svc import access
from storage import util
from bson.objectid import ObjectId



server = Flask(__name__)
# configures Flask-PyMongo to use the videos database by default. 
# when you use fs.put() to store a file using GridFS, Flask-PyMongo will automatically use the videos database for storing the file.
# server.config["MONGO_URI"] = "mongodb://host.minikube.internal:27017/videos"



# allows us to interface with our MongoDB (class PyMongo(object) Manages MongoDB connections for your Flask app.)
mongo_video = PyMongo(
    server,
    uri="mongodb://host.minikube.internal:27017/videos"    
)

mongo_mp3 = PyMongo(
    server,
    uri="mongodb://host.minikube.internal:27017/mp3s"
)

fs_videos = gridfs.GridFS(mongo_video.db)
fs_mp3s = gridfs.GridFS(mongo_mp3.db)

# allows us to use MongoDB's gridfs
# when you pass mongo.db to gridfs.GridFS, it refers to the default database associated with the mongo instance
# this is typically the database specified in the MONGO_URI configuration variable. 
# fs = gridfs.GridFS(mongo.db)

# create a blocking connection to a RabbitMQ server. Code will wait until the connection is established before proceeding
# pass in the host for our rabbitmqq as argument. Service name in kubernetes resolves to the host
connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()


@server.route("/login", methods=["POST"])
def login():
    # we create a module called access that's going to contain this login function
    token, err = access.login(request)

    if not err:
        return token
    else:
        return err

@server.route("/upload", methods=["POST"])
def upload():
    # we create the validate module with the token function
    access, err = validate.token(request)
    if err:
        return err, 401
    
    try:
        access = json.loads(access)
    except json.JSONDecodeError:
        return "Invalid access token", 401
    
    # check the "admin" claims resolve to True or False
    if access["admin"]:
        # check that request.files returns only 1 dictionary value
        if len(request.files) > 1 or len(request.files) < 1:
            return "exactly 1 file required", 400
        
        # iterate through the items in the dictionary (there should only be 1)
        for _, f in request.files.items():
            # to create the util.upload() function with parameters: file, fs instance, rabbitmq channel, access token
            # function returns an error if something goes wrong else returns None
            err = util.upload(f, fs_videos, channel, access)

            if err:
                return err

        return "success!", 200
    else:
        return "not authorized", 401

@server.route("/download", methods=["GET"])
def download():
    access, err = validate.token(request)
    if err:
        return err, 401
    
    try:
        access = json.loads(access)
    except json.JSONDecodeError:
        return "Invalid access token", 401
    
    # check the "admin" claims resolve to True or False
    if access["admin"]: 
        fid_string = request.args.get("fid")

        if not fid_string:
            return "fid is required", 400
        
        # convert fid string provided to a Object ID
        try:
            # retrieve mp3 file from MongoDB, then store it in out variable as a file object
            out = fs_mp3s.get(ObjectId(fid_string))
            return send_file(out, download_name=f"{fid_string}.mp3")
        except Exception as err:
            print(err)
            return "internal server error", 500


    return "not authorized", 401

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)
