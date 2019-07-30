import requests
import base64
import json
from functools import reduce
class Jira():
    def __init__(self,authorization = None):
        self.url = 'https://jira.novobi.com'
        self.token = ""
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': "Basic" + ' ' + str(authorization)
        }

    ## encode standard auth 1

    def encodeAuthorization(self, credentials):
        res = base64.b64encode((credentials["username"] + ':' + credentials['password']).encode('ascii'))
        return res.decode("utf-8")

    def getToken(self):
        return self.token
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
        #check httresponse
        if httpResponse.status_code == 200:
            self.token = self.encodeAuthorization(credentials)

            self.headers = {
                'Content-Type': 'application/json',
                'Authorization': protocol + ' ' + self.getToken()
            }

        return  httpResponse

    def getAllIssues(self):
        startIdx = 0
        searchRange = 1
        data = []
        date_limit = "2019-07-20"
        for i in range(2):
            httpResponse = requests.post(
                url = self.url + "/rest/api/2/search",
                headers= self.headers,
                json= {
                    "jql": "created >= %s" % (date_limit),
                    "startAt": startIdx,
                    "maxResults": searchRange,
                    "fields": [
                        "project",
                        "status",
                        "worklog",
                        "assignee",
                        "updated",
                        "summary"
                        ]
                    }
                )

            if httpResponse.status_code == 200:
                res = httpResponse.json()["issues"]
                data.extend(res)
                if len(res) < searchRange:
                    break
                else:
                    startIdx += searchRange
                    searchRange = httpResponse.json()["total"] - searchRange

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


    def get_project(self,project_key):
        httpResponse = requests.get(
            url=self.url + "/rest/api/2/project/%s" % (project_key),
            headers=self.headers
        )

        data = []
        if httpResponse.status_code == 200:
            try:
                data = httpResponse.json()
            except Exception as e:
                print(e)
                data = []

        return data

    def add_worklog(self, arg):
        httpResponse = requests.post(
            url=self.url + "/rest/api/2/issue/%s/worklog" %(arg["task_id"]),
            headers=self.headers,
            json={
                "comment": arg["description"],
                "started": arg["date"],
                "timeSpentSeconds": int(arg["unit_amount"]*60*60)
            }
        )

        if httpResponse.status_code == 201:
            return httpResponse.json()
        else:
            return None

    def update_worklog(self, arg):
        data ={}

        if arg.get("description"):
            data["comment"] = arg["description"]

        if arg.get("date"):
            data["started"] = arg["date"]

        if arg.get("unit_amount"):
            data["timeSpentSeconds"] = int(arg["unit_amount"]*60*60)

        httpResponse = requests.put(
            url=self.url + "/rest/api/2/issue/%s/worklog/%s" %(arg["task_id"],arg["worklog_id"]),
            headers=self.headers,
            json=data
        )

        if httpResponse.status_code == 200:
            return httpResponse.json()
        else:
            return None

    def remove_worklog(self,arg):
        httpResponse = requests.delete(
            url=self.url + "/rest/api/2/issue/%s/worklog/%s" % (arg["task_id"], arg["worklog_id"]),
            headers=self.headers
        )

        if httpResponse.status_code == 204:
            return True
        else:
            return False

    def get_user(self, username):
        reponse = requests.get(
            url=self.url + "/rest/api/2/user",
            headers=self.headers,
            params={
                "username": username
            }
        )
        if reponse.status_code == 200:
            return reponse.json()
        else:
            return None
