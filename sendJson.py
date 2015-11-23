import json
import requests
import pprint
import sys
import uuid

class sendJson(object):
    """docstring for sendJson"""
    def __init__(self, text = ""):
        super(sendJson, self).__init__()
        self.text = text
        self.url  = 'http://conexa-demo.azurewebsites.net/api/chat'
        self.idd = str(uuid.uuid1(0x222222222222))
        self.headers = {'Content-type': 'application/json'}

    def sendText(self, texto):
        data2 = {"Id":self.idd, "Name" : "pp", "Pic" : "nenene", "Text" : texto}
        data2_json = json.dumps(data2)


        # Verschicken
        response = requests.post(self.url, data=data2_json, headers=self.headers)

    def deleteAll(self):
        requests.delete(self.url)

if __name__ == '__main__':
    sender = sendJson()
    # sender.deleteAll()
    sender.sendText("main unit test")
#print response

# Liste holen und 2ten Datensatz anzeigen

# req = requests.get(url)
# print req
# print req.json()
# for item in req:
#     print item["Text"]

# Liste online loeschen

# requests.delete(url)