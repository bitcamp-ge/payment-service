import requests, json, datetime, utils
import settings

def exit(code):
    if settings.QUIT_ON_ERROR:
        utils.log("[!] Exiting due to error")
        quit(code)
    else:
        utils.log("[!] Error occured - continuing... (QUIT_ON_ERROR=False)")

def login(username, password, url):
    utils.log(f"[.] Authenticating ({username}:{password}) to the backend...")
    
    try:
        response = requests.post(
            url,
            data={
                "username": username,
                "password": password
            }
        )
    except requests.exceptions.RequestException as error:
        utils.log(f"[!] An error occurred while authenticating: {error}")
        exit(1)
    
    if response.ok:
        data = json.loads(response.content.decode("utf-8"))
        utils.log(f"[+] Authentication successful ({data['token']})")
        return data["token"]
    else:
        utils.log(f"[!] Authentication failed with status code: {response.status_code}")
        exit(1)

# get_due_enrolment(AUTHTOKEN)
def get_due_enrolment(token):
    utils.log(f"[.] Querying enrolments...")
    
    today = datetime.date.today() - datetime.timedelta(days=30)
    
    try:
        response = requests.get(
            settings.BACKEND_URL + f"/enrollments/query?date={today.__str__()}",
            headers={
                "Authorization": f"Token {token}" 
            }
        )
    except requests.exceptions.RequestException as error:
        utils.log(f"[!] An error occurred while querying enrolments: {error}")
        exit(1)
    
    if response.ok:
        data = json.loads(response.content.decode("utf-8"))
        utils.log(f"[+] Enrolments retrieved {len(data)} records")
        return data
    else:
        utils.log(f"[!] Failed to retrieve enrolments with status code: {response.status_code}")
        exit(1)

# filter_enrolment_data(get_due_enrolment(AUTHTOKEN))
def filter_enrolment_data(data):
    utils.log(f"[.] Filtering enrolment data of {len(data)} records...")
    
    try:
        return [
            {
                "id": item["id"],
                "user": item["user"],
                "service_id": item["service_id"],
                "program_id": item["program_id"],
                "start_payment": item["start_payment"],
                "last_payment": item["last_payment"],
                "overdue": (datetime.date.today() - datetime.datetime.strptime(item["last_payment"].split("T")[0], "%Y-%m-%d").date()).days,
                "payments": item["payments"],
                "status": item["status"]
            }
            for item in data
        ]
    except Exception as error:
        utils.log(f"[!] An error occurred while filtering enrolment data: {error}")
        exit(1)
    
# update_last_payment(AUTHTOKEN, filtered_data[0]["id"], datetime.date(2024, 2, 2).__str__())
def update_last_payment(token, enrolment_id, new_date):
    utils.log(f"[.] Updating last payment date of enrolment ({enrolment_id}) to ({new_date})...")
    
    try:
        response = requests.put(
            settings.BACKEND_URL + f"/enrollments/update-last-payment",
            headers={
                "Authorization": f"Token {token}"
            },
            data={
                "id": enrolment_id,
                "last_payment": new_date
            }
        )
    except requests.exceptions.RequestException as error:
        utils.log(f"[!] An error occurred while updating last payment: {error}")
        exit(1)

    if response.ok:
        utils.log(f"[+] Last payment date updated successfully")
        data = json.loads(response.content.decode("utf-8"))
        return data
    else:
        utils.log(f"[!] Failed to update last payment with status code: {response.status_code}")
        exit(1)

def main():
    AUTHTOKEN = login(
        settings.DJANGO_ADMIN_USERNAME,
        settings.DJANGO_ADMIN_PASSWORD,
        settings.BACKEND_URL + "/auth/login"
    )
    
    data = get_due_enrolment(AUTHTOKEN)
    filtered_data = filter_enrolment_data(data)
    
    print(
        json.dumps(filtered_data, indent=4)
    )

if __name__ == "__main__":
    utils.log("[+] Script started")
    main()