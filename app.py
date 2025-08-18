import os 
import json 
import base64
import requests
import uvicorn
from fastapi import FastAPI, WebSocket, Request, File,UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import urllib.parse

app = FastAPI()
UPLOAD_DIR = "/var/www/Local_digital_performance/music"
os.makedirs(UPLOAD_DIR, exist_ok=True)
store_genre = {}

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
store_iot_connect = {} #Getting the store map iot control front-end feedback  
store_feedback_sensor = {} #Getting the store map of the input device request 
store_output_feedback = {} #Getting the store output feedback control device 
@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
@app.get("/ws2", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("index2.html", {"request": request})
@app.get("/fetching", response_class=HTMLResponse)
async def get_fetching(request: Request):
    return templates.TemplateResponse("index3.html", {"request": request})
@app.get("/ws3", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("index4.html", {"request": request})
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
   #Getting the motion control and endcode endpoint data 
@app.get("/motion_control/{encoded_data}", response_class=HTMLResponse)
async def motion_control(request: Request, encoded_data: str):
    # Decode from URL encoding (%3D -> =, etc)
    encoded_data_clean = urllib.parse.unquote(encoded_data)
    #Reading the email from the decoded base 64 data and project file name 
    #Get the current project from the email account decoded 
    return templates.TemplateResponse("motion_planning_urdf.html", {
        "request": request,
        "shots_data": encoded_data_clean,
        "model_files":"BD3.URDF",
        "project_names":"BD3"
    })
@app.post("/IoT_connect")
async def IoT_control_motion(request: Request):
      reqiot = await request.json()
      print("Request IoT data: ",reqiot)
      #Store the current position of the robot for getting request of the potion of motion
        
      return reqiot
@app.post("/feedback_sensor")
async def Feedback_sensor_control(request: Request):
      reqfeedback = await request.json() 
      print("Post request feedback sensor data: ",reqfeedback)
      email = list(reqfeedback)[0] #Get the request feedback data 
      project_name = list(reqfeedback.get(email))[0] #Gettin gthe project name from the email payload data 
      payload_sensordata  = reqfeedback.get(email).get(project_name) #Getting the payload data transfer 
      #Store  the payload data of the motion control
      print("Payload store data: ",email,project_name,payload_sensordata)  
      if email not in store_feedback_sensor:
            store_feedback_sensor[email]  = {project_name:payload_sensordata}  #Getting the payload sensor 
      if email in store_feedback_sensor:
            if project_name not in list(store_feedback_sensor[email]): #Getting the project reference 
                      print("Project name not existing in the list ")
                      store_feedback_sensor[email][project_name] = payload_sensordata

            if project_name in list(store_feedback_sensor[email]):
                      print("Project name is existing in the list")
                      store_feedback_sensor[email][project_name] = payload_sensordata 

@app.post("/feedback_motion_control")
async def Feedbackmotion_control(request: Request):
      reqfeedmotion = await request.json() 
      print("Post feedback motion control") 
      email = reqfeedmotion.get('email') #Getting the feedback motion input email 
      project_name = "BD3" 
      return store_feedback_sensor[email][project_name] #Getting the payload feedback sensor 
                                   
@app.post("/output_feedbackcontrol")
async def outputfeedbackcontrol(request: Request):
      reqoutfeed = await request.json() #Getting the request of the output from the front-end 
      print("Post request output feedback control: ",reqoutfeed)
      email =  reqoutfeed.get('email') #Get the email data from the payload request 
      #Getting the payload data output from the post request feedback control
      return store_feedback_sensor[email]        
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            # 1. Receive incoming JSON payload
            data = await websocket.receive_text()
            payload = json.loads(data)
            print("Received payload:", payload)

            # 2. Build a feedback response (you can customize this)
            feedback = {
                "status": "ok",
                "received_keys": list(payload.keys()),
                "timestamp": __import__("time").time()
            }

            # 3. Send it back over the WebSocket
            await websocket.send_text(json.dumps(feedback))

        except Exception as e:
            print("WebSocket error:", e)
            break
@app.websocket("/ws2")
async def websocket_endpoint2(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)

            # Respond as fast as possible
            feedback = {
                "status": "ok",
                "timestamp": time.time(),
                "keys": list(payload.keys())
            }

            # Send response immediately
            await websocket.send_text(json.dumps(feedback))

    except Exception as e:
        print("WebSocket closed or errored:", e)
        await websocket.close()
#End-point fetching test function 
@app.post("/post_back_end")
async def fetching_back_end(request: Request):
        reqdat = await request.json()
        print("reqdat: ",reqdat)
        return reqdat 
@app.websocket("/optimize")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)

            # Process your data here
            print("Received:", payload)

            # Send a response
            await websocket.send_text(json.dumps({
                "status": "ok",
                "message": "Data received successfully"
            }))

            # Explicitly free memory (optional but helps in long sessions)
            del payload
            del data
    except Exception as e:
        print("WebSocket error:", e)
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".mp3"):
        raise HTTPException(status_code=400, detail="Only MP3 files are allowed")

    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    #After write buffer post request to the main processing server
    '''
    file_path = '/var/www/Local_digital_twin_performance/music/'+file.filename
    server_url = 'http://192.168.50.231:9000/upload'
    with open(file_path, 'rb') as f:
        files = {'file': (file_path, f, 'audio/mpeg')}
        response = requests.post(server_url, files=files)
    print(response.status_code)
    print(response.json())
    '''     
    return JSONResponse(content={"message": "File uploaded successfully"}, status_code=200)
@app.post("/genre_request") 
async def get_genredata(request: Request): 
        reqgenre = await request.json() 
        print("Getting genre: ",reqgenre)
        reqdat = requests.post("http://192.168.50.231:9000/genre_request",json=reqgenre).json()
        return {reqgenre['filename']:reqdat}     
@app.get("/total_genre_store")
def genre_data():

     return store_genre
#if __name__ == "__main__":
#    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

