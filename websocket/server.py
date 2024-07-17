import asyncio
import websockets # type: ignore
import re
import asyncio
import json
import socket
import xml.etree.ElementTree as ET
import traceback
import keyboard
import time
from groq import Groq
import os
import easygui

#CHANGE THIS VALUE TO MATCH WITH CURRENT SCREEN SIZE.
#TODO: Need to find a way to get screen size automatically
SCREENSIZE = [1920,1080]

# Host machine IP
HOST = '127.0.0.1'
# Gazepoint Port
PORT = 4242
ADDRESS = (HOST, PORT)

# Websocket Port
WEBSOCKET_PORT = 8080

SLEEP_DURATION = 0.01 #second
TIMEOUT = 0.1  #second

# Set to store processed messages
#processed_messages = set()

#sync def handle_client(websocket, path):
#    print("WebSocket connection established.")

#    async for message in websocket:  # Loop to continuously receive messages
        # if message not in processed_messages:
#            print(f"Message received from client: {message}")
#            processed_messages.add(message)

    # Process the message (e.g., parse JSON)
    # You can perform any required processing here

    # Send a response back to the client
    # response = "Hello from Python!"
    # await websocket.send(response)
    # print("Response sent to client.")

# Function to handle WebSocket connections
#async def handle_client(websocket, path):
#    try:
#        while True:
#            # Simulate receiving updated screenX and screenY coordinates
#            screenX = get_screenX()  # Replace this with your actual implementation
#            screenY = get_screenY()  # Replace this with your actual implementation
#
#            # Send screenX and screenY coordinates to the client
#            await websocket.send(f"{{\"screenX\": {screenX}, \"screenY\": {screenY}}}")
#            
#            # Simulate some delay before sending the next update
#            await asyncio.sleep(1)
#    except websockets.exceptions.ConnectionClosedError:
#        print("Connection closed")


# Match the value of X,Y from (0,1) to screensize in pixel
def mapScreenCoordinates(screenX, screenY, targetWidth, targetHeight):
    mappedX = screenX * targetWidth
    mappedY = screenY * targetHeight
    return mappedX, mappedY

# Extract FPOGX and FPOGY values as floats from string gaze_data
def getFixationfromString(gaze_data):
    # Define the regular expression pattern
    pattern = r'FPOGX="([-+]?\d*\.\d+|\d+)"\s+FPOGY="([-+]?\d*\.\d+|\d+)"'
    # Use regex to find FPOGX and FPOGY values
    match = re.search(pattern, gaze_data)
    FPOGX_FPOGY = []
    if match:
        FPOGX = float(match.group(1))
        FPOGY = float(match.group(2))

        return FPOGX, FPOGY
    else:
        return False,False

# This function connect with eyetracker server, get gaze position and forward it to websocket client, then receive web content from client
async def eyetracking_running(websocket, path):
    print("WebSocket connection established.")
    """Main function for eye tracking."""
    try:
        # Connect to the eye tracker server
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect(ADDRESS)
        print("SERVER connected.")
        
        # Enable data transmission from the eye tracker
        server.send(b'<SET ID="ENABLE_SEND_POG_FIX" STATE="1" />\r\n')
        server.send(b'<SET ID="ENABLE_SEND_DATA" STATE="1" />\r\n')

        # Continuously receive and send gaze data
        while True:
            # Receive XML data (1024 bytes)
            # The format is like <REC FPOGX="0.48439" FPOGY="0.50313"/>
            casual_data = server.recv(1024)
            
            # Decode received information
            gaze_data = casual_data.decode()
            
            FPOGX, FPOGY = getFixationfromString(gaze_data)
            
            if (FPOGX):
                gazeX, gazeY = mapScreenCoordinates(FPOGX, FPOGY, SCREENSIZE[0], SCREENSIZE[1])
                # Create JSON object
                data = json.dumps({"gazeX": gazeX, "gazeY": gazeY})
                
                # Send JSON data to WebSocket client
                await websocket.send(data)
                
                #Receive response message from client
                response = await asyncio.wait_for(websocket.recv(), timeout=TIMEOUT)
              
              
                print("Response from client:", response)
                
                if keyboard.is_pressed('q'): 
                    f = open("response.txt", "w",  encoding="utf-8")
                    f.write(response + "\n")
                    f.close()
                    time.sleep(1)
                    while keyboard.is_pressed('q'):
                        pass 
                    print('Key Released')
                    

                    f = open(r"C:\Users\Azamat Sydykov\Downloads\websocket\response.txt", 'r', encoding="utf-8")
                    data = f.read()
                    dict_1 = eval(data)
                    if (dict_1["elementType"] == "img"):
                        content = 'describe shortly what is on ' + dict_1["url"]
                        os.environ['GROQ_API_KEY'] = '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'
                        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
                        completion = client.chat.completions.create(
                            model="llama3-8b-8192",
                            messages=[
                                {
                                    "role": "user",
                                    "content": content
                                },
                                
                            ],
                            temperature=1,
                            max_tokens=1024,
                            top_p=1,
                            stream=True,
                            stop=None,
                        )
                        output = ""
                        for chunk in completion:
                            output += chunk.choices[0].delta.content or ""

                        easygui.msgbox(output, title="data processed")
   
                    elif (not any([True for k,v in dict_1.items() if type(v) == float]) and dict_1["elementType"] != "img"):
                        if dict_1['url']:
                            content = "short summary of text" + dict_1["content"] + "taking into account image" + dict_1["url"]
                            os.environ['GROQ_API_KEY'] = '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'
                            client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
                            completion = client.chat.completions.create(
                                model="llama3-8b-8192",
                                messages=[
                                    {
                                        "role": "user",
                                        "content": content
                                    },
                                    
                                ],
                                temperature=1,
                                max_tokens=1024,
                                top_p=1,
                                stream=True,
                                stop=None,
                            )
                            output = ""
                            for chunk in completion:
                                output += chunk.choices[0].delta.content or ""

                            easygui.msgbox(output, title="data processed")
                        else:
                            content = "short summary of text" + dict_1["content"]
                            os.environ['GROQ_API_KEY'] = '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'
                            client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
                            completion = client.chat.completions.create(
                                model="llama3-8b-8192",
                                messages=[
                                    {
                                        "role": "user",
                                        "content": content
                                    },
                                    
                                ],
                                temperature=1,
                                max_tokens=1024,
                                top_p=1,
                                stream=True,
                                stop=None,
                            )
                            output = ""
                            for chunk in completion:
                                output += chunk.choices[0].delta.content or ""

                            easygui.msgbox(output, title="data processed")
                    
                
         
            # Delay the process for a moment to get better performance?
            # TODO: question: do we need both sleep and timeout?
            # await asyncio.sleep(SLEEP_DURATION)
           
    except Exception as e:
        print("An error occurred:", e)
        traceback.print_exc()
    finally:
        if 'server' in locals():
            server.send(b'<SET ID="ENABLE_SEND_DATA" STATE="0" />\r\n')
            server.close()

#Execute websocket server
start_server = websockets.serve(eyetracking_running, "localhost", 8080)
#start_server = websockets.serve(handle_client, "localhost", 8080)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()





  
