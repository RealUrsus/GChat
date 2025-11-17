import sys, hmac, json, time, hashlib, base64, binascii, requests, urllib3
import urllib.parse
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

REQUEST_FILE = "data.json"
CHAT_FILE = "chat.dat"

def printData(r, *args, **kwargs):
    print(">>", r.url)
    print(">>", r.text)

# /genesys/2/chat/{serviceName}/{chatId}/command
class GmsApi:
    def __init__(self, request_file):        
        try:
            with open(request_file) as json_file:
                self.req = json.load(json_file) 
        except Exception as e:
            print(e)
            sys.exit(1)

        self.gms_dict = {}

    def commit(self, output:str = None) -> json:
        ''' send request via the wire '''
        try:
            # https://requests.readthedocs.io/en/master/api/
            r = requests.request(**self.req)
            
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)
        try:
            if output:
                print("(+) " + output)

            if r.ok and r.content != "Forbidden":                
                json_data = r.json()
                if "statusCode" in json_data:
                    if json_data["statusCode"] != 0:
                        print("(-) commit json error", json_data["errors"])
                        #sys.exit(0)        
                return json_data
            print ('(!) WAF: ', r.content)
            return None

        except ValueError as e:
            print("(-) commit except error: ", e)            
            sys.exit(1)
        

    def create(self, delay: int):
        # Give some time to the Agent
        # time.sleep(delay)

        #json_data = self.commit("Got Chat ID")
        print("(*) Chat started at: ", datetime.now().strftime("%H:%M:%S:%f")[:-3])        

        try:
            r = requests.request(**self.req, hooks={'response': printData})
            
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)

        print("(+) Got Chat ID at: ", datetime.now().strftime("%H:%M:%S:%f")[:-3])
        print(r)

        if r.status_code == 200 and r.content != "Forbidden":                
            json_data = r.json()
            if "statusCode" in json_data:
                if json_data["statusCode"] != 0:
                    print("(-) JSON error", json_data["errors"])
                    sys.exit(0)        

        self.gms_dict["chatId"] = json_data["chatId"]
        self.gms_dict["secureKey"] = json_data["secureKey"]
        self.gms_dict["userId"] = json_data["userId"]
        self.gms_dict["alias"] = json_data["alias"]
        self.gms_dict["url"] = self.req["url"] + json_data["chatId"] + "/"
        self.gms_dict["transcriptPosition"] = json_data["nextPosition"]
        
    def refresh(self, delay: int) -> json:
        time.sleep(delay)
        # Clean DATA
        self.req["data"].clear()
        # Form a new DATA
        self.req["data"]["alias"] = self.gms_dict["alias"]
        self.req["data"]["secureKey"] = self.gms_dict["secureKey"]
        self.req["data"]["userId"] = self.gms_dict["userId"]
        self.req["data"]["message"] = ""
        self.req["data"]["transcriptPosition"] = self.gms_dict["transcriptPosition"]
        self.req["url"] = self.gms_dict["url"] + "refresh"

        json_data = self.commit("Refresh request with transcriptPosition = " + str(self.gms_dict["transcriptPosition"]) + " has been sent")
        
        if isinstance(json_data, dict):
            if "nextPosition" in json_data:
                self.gms_dict["transcriptPosition"] = json_data["nextPosition"]
            
                if len(json_data["messages"]) != 0:            
                    return json_data["messages"]
        
        return None

    def send(self, message: str):
        self.req["data"].clear()
        self.req["data"]["alias"] = self.gms_dict["alias"]
        self.req["data"]["secureKey"] = self.gms_dict["secureKey"]
        self.req["data"]["userId"] = self.gms_dict["userId"]
        self.req["data"]["message"] = message
        self.req["data"]["transcriptPosition"] = self.gms_dict["transcriptPosition"]
        self.req["url"] = self.gms_dict["url"] + "send"  
        
        json_data = self.commit("Send Message -> " + message)
        if isinstance(json_data, dict):
            if "nextPosition" in json_data:
                self.gms_dict["transcriptPosition"] = json_data["nextPosition"]

    def disconnect(self) -> None:
        self.req["data"].clear()
        self.req["data"]["alias"] = self.gms_dict["alias"]
        self.req["data"]["secureKey"] = self.gms_dict["secureKey"]
        self.req["data"]["userId"] = self.gms_dict["userId"]
        self.req["data"]["message"] = ""
        self.req["data"]["transcriptPosition"] = self.gms_dict["transcriptPosition"]
        self.req["url"] = self.gms_dict["url"] + "disconnect"  

        try:        
            requests.request(**self.req)            
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)
            
        print ("(+) Disconnect")

def get_message(reply: json):
    message = []

    for item in reply:
        if item["type"] == "Message":
            if item["text"] == "QUIT":
                print("(-) Got exit signal")
                return None

            print("(+) Message index = " + str(item["index"]) + " -> " + item["text"])
            message.append(item)

        elif item['type'] == "PushUrl":
            print("(+) PushUrl index = " + str(item["index"]) + " -> " + item["text"])
            message.append(item)
            
        elif item["type"] == "ParticipantJoined":
            print("(+) ParticipantJoined")
        
        elif item["type"] == "ParticipantLeft":
            print("(-) Got ParticipantLeft")
            return None         
        
        elif item["type"] == "TypingStarted":
            pass

        elif item["type"] == "TypingStopped":
            pass

        elif item["type"] == "External":
            pass            
                
    return message

def main():    
    gms = GmsApi(REQUEST_FILE)
    gms.create(5)
    gms.refresh(5)
    gms.send("Hello from Chatbot ¯\\_(ツ)_/¯ !!!")

    '''
    while True:
        reply = gms.refresh(1)

        # Nothing to post back
        if reply == None:
            continue

        message = get_message(reply)

        # Exit from the loop
        if message == None:
            break
        
        for item in message:
            gms.send("You posted: " + item["text"])
    '''
    gms.refresh(20)
    try:
        with open(CHAT_FILE, "r", encoding="utf8") as handler:
            for line in handler:
                if line not in ['\n', '\r\n', '\t', '\v']:
                    print("(>) Strip Line from Dict: ", line.strip())                    
                    gms.refresh(30)
                    gms.send(line.strip())
                    #gms.send(line.strip(urllib.parse.quote(line, safe='')))

    except Exception as e:
        print("Disctionary Error:", e)
        sys.exit(1)

    gms.disconnect()

'''
    print(r.text)
    print(json_data['messages'][0]['utcTime'])
    print(json.dumps(json_data, indent=4, sort_keys=True))
'''

if __name__ == '__main__':
    main()
