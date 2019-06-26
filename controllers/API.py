import requests
import base64
import json
class API():
    def __init__(self,url):
        self.url = url
        self.token = ""
        self.headers = ""

    def authentication(self,credentials):
        protocol = "Basic"

        httpResponse = requests.post(
            url= self.url + "/rest/auth/1/session",
            json={
                'username': credentials['username'],
                'password': credentials['password'],
            }
        )
        self.token = base64.b64encode((credentials["username"] + ':' + credentials['password']).encode('ascii'))

        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': protocol + ' ' + str(self.token.decode("utf-8"))
        }

        return  httpResponse

    def getIssues(self,data):

    def getToken(self):
        return str(self.token.decode("utf-8"))
