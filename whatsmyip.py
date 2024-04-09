import requests
import settings
from lib.Color import Color


# Logging
if settings.DEFAULT_PROXY_URL != "": print(f"{Color.BLUE}Using proxy: {settings.DEFAULT_PROXY_URL}{Color.END}")
else: print(f"{Color.RED}Not using any proxies.{Color.END}")

# Get IP Address
address: str = requests.get(
    url="https://api.ipify.org",
    proxies={
        "http": settings.DEFAULT_PROXY_URL,
        "https": settings.DEFAULT_PROXY_URL
    }
).text

# Print IP Address
print(f"\n{Color.BLUE}Current IP:{Color.END} {address}")


# Gather IP Information
info: dict = requests.get(f"http://ip-api.com/json/{address}").json()

print(f"{Color.BLUE}Country:{Color.END} {info.get('country', '')}")
print(f"{Color.BLUE}Region:{Color.END} {info.get('regionName', '')}")
print(f"{Color.BLUE}City:{Color.END} {info.get('city', '')}")
print(f"{Color.BLUE}ISP:{Color.END} {info.get('isp', '')}")
