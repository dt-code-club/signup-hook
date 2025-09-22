import os
import requests
import json


def findstudentbyrequest(firstname, lastname, snum):
    url = os.environ.get("teams_url")
    payload = "{\r\n    \"keyword\": \""+(firstname + " " + lastname)+"\"\r\n}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:142.0) Gecko/20100101 Firefox/142.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Content-Type': 'application/json;charset=UTF-8',
        'Referer': 'https://teams.microsoft.com/v2/worker/precompiled-web-worker-249ea70c5c0e8257.js',
        'x-client-ui-language': 'en-us',
        'x-ms-client-caller': 'search-thread-members-worker-resolver:searchThreadMembers',
        'x-ms-client-type': 'cdlworker',
        'x-ms-client-version': '1415/25073117413',
        'x-ms-migration': 'True',
        'x-ms-test-user': 'False',
        'Origin': 'https://teams.microsoft.com',
        'Sec-GPC': '1',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'authorization': os.environ.get("teams_auth"),
        'x-ms-object-id': '',
        'x-ms-request-id': '',
        'Connection': 'keep-alive',
        'Priority': 'u=4',
        'TE': 'trailers'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    searchresults = list(filter(
        lambda x: x["userPrincipalName"].replace("@learn.vsb.bc.ca", "") == str(snum), response.json()))
    print(searchresults)
    return searchresults


def findstudent(firstname, lastname, snum):
    students_env = os.environ.get("students")
    if not students_env:
        print("No students found in environment variable.")
        return []
    # Unescape quotes
    students_json = students_env.replace('\\"', '"')
    try:
        students_obj = json.loads(students_json)
        students_list = students_obj.get("students", [])
    except Exception as e:
        print(f"Error parsing students JSON: {e}")
        return []
    searchresults = list(filter(
        lambda x: x["userPrincipalName"].replace("@learn.vsb.bc.ca", "") == str(snum), students_list))
    print(searchresults)
    return searchresults


if __name__ == "__main__":
    findstudent(input("First name: "), input(
        "Last name: "), input("Student number: "))
