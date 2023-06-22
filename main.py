from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()
app.title = "Pic Profile Maker"
app.version = "0.1.0"

@app.get(path="/",tags=["Home"])
def home():
    """
    Returns an HTMLResponse containing a h1 tag with the text "Pic Profile Maker".
    """
    return HTMLResponse('<h1>Pic Profile Maker</h1>')