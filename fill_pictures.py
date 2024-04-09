from requests import Response
import requests
import settings
import random
import string
import sys


print("Please remove any proxies to speed up this process.\n")


try: amount: int = int(sys.argv[1]) if len(sys.argv) >= 2 else settings.DEFAULT_PICTURE_FILLER_COUNT
except: amount: int = settings.DEFAULT_PICTURE_FILLER_COUNT


for i in range(amount):

    print(f"Generating Pictures: {i + 1}/{amount}")

    response: Response = requests.get(
        url="https://thispersondoesnotexist.com",
        headers={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
    )

    file_name = f"./pictures/{str().join(random.choices(string.ascii_letters + string.digits, k=30))}.jpg"

    with open(file_name, "wb") as file: file.write(response.content)
