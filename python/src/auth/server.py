import jwt, datetime, os
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from pymysql import MySQLError

server = Flask(__name__)
mysql = MySQL(server)

# config
server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
server.config["MYSQL_PORT"] = int(os.environ.get("MYSQL_PORT"))

@server.route("/login", methods=["POST"])
def login():
    # get credentials from Basic 'Authentication' header
    auth = request.authorization
    if not auth:
        return "missing credentials", 401
    
    try:
        # check db for username and password
        cur = mysql.connection.cursor()
        res = cur.execute(
                "SELECT email, password FROM user WHERE email=%s", (auth.username,)
        )
    except MySQLError as e:
        return f"Database connection error: {str(e)}", 500

    if res > 0:
        # the elements of the tuple correspond to the columns of the returned row in the same order as specified in the SELECT query.
        # we set email as index 0 in the SELECT query
        # fetchone() resolves to a tuple, returns the next row of the result set as a tuple or None if there are no more rows left to fetch.
        user_row = cur.fetchone()
        email = user_row[0]
        password = user_row[1]
        

        if auth.username == email and auth.password == password:
            return createJWT(auth.username, os.environ.get("JWT_SECRET"), True)
        else:
            return "invalid credentials", 401
    else:
        return "invalid credentials", 401

@server.route("/validate", methods=["POST"])
def validate():
    encoded_jwt = request.headers["Authorization"]

    if not encoded_jwt:
        return "missing credentials", 401
    
    encoded_parts = encoded_jwt.split(" ")
    if len(encoded_parts) != 2 or encoded_parts[0] != "Bearer":
        return jsonify({"error": "invalid token format"}), 401
    
    # the encoded jwt is in the format <type> <credentials>: Bearer <JWT>
    encoded_jwt = encoded_parts[1]
    
    # decode the jwt, then verifies the signature using the secret and algorithm
    try:
        decoded = jwt.decode(encoded_jwt, os.environ.get("JWT_SECRET"), algorithms=["HS256"])
        return decoded, 200
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "invalid token"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    # except:
    #     return "not authorized", 403

    


def createJWT(username, secret, authz):
    # authz is the boolean for admin permissions
    return jwt.encode(
            {
                "username": username,
                "exp": datetime.datetime.now(tz=datetime.timezone.utc)
                + datetime.timedelta(days=1),
                "iat": datetime.datetime.utcnow(),
                "admin": authz,
            },
            secret,
            algorithm="HS256",
        )

if __name__ == "__main__":
    # this tells your os to listen on all public ips
    server.run(host="0.0.0.0", port=5000)
