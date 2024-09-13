# import time
import requests
import config
import json


def check_is_known(i, users):
    return i in users.keys()


class Bot:
    def __init__(self, bot_id, token):
        self.id = bot_id
        self.token = token
        self.run = True
        f = open("users.txt")
        '''
        # Structure for creating log files:
        logs = open(f'logs_for_{time.localtime().tm_year}--{time.localtime().tm_yday//30+1}--{time.localtime().tm_mday}-'
                    f'-{time.localtime().tm_hour}.txt', 'a')  
        # '''

        # # Get information about users from save file
        # self.users = {}
        # self.requests = {}
        # self.num_req = 1
        # string = f.readline()
        # while string:
        #     usid = string[:-1]
        #     string = f.readline()
        #     name = string[:-1]
        #     string = f.readline()
        #     access = string[:-1]
        #     string = f.readline()
        #     activity = string[:-1]
        #     string = f.readline()
        #     tag = string[:-1]
        #     string = f.readline()
        #     # if activity == 'breaking_act':
        #     #     activity = '0'
        #     self.users[usid] = [name, access, activity, tag]
        # f.close()

        # # Get information about chats
        # f = open('chats.txt')
        # self.chats = {}
        # string = f.readline()
        # while string:
        #     inp = string.split()
        #     string = f.readline()
        #     adrs = list(string.split())[::2]
        #     lang = list(string.split())[1::2]
        #     j = 0
        #     for i in inp:
        #         self.chats[i] = [adrs[j], lang[j]]
        #         j += 1
        #     string = f.readline()
        # f.close()

    # Low-level function: send request to GreenAPI with some settings
    def req(self, meth, data, head, type, *id):
        try:
            if type != "DELETE":
                url = "https://api.greenapi.com/waInstance{idInst}/{method}/{apiToken}".format(idInst=self.id,
                                                                                               apiToken=self.token,
                                                                                               method=meth)
                response = requests.request(type, url, headers=head, data=data).text.encode('utf8')
            else:
                url = "https://api.greenapi.com/waInstance{idInst}/deleteNotification/{apiToken}/{receipt}".format(
                    idInst=self.id, apiToken=self.token, receipt=id[0])
                response = requests.request("DELETE", url, headers=head, data=data).text.encode('utf8')
                print(response, id[0])
        except:
            time.sleep(5)
            response = b'\xff\xfen\x00u\x00l\x00l\x00'
        return response

    # Function to clear webhooks(notifications) queue
    def clear_queue(self):
        print(self.req("reboot", {}, {}, "GET"))
        time.sleep(5)
        try:
            i = 1
            while True:
                print(self.req('', {}, {}, "DELETE", i))
                i += 1
        except:
            pass

    # Send one messege to chat with id = r_id and message_text = text
    def send_message(self, r_id, text):
        ans = ''
        for i in text:
            st = str(hex(ord(i)))[2:]
            ans += "\\u" + "0" * (4 - len(st)) + st
        headers = {
            'Content-Type': 'application/json'
        }
        payload = "{\r\n\t\"chatId\": \"" + r_id + "\",\r\n\t\"message\": \"" + ans + "\"\r\n}"
        message_id = self.req("sendMessage", payload, headers, "POST")
        return message_id

    # Forward one messege from chat with id = source, to chat with id = r_id and message_id = id
    def forward(self, r_id, id, source):
        headers = {
            'Content-Type': 'application/json'
        }
        payload = "{\r\n\t\"chatId\": \"" + r_id + "\",\r\n\t\"chatIdFrom\": \"" + source + "\",\r\n\t\"messages\": [\"" + id + "\"]\r\n}"
        message_ids = self.req("forwardMessages", payload, headers, "POST")
        return message_ids

    # Function receives last webhook(notification) from GreenAPI, transforms it into dictionary and returns as result
    def get_news(self):
        payload = {}
        headers = {}
        news = self.req("receiveNotification", payload, headers, "GET")
        try:
            info = json.loads(news)
        except:
            time.sleep(6)
            info = 0
        if info:
            return info
        else:
            return 0

    # Send one messege to multiple chats with ids = recs and message_text = txt
    def multi_send(self, recs, txt):
        for i in recs.keys():
            self.send_message(recs[i][0], txt)
    
    # Forward one messege from one chat with id = source, to multiple chats with chat_ids = recs and message_id = id
    def multi_forward(self, recs, id, source):
        for i in recs.keys():
            self.forward(recs[i][0], id, source)

    def loop(self):
        '''
        Main loop of Chatbot. All algorithms and behavior must be written here
        '''


helper = Bot(config.idInstance, config.ApiTokenInstance)
helper.loop()
