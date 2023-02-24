from dotenv import load_dotenv
import os
import openai
import requests
from gtts import gTTS
import time
import io
import shutil

load_dotenv()

# /getme : bot status for all settings


CHATGPT_ENV=os.getenv('CHATGPT')
CHAT_ID_BOT = os.getenv('CHAT_ID_BOT')
CHAT_ID_GROUP = os.getenv('M_CHAT_ID')

TOKEN = os.getenv('LIVEGPT_BOT_API')
TELEGRAM_BOT_API_ENV = os.getenv('LIVEGPT_BOT_API')

openai.api_key = CHATGPT_ENV

message = "deneme mesaji"

url_bot_message = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID_GROUP}&text={message}"

url_info = f"https://api.telegram.org/bot{TOKEN}/getUpdates"


def url_send_message(chat_id: str, message: str):
    return f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
    
        
def send_audio_with_telegram(chat_id: str, file_path: str, post_file_title: str, bot_token: str) -> None:
    with open(file_path, 'rb') as audio:
        payload = {
            'chat_id': chat_id,
            'title': post_file_title,
            'parse_mode': 'HTML'
        }
        files = {
            'audio': audio.read(),
        }
        resp = requests.post(
            "https://api.telegram.org/bot{token}/sendAudio".format(token=bot_token),
            data=payload,
            files=files).json()
        
def send_photo_with_telegram(chat_id: str, file_path: str, post_file_title: str, bot_token: str) -> None:
    with open(file_path, 'rb') as photo:
        payload = {
            'chat_id': chat_id,
            'title': post_file_title,
            'parse_mode': 'HTML'
        }
        files = {
            'photo': photo.read(),
        }
        resp = requests.post(
            "https://api.telegram.org/bot{token}/sendPhoto".format(token=bot_token),
            data=payload,
            files=files).json()


def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)

def remove_spaces(string):
    return "".join(string.split())

def example_reach_rasa():
    import requests

    url: str = 'http://0.0.0.0:5005/webhooks/rest/webhook'

    data = {
        "sender": 1,
        "message": "i want to buy a tshirt"
    }

    result = requests.post(url=url, json=data)
    print(result.json()[0]['text'])



def mp3_to_bytearray(file):
    with io.open(file, "rb") as f:
        return bytearray(f.read())

# mp3_file = "audios/ChatGPTizG.mp3"
# byte_array = mp3_to_bytearray(mp3_file)
# print(byte_array)

def send_telegram_message(chat_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_API_ENV}/sendMessage?chat_id={chat_id}&text={message}"
    #await bot.send_message(chat_id=chat_id, text=message)
    requests.get(url).json()
    
async def send_audio_telegram_message(bot, chat_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_API_ENV}/sendAudio"
    #await bot.send_message(chat_id=chat_id, text=message)
    parameters = {
        "chat_id": chat_id,
        "audio": "response.mp3",
        "caption": "response audio received"
    }
    await requests.get(url, data=parameters).json()
    

 
def dall_e_test():
    response = openai.Image.create(
        prompt="a yellow tshirt with small L char logo and text with life is dream",
        n=1,
        size="256x256"
    )
    image_url = response['data'][0]['url']

    file_name = 'images/dalle_image_skirt.png'

    res = requests.get(image_url, stream = True)

    if res.status_code == 200:
        with open(file_name,'wb') as f:
            shutil.copyfileobj(res.raw, f)
        print('Image sucessfully Downloaded: ', file_name)
    else:
        print('Image Couldn\'t be retrieved')
    print(image_url)   


# chat_id_group=CHAT_ID_GROUP, telegram_bot_api_env=TELEGRAM_BOT_API_ENV
def telegram_live_gpt_response(url_info: str, chat_id_group: str, telegram_bot_api_env: str):
    last_textchat = (None, None)
    print('Hello GPt, VGPT and DGPT running')
    while True:
        # ses klasoru icindekileri komple silmek gerekli
        result = requests.get(url=url_info).json()
        #print(result)
        try:
            question, chat = get_last_chat_id_and_text(result)
            #print(f"text, chat  {text} {chat}")
            if (question, chat) != last_textchat and question.startswith('gpt'):
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=question[2:],
                    max_tokens=256,
                    n=1
                )
                response_text = response['choices'][0]['text']
                
                send_telegram_message(chat_id=chat_id_group, message=response_text)
                print(f'Response : {response_text}') 
               
                last_textchat = (question, chat)
            elif (question, chat) != last_textchat and question.startswith('vgpt'):
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=question[3:],
                    max_tokens=256,
                    n=1
                )
                response_text = response['choices'][0]['text']
                tts = gTTS(response_text, lang='tr', tld="com")
                tts.save(f'audios/ChatGPT{remove_spaces(response_text[:5])}.mp3')
                #url_send_message(chat_id=CHAT_ID_GROUP, message=response_text)
                send_audio_with_telegram(chat_id=chat_id_group,
                             file_path=f'audios/ChatGPT{remove_spaces(response_text[:5])}.mp3',
                             post_file_title=f'received-{remove_spaces(response_text[:5])}.mp3',
                             bot_token=telegram_bot_api_env)
                #requests.get(url=url_send_message(chat, question)).json()
                last_textchat = (question, chat)
            elif (question, chat) != last_textchat and question.startswith('dgpt'):
                response = openai.Image.create(
                    prompt=question[3:],
                    n=1,
                    size="256x256"
                )
                
                image_url = response['data'][0]['url']
                file_name = f'images/dll_img_{hash(image_url)}.png'
                
                res = requests.get(image_url, stream = True)
                with open(file_name,'wb') as f:
                    shutil.copyfileobj(res.raw, f)
                send_photo_with_telegram(chat_id=chat_id_group,
                             file_path=file_name,
                             post_file_title=f'received-{hash(image_url)}.png',
                             bot_token=telegram_bot_api_env)
                
                last_textchat = (question, chat)
        except:
            print(f'last activity not including message')
        time.sleep(1)

telegram_live_gpt_response(url_info=url_info, chat_id_group=CHAT_ID_GROUP, telegram_bot_api_env=TELEGRAM_BOT_API_ENV)  