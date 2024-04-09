from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from requests import Session
from time import sleep, time
import random
from dataclasses import dataclass
from json import JSONDecodeError
import json
from lib.Color import Color
import settings
from lib import (
    email_generator,
    name_generator,
    otp_generator,
    password_generator,
    username_generator,
    session_id_extractor
)


if __name__ == "__main__": raise Exception("To create an account, please run \"main.py\".")


def initiate(session: Session, user_agent: str) -> None:
    """
    Returns MID & DeviceID, required for further actions.
    """

    response: str = session.get(
        url="https://www.instagram.com/accounts/emailsignup/",
        headers={
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9",
            "sec-ch-ua": user_agent,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1"
        },
    ).text

    # Extract Mid
    rest_data: str = response[response.index("\"machine_id\":\"") + 14:]
    mid: str = rest_data[:rest_data.index("\"")]

    # Remove First Occurence Of 'device_id'
    response = response.replace("\"device_id\":\"", "", response.count("\"device_id\":\"") - 1)

    # Extract Device ID
    rest_data: str = response[response.index("\"device_id\":\"") + 13:]
    device_id: str = rest_data[:rest_data.index("\"")]

    # Return Data
    return mid, device_id


def create(proxy: dict[str, str] = None):
    """
    Creates an account and returns its credentials.
    """

    session: Session = None

    user_agent: str = ""
    email_regenerated, max_email_collisions = 0, 3

    while True:
        user_agent: str = UserAgent(software_names=[SoftwareName.CHROME.value, SoftwareName.FIREFOX.value], operating_systems=[OperatingSystem.WINDOWS.value]).get_random_user_agent()
        
        session: Session = Session()
        session.proxies = proxy

        mid, web_device_id = initiate(session, user_agent)

        session.cookies.set("mid", mid, domain=".instagram.com")

        preferred_color_scheme: str = random.choice(["light", "dark"])
        
        full_name: str = name_generator.generate()
        username: str = username_generator.generate(full_name)
        password_raw, password = password_generator.generate()
        email: str = email_generator.generate()

        print(f"{Color.BLUE}User Agent: {Color.END}{user_agent}")

        print(f"{Color.GREEN}\nAttempting dryrun...{Color.END}")
        csrf = session.cookies.get("csrftoken")

        # Attempt: For dry run
        attempt = session.post(
            url="https://www.instagram.com/api/v1/web/accounts/web_create_ajax/attempt/",
            headers={
                "user-agent": user_agent,
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.9",
                #"cache-control": "no-cache",
                "content-type": "application/x-www-form-urlencoded",
                "pragma": "no-cache",
                #"sec-ch-prefers-color-scheme": preferred_color_scheme,
                #"sec-ch-ua": user_agent,
                #"sec-ch-ua-full-version-list": user_agent,
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-model": "\"\"",
                #"sec-ch-ua-platform": "\"Windows\"",
                #"sec-ch-ua-platform-version": "15.0.0",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "x-csrftoken": session.cookies.get("csrftoken"),
                "x-ig-app-id": "936619743392459",
                "x-ig-www-claim": "0",
                "x-requested-with": "XMLHttpRequest",
                "x-web-device-id": web_device_id,
                "Referer": "https://www.instagram.com/accounts/emailsignup/",
                "Referrer-Policy": "strict-origin-when-cross-origin"
            },
            data={
                "enc_password": password,
                "email": email,
                "first_name": full_name,
                "username": username,
                "client_id": mid,
                "seamless_login_enabled": 1,
                "opt_into_one_tap": False
            },
            cookies={
                "csrftoken": csrf,
                "mid":mid,
                "ig_did": web_device_id
            }
        )
        
        if attempt.json()["status"] != "ok" or attempt.json()["dryrun_passed"] == False:

            if not "email" in attempt.json().get("errors", {}).keys():
                print(attempt.json())
                raise Exception("Dryrun not passed. Check proxies and account details.")
            
            if email_regenerated < max_email_collisions:
                email_regenerated += 1
                print(f"{Color.BLUE}Email already used. Generating another one...{Color.END}")
                continue

            else:
                print()
                raise Exception(f"Email collided {max_email_collisions} times. Your duck addresses for this email are finished. Sign up for another duck account and use it's token.")

        print(f"{Color.BLUE}Email: {Color.END}{email}\n")
        break

    otp_initial_send_timestamp: float = time()
    
    # Send verification email
    print(f"\n" if email_regenerated != 0 else "" + f"{Color.BLUE}Waiting {settings.STEP_GAP} seconds...{Color.END}\n")
    sleep(settings.STEP_GAP)

    print(f"{Color.GREEN}Sending verification email...{Color.END}")

    send_otp = session.post(
        url="https://www.instagram.com/api/v1/accounts/send_verify_email/",
        headers={
            "user-agent": user_agent,
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded",
            "sec-ch-prefers-color-scheme": preferred_color_scheme,
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-csrftoken": csrf,
            "x-ig-app-id": "936619743392459",
            "x-ig-www-claim": "0",
            "x-mid": mid,
            "x-requested-with": "XMLHttpRequest",
            "x-web-device-id": web_device_id,
            "Referer": "https://www.instagram.com/accounts/signup/email/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        },
        data={
            "device_id": mid,
            "email": email
        },
        cookies={
            "csrftoken": csrf,
            "mid":mid,
            "ig_did": web_device_id
        }
    )
    if send_otp.json().get("email_sent", False) is False or send_otp.json()["status"] != "ok":
        print(send_otp.json())
        raise Exception("Verification email not sent.")
    

    # Verify OTP
    print(f"\n{Color.BLUE}Waiting {settings.STEP_GAP} seconds...{Color.END}")
    sleep(settings.STEP_GAP)

    while True:
        otp=""
        otp = otp_generator.generate(otp_initial_send_timestamp)

        verify_otp = session.post(
            url="https://www.instagram.com/api/v1/accounts/check_confirmation_code/",
            headers={
                "user-agent": user_agent,
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.9",
                #"cache-control": "no-cache",
                "content-type": "application/x-www-form-urlencoded",
                "pragma": "no-cache",
                #"sec-ch-prefers-color-scheme": preferred_color_scheme,
                #"sec-ch-ua": user_agent,
                #"sec-ch-ua-full-version-list": user_agent,
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-model": "\"\"",
                #"sec-ch-ua-platform": "\"Windows\"",
                #"sec-ch-ua-platform-version": "15.0.0",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "x-csrftoken": csrf,
                "x-ig-app-id": "936619743392459",
                "x-ig-www-claim": "0",
                "x-requested-with": "XMLHttpRequest",
                "x-web-device-id": web_device_id,
                "Referer": "https://www.instagram.com/accounts/emailsignup/",
                "Referrer-Policy": "strict-origin-when-cross-origin"
            },
            data={
                "code": otp,
                "device_id": mid,
                "email": email
            },
            cookies={
            "csrftoken": csrf,
            "mid":mid,
            "ig_did": web_device_id
            }
        )

        if verify_otp.json().get("signup_code") is None or verify_otp.json()["status"] != "ok":
            print({Color.RED})
            print(verify_otp.json())
            print(f"Didn't get signup code. Maybe the OTP is incorrect.{Color.END}\n")
            continue

        break

    # Finally, create ajax request for complete account creation
    print(f"{Color.BLUE}Waiting {settings.STEP_GAP} seconds...{Color.END}\n")
    sleep(settings.STEP_GAP)
        
    print(f"{Color.GREEN}Finishing up...{Color.END}")
    signup_code = verify_otp.json()["signup_code"]
    
    final_data_pass: dict = {
        "enc_password": password,
        "day": random.randint(1, 28),
        "email": email,
        "first_name": full_name,
        "month": random.randint(1, 12),
        "username": username,
        "year": random.randint(1970, 2004),
        "client_id": mid,
        "seamless_login_enabled": 1,
        "tos_version": "eu",
        "force_sign_up_code": signup_code
    }

    ajax = session.post(
        url="https://www.instagram.com/api/v1/web/accounts/web_create_ajax/",
        headers={
            "user-agent": user_agent,
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "no-cache",
            "content-type": "application/x-www-form-urlencoded",
            "pragma": "no-cache",
           # "sec-ch-prefers-color-scheme": preferred_color_scheme,
           # "sec-ch-ua": user_agent,
           # "sec-ch-ua-full-version-list": user_agent,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-model": "\"\"",
           # "sec-ch-ua-platform": "\"Windows\"",
            #"sec-ch-ua-platform-version": "15.0.0",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-csrftoken": csrf,
            "x-ig-app-id": "936619743392459",
            "x-ig-www-claim": "0",
            "x-requested-with": "XMLHttpRequest",
            "x-web-device-id": web_device_id,
            "Referer": "https://www.instagram.com/accounts/emailsignup/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        },
        allow_redirects=False,
        data=final_data_pass,
        cookies={
            "csrftoken": csrf,
            "mid":mid,
            "ig_did": web_device_id
        },
        timeout=None
    )

    try: sessionid = session_id_extractor.extract(ajax.headers.get("set-cookie"))
    except: sessionid = ""

    try:
        ## Debugging Purposes:
        # with open("last-ajax-response-headers.json", "w", encoding="utf-8") as file:
        #     respose_headers: dict = {}

        #     for heading in ajax.headers.keys():
        #         respose_headers[heading] = ajax.headers.get(heading)

        #     file.write(json.dumps(respose_headers))
        
        ## Debugging Purposes:
        # with open("last-ajax-response-content.html", "w", encoding="utf-8") as file:
        #     file.write(ajax.text)

        # if ajax.json()["status"] != "ok" or ajax.json()["account_created"] == False:
        #     print(ajax.json())
        #     print("\n")
        #     raise Exception("Unable to create final account. Response has been printed above.")
        
        # Account created.
        print(f"{Color.GREEN}Account created.{Color.END}")
        
        return Account(
            email=email,
            password=password_raw,
            username=username,
            full_name=full_name,
            sessionid=sessionid,
            user_agent=user_agent
        )
    
    except JSONDecodeError:
        print(f"{Color.GREEN}Account created, but couldn't retrieve session_id. Status: {ajax.status_code}{Color.END}")
        
        return Account(
            email=email,
            password=password_raw,
            username=username,
            full_name=full_name,
            sessionid=sessionid,
            doubt=True,
            user_agent=user_agent
        )


@dataclass(frozen=True)
class Account:
    
    email: str
    password: str
    username: str
    full_name: str
    sessionid: str
    user_agent: str
    doubt: bool = False
