from create import create, Account
import json
import sys
import settings
from lib.Color import Color
from lib import biographies, biography_updater, picture_updater, pictures, ip_changer


# Import Warning
if __name__ != "__main__": raise Exception("This file isn't meant to be imported. Please run it independently.")

# Command-Line Configurations
PROXY_URL: str = sys.argv[1].strip() if len(sys.argv) >= 2 else settings.DEFAULT_PROXY_URL
IP_CHANGE_URL: str = sys.argv[2].strip() if len(sys.argv) >= 3 else settings.DEFAULT_IP_CHANGE_URL

# Change IP
ip_changer.change(IP_CHANGE_URL)


def save_account(account: Account):
    """
    Saves created account's information inside the default save file.
    """

    with open(settings.ACCOUNTS_SAVE_FILE, "r", encoding="utf-8") as file: content: str = file.read().strip()

    file = open(settings.ACCOUNTS_SAVE_FILE, "w", encoding="utf-8")

    file.write(
        f"{content}"
        f"{'\n' if content != '' else ''}" +
        json.dumps(
            {
                'username': account.username,
                'email': account.email,
                'password': account.password,
                'doubt': account.doubt,
                'sessionid': account.sessionid
            }
        )
    )

    file.close()


def beautiful_print(account: Account):
    """
    Beautifully prints created account's credentials in the terminal.
    """

    print(f"\n{Color.BLUE}Username:{Color.END} {account.username}")
    print(f"{Color.BLUE}Email:{Color.END} {account.email}")
    print(f"{Color.BLUE}Password:{Color.END} {account.password}")

    # Special Treatment
    if account.sessionid != "": print(f"{Color.BLUE}SessionID:{Color.END} {account.sessionid}")

    print(f"{Color.BLUE}\nProfile:{Color.END} {Color.GREEN}https://instagram.com/{account.username}{Color.END}")


def update_biography(account: Account):
    """
    Updates created account's biography to a randomly chosen one.
    """

    text: str = biographies.random()
    print(f"\n{Color.BLUE}Updating biography:{Color.END} \"{text}\"")

    biography_updater.update(account, text)


def update_picture(account: Account):
    """
    Updates created account's profile picture to a randomly generated one.
    """

    picture: str = pictures.pick()
    print(f"{Color.BLUE}Updating Profile Picture...{Color.END}")

    picture_updater.update(account, picture)


def main():
    """
    Initiates terminal interface for account creation.
    """

    # Create Account
    account: Account = create({"http": PROXY_URL, "https": PROXY_URL} if PROXY_URL != "" else None)

    # Save & Print Credentials
    save_account(account)
    beautiful_print(account)

    # Update Biography & Picture
    if settings.AUTO_UPDATE_BIO: update_biography(account)
    if settings.AUTO_UPDATE_PICTURE: update_picture(account)


# Initiate Program
main()
