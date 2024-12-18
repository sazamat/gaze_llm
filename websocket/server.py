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
import signal
import sys
import subprocess
import psutil

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
TIMEOUT = 15  #second

Numb_of_sentence = 5
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

count_a_press = 0


quit_required = False

# def free_port(port):
#     """Terminate any process using the given port."""
#     for proc in psutil.process_iter(attrs=['pid', 'name', 'connections']):
#         for conn in proc.info['connections']:
#             if conn.laddr.port == port:
#                 print(f"Terminating process {proc.info['name']} (PID {proc.info['pid']}) using port {port}.")
#                 proc.terminate()
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
            global count_q_press
            
            if (FPOGX):
                gazeX, gazeY = mapScreenCoordinates(FPOGX, FPOGY, SCREENSIZE[0], SCREENSIZE[1])
                # Create JSON object
                data = json.dumps({"gazeX": gazeX, "gazeY": gazeY})
                
                # Send JSON data to WebSocket client
                await websocket.send(data)
                
                
                #Receive response message from client
                response = await asyncio.wait_for(websocket.recv(), timeout=TIMEOUT)
                
                response_dict = eval(response)
                
              
                
                #print("Response from client:", response)
               
                
                
                if(response_dict["check_selected"] == 1):
                    global quit_required
                    global count_a_press
                    #--------------------------------------------------- press 'a'--------------------------------------------------------------------------------------------------------
                    
                    if keyboard.is_pressed('a'):
                        
                    
                        while keyboard.is_pressed('a'):
                            pass 
                        
                        with open(r"response.txt", "r", encoding="utf-8") as f:
                            existing_lines = set(line.strip() for line in f)
                        
                        if response not in existing_lines:
                            with open(r"response.txt", "a", encoding="utf-8") as f:
                                f.write(response + '\n')
                            
                    count_a_press += 1  # Increment counter only for new responses
                            
                        #------------------------------------------------------------if we press 'q'-----------------------------------------------------------------------------------------------        
                    
                    if count_a_press == 0 and keyboard.is_pressed("q") and quit_required ==False:
                        
                        while keyboard.is_pressed('q'):
                            pass
                       
                        f = open("response.txt", "w",  encoding="utf-8")
                        f.write(response + "\n")
                        f.close()
                        
                        f = open(r"C:\Users\Azamat Sydykov\Downloads\websocket\response.txt", 'r', encoding="utf-8")
                        data = f.read()
                        dict_1 = eval(data)
                        URLs=[]
                        count_a_press = 0
                        
                        for url in dict_1["urls"]:
                            if (dict_1["elementType"] == "img" ) :
                                URLs.append(url)
                        
                        
                        description = []
                        
                        
                        
                            
                        class Application(tk.Tk):
                            def __init__(self):
                                super().__init__()
                                self.title("LLM response")
                                self.popup_window = None
                                if dict_1["elementType"] != 'img':
                                    popup_width = 160
                                    popup_height = 150
                                elif dict_1["elementType"] == 'img' or (str(dict_1["content"]).strip() == '' and dict_1["styles"]["backgroundImage"] is not None):
                                    popup_width = 170
                                    popup_height = 90
                                if 0 < abs(int(dict_1["borderX"])) - 100 < SCREENSIZE[0] - popup_width:
                                    popup_x = abs(int(dict_1["borderX"])) - 100 + (popup_width - (abs(int(dict_1["borderX"])) - 100))
                                elif abs(int(dict_1["borderX"])) - 100 > SCREENSIZE[0] - popup_width:
                                    # popup_x = abs(int(dict_1["borderX"])) - 100 - ((abs(int(dict_1["borderX"])) - 100) - (SCREENSIZE[0] - popup_width))
                                    popup_x = 700
                                else:
                                    popup_x = (abs(int(dict_1["borderX"]))) 
                                if 0 < abs(int(dict_1["borderY"])) - 100 < SCREENSIZE[1] - popup_width:
                                    popup_y = (abs(int(dict_1["borderY"])) - 100) + (popup_height - (abs(int(dict_1["borderY"])) - 100))
                                elif abs(int(dict_1["borderY"])) - 100 > SCREENSIZE[1] - popup_height:
                                    # popup_y = abs(int(dict_1["borderY"])) - 100 - ((abs(int(dict_1["borderY"])) - 100) - (SCREENSIZE[1] - popup_height))
                                    popup_y = 700
                                else:                                                   
                                    popup_y = (abs(int(dict_1["borderY"]))) 
                                
                                self.geometry(f'{popup_width}x{popup_height}+{popup_x-160}+{popup_y}')
                                self.attributes("-topmost", True)
                                self.create_widgets()
                                self.bind_keys()
                                

                            def create_widgets(self):
                                self.actions = []
                                if dict_1["elementType"] != 'img' and dict_1["styles"]["backgroundImage"] ==  'none' :
                                    self.actions = ['Summarize', 'Translate into Italian', 'Paraphrase','Add element']
                                elif dict_1["elementType"] == 'img' or (str(dict_1["content"]).strip() == '' or dict_1["styles"]["backgroundImage"] != 'none'):
                                    self.actions = ['Describe the image', 'Add element']
                                
                                self.action_buttons = []
                                for action_name in self.actions:
                                    action_button = tk.Button(self, text=action_name, command=lambda action_name=action_name: self.send_request(action_name), font=("Arial", 12),
                bg="#0078D7",
                fg="white",
                activebackground="#005fa3",
                relief="raised",
                bd=3,
                anchor="w",
                padx=10,
                pady=5,)
                                    action_button.pack(fill="x", expand=True)
                                    self.action_buttons.append(action_button)
                            os.environ['GROQ_API_KEY'] = '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'
                            # def handle_action(self, action_name):
                            #     if action_name == 'add element':
                            #         self.add_element_action()
                            #     else:
                            #         self.send_request(action_name)

                            # def add_element_action(self):
                            #     count_a_press += 1
                            #     self.close_application()
                            def send_request(self, choice):
                                global count_a_press
                                prompt = ""
                                if choice == 'Summarize':
                                    if dict_1["elementType"] == 'main':
                                        prompt = 'summarize shortly each contents seperately \n' + dict_1["content"] + ', '.join(dict_1["urls"]) 
                                    else:
                                        prompt += f" Shortly summarize each contents  " + dict_1["content"] 
                                        if dict_1["urls"] != "":
                                            prompt += ', '.join(dict_1["urls"]) 
                                        if dict_1["styles"]["backgroundImage"] != 'none' and str(dict_1["content"]).strip() == "":
                                            
                                            prompt +=  dict_1["styles"]["backgroundImage"] 
                                        
                                    print(prompt)
                                    # for i in range(len(description)):
                                    #     prompt += description[i] 
                                elif choice == 'Translate into Italian':
                                    prompt = 'Translate into Italian the text: ' + dict_1["content"]
                                elif choice == 'Paraphrase':
                                    prompt = 'paraphrase the text very shortly: ' + dict_1["content"]   
                                elif choice == 'Describe the image':
                                    prompt = f'Sumarize  this description (and alt text if present)'
                                    if (dict_1["elementType"] == 'img' or  dict_1["styles"]["backgroundImage"] is not None):
                                        for i in range(len(dict_1["urls"])):
                                            client = Groq()
                                            completion = client.chat.completions.create(
                                            model="llama-3.2-11b-vision-preview",
                                                messages=[
                                                    {
                                                        "role": "user",
                                                        "content": [
                                                            {
                                                                "type": "text",
                                                                "text": "What's in this image? "
                                                            },
                                                            {
                                                                "type": "image_url",
                                                                "image_url": {
                                                                    "url": URLs[i]
                                                                }
                                                            }
                                                        ]
                                                    },
                                                    {
                                                        "role": "assistant",
                                                        "content": ""
                                                    }
                                                ],
                                                temperature=1,
                                                max_tokens=1024,
                                                top_p=1,
                                                stream=False,
                                                stop=None,
                                            )
                                            
                                            description.append(completion.choices[0].message.content)
                                    
                                    prompt +=  dict_1["content"] + "\n"
                                    for i in range(len(description)):
                                        prompt += description[i]
                                    if dict_1["styles"]["backgroundImage"] != 'none' and str(dict_1["content"]).strip() == "":
                                            
                                            prompt +=  dict_1["styles"]["backgroundImage"] 
                                    
                                    
                                    print (prompt)
                                
                                elif choice == 'Add element':
                                    
                                    count_a_press += 1
                                    self.close_application()
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
                                
                                self.show_popup("Result", output)

                            def show_popup(self, title, output):
                                if self.popup_window is None or not self.popup_window.winfo_exists():
                                    self.popup_window = tk.Toplevel(self)
                                    # self.popup_window.title(title)
                                    self.popup_window.attributes("-topmost", True) 
                                    self.popup_window.focus_set()
                                    self.popup_window.minsize(10, 10)  # Sets the minimum window size
                                    self.popup_window.resizable(True, True)  # Allows the window to be resized
                                    self.popup_window.configure(bg="#ffffff")
                                    self.popup_window.focus_force()

                                    frame = tk.Frame(self.popup_window, bg="#f1f1f1", padx=2, pady=2)
                                    frame.pack(fill="both", expand=True)

                                    title_label = tk.Label(
                                        frame,
                                        text=title,
                                        font=("Arial", 11, "bold"),
                                        bg="#0078D7",
                    fg="white",
                    activebackground="#005fa3",
                    relief="raised",
                    
                                        anchor="center",
                                        pady=2,
                                    )
                                    title_label.pack(fill="x", pady=(0, 10))
                                    

                                    popup_widget = tk.Text(frame, wrap=tk.WORD, font=("Arial", 10))
                                    popup_widget.insert('1.0', output)

                                    scroll_bar = tk.Scrollbar(frame, orient='vertical', command=popup_widget.yview)
                                    popup_widget['yscrollcommand'] = scroll_bar.set
                                    scroll_bar.pack(side='right', fill='y')
                                    popup_widget.pack(side='left', fill="both", expand=True)

                                    self.popup_window.update_idletasks()
                                    num_lines = len(popup_widget.get('1.0', tk.END).splitlines())
                                    width = 600
                                    height = max(150, num_lines * 20 + 50)
                                    while True:
                                        if 0 < abs(int(dict_1["borderX"])) - 100 < SCREENSIZE[0] - 160:
                                            popup_x = abs(int(dict_1["borderX"])) - 100 + (160 - (abs(int(dict_1["borderX"])) - 100))
                                        elif abs(int(dict_1["borderX"])) - 160 > SCREENSIZE[0] - 160:
                                            popup_x = 700
                                        else:
                                            popup_x = (abs(int(dict_1["borderX"]))) 
                                        if 0 < abs(int(dict_1["borderY"])) - 160 < SCREENSIZE[1] - 160:
                                            popup_y = (abs(int(dict_1["borderY"])) - 160) + (160 - (abs(int(dict_1["borderY"])) - 100))
                                        elif abs(int(dict_1["borderY"])) - 160 > SCREENSIZE[1] - 160:
                                            
                                            popup_y = 700
                                        else:                                                   
                                            popup_y = (abs(int(dict_1["borderY"])))
                                        
                                        self.popup_window.geometry(f'{width}x{height}+{popup_x +240}+{popup_y + 200}')
                                        self.popup_window.update_idletasks()
                                        popup_widget.update_idletasks()
                                        self.popup_window.update()
                                        if popup_widget.get(1.0, tk.END) != '\n':
                                            break
                                        
                                        self.popup_window.geometry(f'{width+150}x{height+150}+{800}+{800}')
                                        height += 20
                                    self.popup_window.update_idletasks()

                            def bind_keys(self):
                                self.after(10, self.check_keys)

                            def check_keys(self):
                                if not self.winfo_exists():  # Ensure the main window exists
                                    return
                                
                                quit_required = True 
                                global count_a_press
                                if keyboard.is_pressed("q") and quit_required == True:
                                    while keyboard.is_pressed("q"):
                                        pass
                                    self.close_application()
                                    
                                if keyboard.is_pressed('a'):
                                    self.close_application()  # Close both windows
                                    count_a_press += 1
                                if quit_required:    
                                    self.after(100, self.check_keys)  # Check again after 100ms

                            def create_main_window(self):
                                if self.winfo_exists():  # Check if the window is still valid
                                    self.deiconify() 
                                

                            def close_application(self):
                                if self.popup_window and self.popup_window.winfo_exists():
                                    self.popup_window.destroy()  # Close the popup if it's open
                                if self.winfo_exists():
                                    self.destroy()  # Close the main application

                        if __name__ == "__main__":
                            app = Application()
                            app.withdraw()  # Start hidden
                            app.title("Task selection")
                            app.mainloop()
                        
                    quit_required = False
                    if (count_a_press == 0):
                        with open("response.txt", "w") as f:
                            f.write("")

                            
