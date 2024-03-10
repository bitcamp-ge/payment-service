import requests, json, datetime
import settings


def login(username, password, url):
    try:
        response = requests.post(
            url,
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        
        data = response.json()
        
        return data["token"]
    except requests.RequestException as e:
        print(f"Login error: {e}")
        return None


def get_due_enrolment(token):
    
    today = datetime.date.today() - datetime.timedelta(days=30)
    
    try:
        response = requests.get(
            f"{settings.BACKEND_URL}/enrollments/query?date={today.isoformat()}",
            headers={"Authorization": f"Token {token}"}
        )
        
        response.raise_for_status()
        
        return response.json()
    
    except requests.RequestException as e:
        print(f"Error fetching due enrolment: {e}")
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