import random
import requests
import os
from flask import Flask, request
from fbmessenger import elements
from pymessenger.bot import Bot
from scrapping import scrape_google

app = Flask(__name__)
app.debug = True
ACCESS_TOKEN = 'EAAIiXXZBZBZAd8BAFIvOnSw5u7WIFkC5ZA7NSfCgSvziYhZBr3cUVlZBm4DZBiY4ZB0SYAT0ZBIXXJZCmBujX0OxZCiESbqZAw34xZC7KXT03DJZCpK0SxAi1nIJpN0AmU7LFd0rnNktcTW76XoqHxZAKPBV4ZCEEnRx5KYiFZC1hUSeINMSTKaZBYuNEil1P2'
VERIFY_TOKEN = 'd8230120b243bf986a3f998a24db674c451160a6'
bot = Bot(ACCESS_TOKEN)

messenger = Messenger(os.environ.get(ACCESS_TOKEN))
elements2 =[{
  "type":"phone_number",
  "title":"Jao's phone",
  "payload":"+261329125857"
    }]

@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if (request.args.get('hub.verify_token') == os.environ.get(VERIFY_TOKEN)):
            return request.args.get('hub.challenge')
        raise ValueError('FB_VERIFY_TOKEN does not match.')
    elif request.method == 'POST':
        messenger.handle(request.get_json(force=True))
        for event in messenger['entry']:
          messaging = event['messaging']
          for message in messaging:
            if message.get('message'):
                recipient_id = message['sender']['id']
                if message['message'].get('text'):
                    receive_message = message['message'].get('text').split()
                    if (receive_message[0] == "search_google"):
                        if len(receive_message) < 2:
                            send_message(recipient_id, 'Veuillez réessayer la syntaxe exacte doit être search_google + mot_recherché')
                        else:
                            response_query = ' '.join(map(str, receive_message[1:]))
                            send_message(recipient_id, 'ok, research google {} en cours ....'.format(response_query))
                            send_generic_template(recipient_id, response_query)
                    else:
                        response_sent_text = get_message()
                        send_BM(recipient_id, response_sent_text,elements2)
                        send_message(recipient_id, response_sent_text)
                if message['message'].get('attachments'):
                    response_sent_nontext = get_message()
                    send_message(recipient_id, response_sent_nontext)
            if message.get('postback'):
                recipient_id = message['sender']['id']
                if message['postback'].get('payload'):
                    receive_postback = message['postback'].get('payload').split()
                    print(receive_postback)
                    if receive_postback[0] == "PDF_view":
                            if len(receive_postback) < 2:
                                send_message(recipient_id, 'Veuillez réessayer la syntaxe exacte doit être PDF_view + lien_recherché')
                            else:
                                response_query = ' '.join(map(str, receive_postback[1:]))
                                file = attachments.File(url='http://example.com/file.txt')
								messenger.send(file.to_dict(), 'RESPONSE')
                                send_message(recipient_id, 'ok, transcription to PDF {} en cours ....'.format(response_query))
    return "Message Processed"

def get_message():
    sample_responses = ["You are stunning!", "We're proud of you.", "Keep on being you!", "We're greatful to know you :)"]
    return random.choice(sample_responses)

def send_message(recipient_id, response):
    bot.send_text_message(recipient_id, response)
    return "success"

def send_generic_template(recipient_id, research_query):
    url = "https://graph.facebook.com/v2.6/me/messages?access_token="+ACCESS_TOKEN
    results = scrape_google(research_query, 10, "en")
    payload = []
    for result in results:
        payload.append({
            "title": result["title"],
            "image_url": "https://www.presse-citron.net/wordpress_prod/wp-content/uploads/2020/05/Section-Google.jpg",
            "subtitle": result["description"],
            "default_action": {
                "type": "web_url",
                "url": result["link"],
                "webview_height_ratio": "tall",
            },
            "buttons": [
                {
                    "type": "web_url",
                    "url": result["link"],
                    "title": "View In Google"
                },
                {
                    "type": "postback",
                    "title": "PDF view",
                    "payload": "PDF_view {}".format(result["link"])
                }
            ]
        })
    print(payload[0])
    extra_data = {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": payload
            }
        }
    }

    data = {
        'recipient': {'id': recipient_id},
        'message': {
            "attachment": extra_data["attachment"]
        }
    }
    resp = requests.post(url, json=data)
    postback_data = request.get_json()
    print(postback_data)
    return "success"

def send_BM(recipient_id, response_sent_text,element):
    bot.send_button_message(recipient_id, response_sent_text,element)
    return "success"


if __name__ == "__main__":
    app.run()