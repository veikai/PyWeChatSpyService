from flask import Flask
from redis import ConnectionPool, Redis
import toml

with open("conf.toml", "r") as rf:
    conf = toml.load(rf)

pool = ConnectionPool(host=conf["Redis"]["host"], port=6379, password=conf["Redis"]["password"], db=0)
r = Redis(connection_pool=pool)


app = Flask(__name__)


@app.route("/<key>")
def index(key):
    if r.get(key):
        return "1"
    return "0"


if __name__ == '__main__':
    app.run(host="0.0.0.0")

