import requests

bot_token = '2105001904:AAFiRZH2_M2Mi9rZo2clX-7xyEomSIYfpeg'
chat_id = '2092707504'
def send_telegram_message(msg):
    base_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {
        "chat_id": chat_id,
        "text": msg
    }

    response = requests.post(base_url, params=params)
    result = response.json()


send_telegram_message('11111')