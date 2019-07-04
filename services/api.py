import requests
import base64
import json
from functools import reduce
class Jira():
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

    def getAllIssues(self):
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
                        "assignee",
                        "updated"
                        ]
                    }
                )

            if httpResponse.status_code == 200:
                try:
                    res = httpResponse.json()["issues"]
                    data.extend(res)
                    if len(res) <= (endIdx - startIdx):
                        break
                    else:
                        startIdx = endIdx
                        endIdx += searchRange

                except Exception as e:
                    print(e)
                    data = []
                    break

        return data

    def getAllWorklogByIssue(self, issueID):
        httpResponse = requests.get(
            url=self.url + "/rest/api/2/issue/%s/worklog/" % (issueID),
            headers=self.headers
        )
        try:
            data = httpResponse.json()["worklogs"]
        except Exception as e:
            print(e)
            data = []

        return data

    def getToken(self):
        return str(self.token.decode("utf-8"))
