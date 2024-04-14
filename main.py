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
        
def perform_transaction(enrolment, payments, user):
    service = enrolment["service"]
    last_payment = payments[-1]
    
    if service["price"] <= 0.00:
        # Its free!
        return False
    
    payload = {
        "source": "Card",
        "amount": service["price"].__str__(),
        "currency": "GEL",
        "language": "KA",
        "token": last_payment["token"].__str__(),
        "hooks": {
            "webhookGateway": "https://platform.bitcamp.ge/payments/payze_hook",
            "successRedirectGateway": f"https://platform.bitcamp.ge/enrollments/{enrolment['id']}/check-payze-subscription-status",
            "errorRedirectGateway": f"https://platform.bitcamp.ge/enrollments/{enrolment['id']}/check-payze-subscription-status"
        },
        "metadata": {
            "extraAttributes": [
                { "key": "service", "value": service["title"] },
                { "key": "email", "value": user["email"] }
            ]
        }
    }
    
    headers = {
        "Accept": "application/*+json",
        "Content-Type": "application/json",
        "Authorization": settings.PAYZE_API_KEY,
        "User-Agent": "bitcampayservice/v1"
    }
    
    response = requests.put("https://payze.io/v2/api/payment", json=payload, headers=headers)
    
    if response.ok:
        payze_data = response.json()
        
        payment = {
            "enrollment": enrolment,
            "amount": payze_data["data"]["payment"]["amount"],
            "status": payze_data["data"]["payment"]["status"],
            "payze_transactionId": payze_data["data"]["payment"]["transactionId"],
            "payze_paymentId": payze_data["data"]["payment"]["id"],
            "cardMask": payze_data["data"]["payment"]["cardPayment"]["cardMask"] if payze_data["data"]["payment"]["cardPayment"]["cardMask"] is not None else "",
            "token": payze_data["data"]["payment"]["cardPayment"]["token"],
        }
        
        return payment        

def take_action(token, enrolment):
    overdue_by = enrolment["overdue"] - 30
    
    if enrolment["status"] == "Active":
        if overdue_by > 5:
            print(f"More than 35 days have passed ({overdue_by} days)")
            ... # More than 35 days have passed
            # He cant keep getting away with this!

        data = json.loads(requests.get(
            settings.BACKEND_URL + f"/enrollments/get-enrollment-data?id={enrolment['id']}",
            headers={
                "Authorization": f"Token {token}"
            }
        ).content)
        
        perform_transaction(data["enrolment"], data["enrolment"]["payments"], data["user"])

def main():
    AUTHTOKEN = login(
        settings.DJANGO_ADMIN_USERNAME,
        settings.DJANGO_ADMIN_PASSWORD,
        settings.BACKEND_URL + "/auth/login"
    )
    
    data = get_due_enrolment(AUTHTOKEN)
    filtered_data = filter_enrolment_data(data)
    
    [take_action(AUTHTOKEN, enrolment) for enrolment in filtered_data]

if __name__ == "__main__":
    utils.log("[+] Script started")
    main()
