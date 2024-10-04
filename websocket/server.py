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
import tkinter as tk
from tkinter import messagebox

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
TIMEOUT = 20  #second


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
count = 0
# This function connect with eyetracker server, get gaze position and forward it to websocket client, then receive web content from client
async def eyetracking_running(websocket, path):
    global count
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
                response_dict = eval(response)
                
              
              
                print("Response from client:", response)
                if keyboard.is_pressed('a'):
                    if count == 0:
                        while keyboard.is_pressed('a'):
                            pass 
                        print('Key Released')
                        f = open("response.txt", "w",  encoding="utf-8")
                        f.write(response + "\n")
                        f.close()
                        print(count)
                        count = count + 1
                        
                    else:
                        while keyboard.is_pressed('a'):
                            pass 
                        print('Key Released')
                        with open(r"response.txt", 'a', encoding="utf-8") as f:
                            f.write(response + '\n')
                        print(count)
                        count = count + 1
                            
                if keyboard.is_pressed('q'):
                    if count == 0 or count == 1:
                        f = open("response.txt", "w",  encoding="utf-8")
                        f.write(response + "\n")
                        f.close()
                        time.sleep(1)
                        while keyboard.is_pressed('q'):
                            pass 
                        print('Key Released')
                        print(count)
                        

                        f = open(r"C:\Users\Azamat Sydykov\Downloads\websocket\response.txt", 'r', encoding="utf-8")
                        data = f.read()
                        dict_1 = eval(data)
                        
                        # Set the API key and URL
                        os.environ['GROQ_API_KEY'] = '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'
                        

                        class Application(tk.Tk):
                            def __init__(self):
                                super().__init__()
                                self.title("Send to LLM")
                                popup_width = 150
                                popup_height = 150
                                if 0 < abs(int(dict_1["borderX"])) - 100 < SCREENSIZE[0] - popup_width:
                                    popup_x = abs(int(dict_1["borderX"])) - 100 + (popup_width - (abs(int(dict_1["borderX"])) - 100))
                                elif abs(int(dict_1["borderX"])) - 100 > SCREENSIZE[0] - popup_width:
                                    popup_x = abs(int(dict_1["borderX"])) - 100 - ((abs(int(dict_1["borderX"])) - 100) - (SCREENSIZE[0] - popup_width))
                                else:
                                    popup_x = (abs(int(dict_1["borderX"]))) 
                                if 0 < abs(int(dict_1["borderY"])) - 100 < SCREENSIZE[1] - popup_width:
                                    popup_y = (abs(int(dict_1["borderY"])) - 100) + (popup_height - (abs(int(dict_1["borderY"])) - 100))
                                elif abs(int(dict_1["borderX"])) - 100 > SCREENSIZE[1] - popup_height:
                                    popup_y = abs(int(dict_1["borderX"])) - 100 - ((abs(int(dict_1["borderY"])) - 100) - (SCREENSIZE[1] - popup_height))
                                else:                                                   
                                    popup_y = (abs(int(dict_1["borderY"]))) 
                                
                                self.geometry(f'{popup_width}x{popup_height}+{popup_x}+{popup_y}')
                                self.focus_force()
                                self.attributes("-topmost", True)
                                self.action = tk.StringVar()
                                self.action.set('summarize')

                                self.create_widgets()

                            def create_widgets(self):
                            

                                self.actions = ['summarize', 'explain', 'paraphrase', 'describe the image']
                                self.action_buttons = []
                                for action_name in self.actions:
                                    action_button = tk.Button(self, text=action_name, command=lambda action_name=action_name: self.send_request(action_name), font=('Arial', 12, 'bold'))
                                    action_button.pack(fill="x", expand=True)
                                    self.action_buttons.append(action_button)

                            def send_request(self, choice):
                                prompt = ''
                                if choice == 'summarize':
                                    prompt += f" I will give  you some webpage element, please help me to summarize the content of element if the element type is div or pharagraph also consider the images inside these elements if they have it, and summarize together with the image() . Do not need to show the element type, just give me summary of both the content and images in no more than 5 sentences." + dict_1["content"] + ', '.join(dict_1["urls"])
                                   
                                elif choice == 'explain':
                                    prompt = 'explain simply and shortly the text about ' + dict_1["content"]
                                elif choice == 'paraphrase':
                                    prompt = 'paraphrase the text ' + dict_1["content"] 
                                elif choice == 'describe the image':
                                    
                                    prompt = "describe the image in given url if elementType is img, or decribe url what is on background image if it is not empty, but content is empty.Do not show the urls in output message. Just Give me desciption what is on image" + ', '.join(dict_1["urls"])
                                        
                                else:
                                    messagebox.showerror("Error", "Invalid choice")
                                    return

                                client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
                                completion = client.chat.completions.create(
                                    model="llama3-8b-8192",
                                    messages=[
                                        {
                                            "role": "user",
                                            "content": prompt
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
                                popup_window = tk.Toplevel(self)
                                popup_window.title("Result")
                                popup_window.focus_force()
                                popup_window.minsize(10, 10)  # Sets the minimum window size
                                popup_window.resizable(True, True)  # Allows the window to be resized

                                frame = tk.Frame(popup_window)
                                frame.pack(fill="both", expand=True)

                                popup_widget = tk.Text(frame, wrap=tk.WORD)
                                popup_widget.insert('1.0', output)

                                
                                scroll_bar = tk.Scrollbar(frame, orient='vertical', command=popup_widget.yview)
                                popup_widget['yscrollcommand'] = scroll_bar.set

                                scroll_bar.pack(side='right', fill='y')
                                popup_widget.pack(side='left', fill="both", expand=True)

                            
                                popup_window.update_idletasks()
                                num_lines = len(popup_widget.get('1.0', tk.END).splitlines())
                                width = 600
                                height = max(150, num_lines * 20 + 50)
                                while True:
                                    popup_window.geometry(f'{width}x{height}')
                                    popup_window.update_idletasks()
                                    popup_widget.update_idletasks()
                                    popup_window.update()
                                    if popup_widget.get(1.0, tk.END) != '\n':
                                        break
                                    popup_window.geometry(f'{width}x{height+20}')
                                    height += 20
                                popup_window.update_idletasks()

                            def mainloop(self):
                                super().mainloop()

                        if __name__ == "__main__":
                            app = Application()
                            app.mainloop()
                        print(count)
                        count = 0
                    else:
                        while keyboard.is_pressed('q'):
                            pass 
                        print('Key Released')
                        print(count)
                        dict_list = []

                        with open(r"response.txt", 'r', encoding="utf-8") as f:
                            for line in f:
                                item = eval(line.strip())
                                dict_list.append(item)

                        
                        os.environ['GROQ_API_KEY'] = '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'
                        

                        class Application(tk.Tk):
                            def __init__(self):
                                super().__init__()
                                self.title("Send to LLM")
                                popup_width = 150
                                popup_height = 150
                                for item in dict_list:
                                    pass
                                
                               
                                
                                self.geometry(f'{popup_width}x{popup_height}')
                                self.focus_force()
                                self.attributes("-topmost", True)
                                self.action = tk.StringVar()
                                self.action.set('summarize')

                                self.create_widgets()

                            def create_widgets(self):
                            

                                self.actions = ['summarize', 'explain', 'paraphrase', 'describe the image']
                                self.action_buttons = []
                                for action_name in self.actions:
                                    action_button = tk.Button(self, text=action_name, command=lambda action_name=action_name: self.send_request(action_name), font=('Arial', 12, 'bold'))
                                    action_button.pack(fill="x", expand=True)
                                    self.action_buttons.append(action_button)

                            def send_request(self, choice):
                                prompt = ''
                                if choice == 'summarize':
                                    prompt = "I will give you some webpage elements, please help me to summarize the content of element if the element type is div or pharagraph also consider the images inside these elements if they have it, and describe the image in given url if element type is img. Do not need to show the element type, just give me summary of both the content and images in no more than 5 sentences."
                                    for item in dict_list:
                                        prompt += f"{item}"
                                elif choice == 'explain':
                                    prompt = "I will give you some webpage elements, please help me to explain the content of element(s) if the element type is div or paragraph, and explain also the image in given url(s) . Do not need to show the element type, just give me explanation of both the content and images in no more than 5 sentences."
                                    for item in dict_list:
                                        prompt += f"{item}"
                                elif choice == 'paraphrase':
                                    prompt = "Paraphrase briefly this texts as one"
                                    for item in dict_list:
                                         prompt =+ (f"{item['content']}")
                                elif choice == 'describe the image':

                                    prompt = "I will give you some webpage elements, please help me to describe what is on image ,or all of multiple images if there is many images, in given url(s) if element type is img or also describe the url of background image if i is not empty, but content shoul be empty. Do not need to show the content, element type,urls, borderX and other unnecessary technical details from the file, just give me description of  images for simple user "
                                    for item in dict_list:
                                         prompt += f"{item}"
                                else:
                                    messagebox.showerror("Error", "Invalid choice")
                                    return

                                client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
                                completion = client.chat.completions.create(
                                    model="llama3-8b-8192",
                                    messages=[
                                        {
                                            "role": "user",
                                            "content": prompt
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
                                popup_window = tk.Toplevel(self)
                                popup_window.title("Result")
                                popup_window.focus_force()
                                popup_window.minsize(10, 10)  # Sets the minimum window size
                                popup_window.resizable(True, True)  # Allows the window to be resized

                                frame = tk.Frame(popup_window)
                                frame.pack(fill="both", expand=True)

                                popup_widget = tk.Text(frame, wrap=tk.WORD)
                                popup_widget.insert('1.0', output)

                                
                                scroll_bar = tk.Scrollbar(frame, orient='vertical', command=popup_widget.yview)
                                popup_widget['yscrollcommand'] = scroll_bar.set

                                scroll_bar.pack(side='right', fill='y')
                                popup_widget.pack(side='left', fill="both", expand=True)

                            
                                popup_window.update_idletasks()
                                num_lines = len(popup_widget.get('1.0', tk.END).splitlines())
                                width = 600
                                height = max(150, num_lines * 20 + 50)
                                while True:
                                    popup_window.geometry(f'{width}x{height}')
                                    popup_window.update_idletasks()
                                    popup_widget.update_idletasks()
                                    popup_window.update()
                                    if popup_widget.get(1.0, tk.END) != '\n':
                                        break
                                    popup_window.geometry(f'{width}x{height+20}')
                                    height += 20
                                popup_window.update_idletasks()

                            def mainloop(self):
                                super().mainloop()

                        if __name__ == "__main__":
                            app = Application()
                            app.mainloop()
                        count = 0
        

                            

                    
                
         
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





  
