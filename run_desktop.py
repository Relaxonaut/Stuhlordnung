import threading
import time
import webbrowser

import uvicorn

from backend.main import app

#desktopsetup mit direktem Browser öffnen

def openbrowser():
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:8000")


if __name__ == "__main__":
    threading.Thread(target=openbrowser).start()
    uvicorn.run(app, host="127.0.0.1", port=8000)
