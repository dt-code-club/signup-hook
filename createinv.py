import os
import requests


def generateinvite():
    channel_id = "863894196943060995"
    bot_token = os.environ.get("disc_token")

    url = f"https://discord.com/api/channels/{channel_id}/invites"

    data = {
        "max_age": 3600,
        "max_uses": 1,
        "temporary": True,
        "unique": True
    }

    headers = {
        "Authorization": f"Bot {bot_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=data, headers=headers)
    invite = response.json()
    print(invite)
    return invite["code"]


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(dotenv_path='./.env.local')
    print(generateinvite())
