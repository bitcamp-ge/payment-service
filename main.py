import requests, json, datetime, utils
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

def filter_enrolment_data(data):
    return [
        {
            "id": item["id"],
            "user": item["user"],
            "service_id": item["service_id"],
            "program_id": item["program_id"],
            "start_payment": item["start_payment"],
            "last_payment": item["last_payment"],
            "payments": item["payments"],
            "status": item["status"]
        }
        for item in data
    ]

def main():
    AUTHTOKEN = login(
        settings.DJANGO_ADMIN_USERNAME,
        settings.DJANGO_ADMIN_PASSWORD,
        settings.BACKEND_URL + "/auth/login"
    )
    
    utils.log("[+] Authentication token:", AUTHTOKEN)
    
    data = get_due_enrolment(AUTHTOKEN)
    filtered_data = filter_enrolment_data(data)
    
    print(
        json.dumps(filtered_data, indent=4)
    )

if __name__ == "__main__":
    main()