#-----------------------------------------------------------------------press q after you press 'a' ----------------------------------------------------------------------------------------                            
                if count_a_press > 0 and keyboard.is_pressed('q'):
                    
                    while keyboard.is_pressed('q'):
                        pass
                
                    quit_required = True
                    

                
                    dict_list = []
                    if response_dict["check_selected"] == 1:
                        with open(r"response.txt", "r", encoding="utf-8") as f:
                            # Read lines and strip trailing newline characters
                            existing_lines = set(line.strip() for line in f)
                            
                            if response not in existing_lines:
                                with open(r"response.txt", "a", encoding="utf-8") as f:
                                    f.write(response + '\n')
                       

                            
                            

                    with open(r"response.txt", 'r', encoding="utf-8") as f:
                        for line in f:
                            item = eval(line.strip())
                            dict_list.append(item)
                    
                    urls = []
                    count_a_press = 0
                    for i in range(len(dict_list)):
                        if(dict_list[i]["elementType"] == 'img') :
                            urls.append(dict_list[i]["urls"])
                            

                        
                    
                
        

                    
                    string_urls = [''.join(i) for i in urls]
                    
                    
                    
                    if os.path.getsize('response.txt') > 0:

                        class Application(tk.Tk):
                            def __init__(self):
                                super().__init__()
                                self.title("LLM response")
                                self.popup_window = None
                                if all(d["elementType"] == 'img' for d in dict_list):
                                    popup_width = 170
                                    popup_height = 90
                                if any(d["elementType"] != 'img' for d in dict_list) and any(d["elementType"] == 'img' for d in dict_list):
                                    popup_width = 170
                                    popup_height = 200
                                if all(d["elementType"] != 'img' for d in dict_list):
                                    popup_width = 170
                                    popup_height = 160                  
                                self.geometry(f'{popup_width}x{popup_height}')
                                self.attributes("-topmost", True)
                                self.create_widgets()
                                self.bind_keys()
    
                            def create_widgets(self):
                                if all(
                                        isinstance(d, dict) and (
                                            d.get("elementType") == "img" or 
                                            d.get("styles", {}).get("backgroundImage") != "none"
                                        )
                                        for d in dict_list
                                    ):
                                    self.actions = ['Describe the image', 'Add element']
                                    print("yes")
                                if all(d["elementType"] != 'img' and d["styles"]["backgroundImage"] == 'none'  for d in dict_list):
                                    self.actions = ['Summarize', 'Translate into Italian', 'Paraphrase', 'Add element']
                                if any(d["elementType"] != 'img' for d in dict_list) and any(d["elementType"] == 'img' for d in dict_list):
                                    self.actions = ['Summarize', 'Translate into Italian', 'Paraphrase', 'Describe the image', 'Add element']

                                
                                self.action_buttons = []
                                for action_name in self.actions:
                                    action_button = tk.Button(self, text=action_name, command=lambda action_name=action_name: self.send_request(action_name), font=("Arial", 12),
                    bg="#0078D7",
                    fg="white",
                    activebackground="#005fa3",
                    relief="raised",
                    anchor="w",
                    bd=3,
                    padx=10,
                    pady=5,)
                                    action_button.pack(fill="x", expand=True)
                                    self.action_buttons.append(action_button)
                            os.environ['GROQ_API_KEY'] = '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'
                            def send_request(self, choice):
                                prompt = ""
                                global count_a_press
                                
                                
                                
                                if choice == 'Summarize':
                                    prompt = "Summarize  shortly each contents seperately: "
                                    count_img = 0
                                    count_txt = 0
                                    for i in range(len(dict_list)):
                                        
                                        if (dict_list[i]["elementType"] == 'img'):
                                            count_img += 1
                                            description = ''
                                            url= ''
                                            
                                            url = dict_list[i]["urls"]
                                            print(url)
                                            client = Groq()
                                            completion = client.chat.completions.create(
                                            model="llama-3.2-11b-vision-preview",
                                                messages=[
                                                    {
                                                        "role": "user",
                                                        "content": [
                                                            {
                                                                "type": "text",
                                                                "text": "What's in this image? "
                                                            },
                                                            {
                                                                "type": "image_url",
                                                                "image_url": {
                                                                    "url": str(''.join(url))
                                                                }
                                                            }
                                                        ]
                                                    },
                                                    {
                                                        "role": "assistant",
                                                        "content": ""
                                                    }
                                                ],
                                                temperature=1,
                                                max_tokens=1024,
                                                top_p=1,
                                                stream=False,
                                                stop=None,
                                            )
                                            description = completion.choices[0].message.content
                                            
                                            prompt += f"Image {count_img}: "
                                            prompt += f"{dict_list[i]["content"]}\n "
                                            prompt += description
                                            
                                        else:
                                            count_txt += 1
                                            prompt += f"Text {count_txt}: "
                                            prompt += f"{dict_list[i]["content"]}\n"
                                            if dict_list[i]["urls"] and dict_list[i]["elementType"] != 'img' :
                                                
                                                prompt += "Consider also images" ', '.join(dict_list[i]["urls"]) 

                                            if dict_list[i]["styles"]["backgroundImage"] != "none" :
                                                # match = re.search(r'url\("([^"]+)"\)', f"{dict_list[i]["styles"]["backgroundImage"]}")
                                                # if match:
                                                #     extracted_url = match.group(1)
                                                prompt = f"Describe what is in the image: {dict_list[i]["styles"]["backgroundImage"]}"                                           
                                
                                                

                                    print (prompt)

                                elif choice == 'Translate into Italian':
                                    prompt = "Translate into Italian the text: "
                                    count_txt = 0
                                    for item in dict_list:

                                        if (f"{item["elementType"]}" != 'img'):
                                            count_txt +=1
                                            prompt += f"Text {count_txt}: "
                                            prompt += f"{item["content"]}"
                                elif choice == 'Paraphrase':
                                    prompt = "Paraphrase the text:"
                                    count_txt = 0
                                    for i in range(len(dict_list)):
                                        if (dict_list[i]["elementType"] != 'img'):
                                            count_txt += 1
                                            prompt += f"Text {count_txt}: "
                                            prompt += f"{dict_list[i]["content"]}"
                                elif choice == 'Describe the image':
                                    count_img = 0
                                    prompt = "Summarize the description: "
                                    for i in range(len(dict_list)):
                                        if (dict_list[i]["elementType"] == 'img'):
                                            count_img +=1
                                            description = ''
                                            url= ''
                                            url = dict_list[i]["urls"]
                                            client = Groq()
                                            completion = client.chat.completions.create(
                                            model="llama-3.2-11b-vision-preview",
                                                messages=[
                                                    {
                                                        "role": "user",
                                                        "content": [
                                                            {
                                                                "type": "text",
                                                                "text": "What's in this image? "
                                                            },
                                                            {
                                                                "type": "image_url",
                                                                "image_url": {
                                                                    "url": str(''.join(url))
                                                                }
                                                            }
                                                        ]
                                                    },
                                                    {
                                                        "role": "assistant",
                                                        "content": ""
                                                    }
                                                ],
                                                temperature=1,
                                                max_tokens=1024,
                                                top_p=1,
                                                stream=False,
                                                stop=None,
                                            )
                                            description = completion.choices[0].message.content
                                            
                                            prompt += f"Image {count_img}: "
                                            prompt += f"{dict_list[i]["content"]} \n"
                                            prompt += description
                                        if (dict_list[i]["styles"]["backgroundImage"] != 'none'):
                                            match = re.search(r'url\("([^"]+)"\)', dict_list[i]["styles"]["backgroundImage"])

                                            # Extracted URL
                                            if match:
                                                url = match.group(1)
                                            prompt = "Describe what is in the image(s) shortly"  + url
                                    

                                    print (prompt)
                                            
                                            
                                elif choice == 'Add element':
                                        
                                        count_a_press += 1
                                        self.close_application()
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
                                
                                self.show_popup("Result", output)

                            def show_popup(self, title, output):
                                if self.popup_window is None or not self.popup_window.winfo_exists():
                                    self.popup_window = tk.Toplevel(self)
                                    # self.popup_window.title(title)
                                    self.popup_window.attributes("-topmost", True) 
                                    self.popup_window.focus_set()
                                    self.popup_window.minsize(10, 10)  # Sets the minimum window size
                                    self.popup_window.resizable(True, True)  # Allows the window to be resized
                                    self.popup_window.configure(bg="#ffffff")
                                    self.popup_window.focus_set()

                                    frame = tk.Frame(self.popup_window, bg="#f1f1f1", padx=2, pady=2)
                                    frame.pack(fill="both", expand=True)
                                    title_label = tk.Label(
                                        frame,
                                        text=title,
                                        font=("Arial", 11, "bold"),
                                            bg="#0078D7",
                        fg="white",
                        activebackground="#005fa3",
                        relief="raised",
                        
                                            anchor="center",
                                            pady=2,
                                    )
                                    title_label.pack(fill="x", pady=(0, 10))

                                    popup_widget = tk.Text(frame, wrap=tk.WORD,font=("Arial", 10) )
                                    popup_widget.insert('1.0', output)

                                    scroll_bar = tk.Scrollbar(frame, orient='vertical', command=popup_widget.yview)
                                    popup_widget['yscrollcommand'] = scroll_bar.set
                                    scroll_bar.pack(side='right', fill='y')
                                    popup_widget.pack(side='left', fill="both", expand=True)
                                    self.popup_window.update_idletasks()
                                    num_lines = len(popup_widget.get('1.0', tk.END).splitlines())
                                    width = 600
                                    height = max(150, num_lines * 20 + 50)
                                    while True:
                                        for i in range(len(dict_list)):
                                            if 0 < abs(int(dict_list[i]["borderX"])) - 100 < SCREENSIZE[0] - 160:
                                                popup_x = abs(int(dict_list[i]["borderX"])) - 100 + (160 - (abs(int(dict_list[i]["borderX"])) - 100))
                                            elif abs(int(dict_list[i]["borderX"])) - 160 > SCREENSIZE[0] - 160:
                                                popup_x = 700
                                            else:
                                                popup_x = (abs(int(dict_list[i]["borderX"]))) 
                                            if 0 < abs(int(dict_list[i]["borderY"])) - 160 < SCREENSIZE[1] - 160:
                                                popup_y = (abs(int(dict_list[i]["borderY"])) - 160) + (160 - (abs(int(dict_list[i]["borderY"])) - 100))
                                            elif abs(int(dict_list[i]["borderY"])) - 160 > SCREENSIZE[1] - 160:
                                                
                                                popup_y = 700
                                            else:                                                   
                                                popup_y = (abs(int(dict_list[i]["borderY"]))) 
                                        self.popup_window.geometry(f'{width}x{height}+{popup_x + 250}+{popup_y}')
                                        self.popup_window.update_idletasks()
                                        self.popup_window.update_idletasks()
                                        self.popup_window.update()
                                        if popup_widget.get(1.0, tk.END) != '\n':
                                            break
                                        self.popup_window.geometry(f'{width}x{height}')
                                        height += 20
                                    self.popup_window.update_idletasks()

                            def bind_keys(self):
                                self.after(10, self.check_keys)

                            def check_keys(self):
                                
                                self.create_main_window()  # Create the main application window
                                count = 1
                                global count_a_press
                                
                                if keyboard.is_pressed("q") and count == 1 and quit_required == True:
                                    while keyboard.is_pressed('q'):
                                        pass
                                    self.close_application()
                                if keyboard.is_pressed('a'):
                                    self.close_application()  # Close both windows
                                    count_a_press += 1
                                if quit_required:
                                    self.after(10, self.check_keys)  # Check again after 100ms


                            def create_main_window(self):
                                if self.winfo_exists():  # Check if the window is still valid
                                    self.deiconify() 
                                

                            def close_application(self):
                                if self.popup_window and self.popup_window.winfo_exists():
                                    self.popup_window.destroy()  # Close the popup if it's open
                                if self.winfo_exists():
                                    self.destroy()  # Close the main application

                        if __name__ == "__main__":
                            app = Application()
                            app.withdraw()  # Start hidden
                            app.title("Task selection")
                            app.mainloop()
                        
                    quit_required = False
                    if (count_a_press == 0):
                        with open("response.txt", "w") as f:
                            f.write("")
                            
                    
                        
        

                            

                    
                
         
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

# def restart_program():
#     """Restart the current program."""
#     print("Restarting program...")

#     # Get Python executable and script path
#     python_executable = sys.executable
#     script_path = os.path.abspath(__file__)

#     try:
#         # Restart the program
#         subprocess.run([python_executable, script_path], shell=False)
#         sys.exit(0)  # Exit the current instance
#     except Exception as e:
#         print(f"Error restarting the program: {e}")
   





def main():
    
    
    start_server = websockets.serve(eyetracking_running, "localhost", 8080)
    #start_server = websockets.serve(handle_client, "localhost", 8080)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()



if __name__ == "__main__":
    main()





  
