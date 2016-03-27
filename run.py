from application import CONFIG
from application import sio
from application import app

if __name__ == "__main__":
    sio.run(app, debug = CONFIG["DEBUG"], port = CONFIG["PORT"])