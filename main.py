import requests, json, datetime
import settings

def login(username, password, url):
    response = requests.post(
        url,
        data={
            "username": username,
            "password": password
        }
    )
    
    if response.ok:
        data = json.loads(response.content.decode("utf-8"))
        return data["token"]
    else:
        return None

def get_due_enrolment(token):
    today = datetime.date.today() - datetime.timedelta(days=30)
    
    response = requests.get(
        settings.BACKEND_URL + f"/enrollments/query?date={today.__str__()}",
        headers={
            "Authorization": f"Token {token}" 
        }
    )
    
    if response.ok:    
        data = json.loads(response.content.decode("utf-8"))
        return data
    else:
        return None

def main():
    AUTHTOKEN = login(
        settings.DJANGO_ADMIN_USERNAME,
        settings.DJANGO_ADMIN_PASSWORD,
        settings.BACKEND_URL + "/auth/login"
    )
    
    print(AUTHTOKEN)
    
    print(
        json.dumps(
            get_due_enrolment(AUTHTOKEN),
            indent=4
        )
    )

if __name__ == "__main__":
    main()