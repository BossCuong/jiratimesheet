import requests
import base64
import json
from functools import reduce
class JiraAPIService():
    def __init__(self,url):
        self.url = url
        self.token = ""
        self.headers = ""

    ## encode standard auth 1

    def encodeAuthorization(self, credentials):
        return base64.b64encode((credentials["username"] + ':' + credentials['password']).encode('ascii'))
    ## Write get,set method

    def authentication(self,credentials):
        protocol = "Basic"

        httpResponse = requests.post(
            url= self.url + "/rest/auth/1/session",
            json={
                'username': credentials['username'],
                'password': credentials['password'],
            }
        )
        self.token = self.encodeAuthorization(credentials)

        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': protocol + ' ' + self.getToken()
        }

        return  httpResponse


    # def getAllProject(self):
    #     httpResponse = requests.get(
    #         url = self.url + "/rest/api/2/project",
    #         headers = self.headers
    #     )
    #     try:
    #         projects = httpResponse.json()
    #     except Exception as e:
    #         print(e)
    #
    #     return projects

    def getAllIssues(self):

        httpResponse = requests.post(
            url = self.url + "/rest/api/2/search",
            headers= self.headers,
            json ={
                "jql": "",
                "startAt": 0,
                "maxResults": 50,
                "fields": [
                    "project",
			        "status",
			        "worklog",
			        "assignee"
                    ]
                }
            )

        try:
            data = httpResponse.json()["issues"]
        except Exception as e:
            print(e)
            data = None

        return data

    def getToken(self):
        return str(self.token.decode("utf-8"))
