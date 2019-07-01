import requests
import base64
import json
from functools import reduce
class JiraAPIService():
    def __init__(self,url):
        self.url = url
        self.token = ""
        self.headers = ""


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
        self.token = base64.b64encode((credentials["username"] + ':' + credentials['password']).encode('ascii'))

        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': protocol + ' ' + self.getToken()
        }

        return  httpResponse

    def getAllIssues(self):
<<<<<<< HEAD

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
=======
        searchRange = 50
        startIdx = 0
        endIdx = 50
        data = []
        while(True):
            httpResponse = requests.post(
                url = self.url + "/rest/api/2/search",
                headers= self.headers,
                json = {
                    "jql": "",
                    "startAt": startIdx,
                    "maxResults": endIdx,
                    "fields": [
                        "project",
                        "status",
                        "worklog",
                        "assignee"
                        ]
                    }
                )

            if httpResponse.status_code == 200:
                try:
                    if httpResponse.json()["issues"].len() <= (endIdx - startIdx):
                        break
                    else:
                        data.extend(httpResponse.json()["issues"])
                        startIdx = endIdx
                        endIdx += searchRange

                except Exception as e:
                    print(e)
                    data = []
                    break
>>>>>>> abc

        return data




    def getToken(self):
        return str(self.token.decode("utf-8"))
