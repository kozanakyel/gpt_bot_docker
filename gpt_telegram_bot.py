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
        response = requests.post(
            "https://api.telegram.org/bot{token}/sendAudio".format(token=bot_token),
            data=payload,
            files=files).json()
        return response
        
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
        response = requests.post(
            "https://api.telegram.org/bot{token}/sendPhoto".format(token=bot_token),
            data=payload,
            files=files).json()
        return response


def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)

def remove_spaces(string):
    return "".join(string.split())


def mp3_to_bytearray(file):
    with io.open(file, "rb") as f:
        return bytearray(f.read())


def send_telegram_message(chat_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_API_ENV}/sendMessage?chat_id={chat_id}&text={message}"
    requests.get(url).json()
    
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
            if (question, chat) != last_textchat and question.startswith('/gpt'):
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=question[3:],
                    max_tokens=256,
                    n=1
                )
                response_text = response['choices'][0]['text']
                
                send_telegram_message(chat_id=chat_id_group, message=response_text)
                print(f'Response : {response_text}') 
               
                last_textchat = (question, chat)
            elif (question, chat) != last_textchat and question.startswith('/doc'):
                response_text= f"Welcome the ShopyVerse GPT Docs.\nUse /gpt for getting Text response.\nUse /vgpt for getting Voice response.\nUse /dpt for creating AI images from Dalle model."
                
                send_telegram_message(chat_id=chat_id_group, message=response_text)
                print(f'Response : {response_text}') 
               
                last_textchat = (question, chat)
            elif (question, chat) != last_textchat and question.startswith('/vgpt'):
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=question[4:],
                    max_tokens=256,
                    n=1
                )
                response_text = response['choices'][0]['text']
                file_name = f'data/audios/ChatGPT{remove_spaces(response_text[:5])}.mp3'
                
                tts = gTTS(response_text, lang='tr', tld="com")
                tts.save(file_name)
                response_tg = send_audio_with_telegram(chat_id=chat_id_group,
                             file_path=file_name,
                             post_file_title=f'received-{remove_spaces(response_text[:5])}.mp3',
                             bot_token=telegram_bot_api_env)
                
                print(f'response_tg: {response_tg}')
                last_textchat = (question, chat)
                
                os.remove(file_name)
                print(f'removed this file {file_name}')
            elif (question, chat) != last_textchat and question.startswith('/dgpt'):
                response = openai.Image.create(
                    prompt=question[4:],
                    n=1,
                    size="256x256"
                )
                
                image_url = response['data'][0]['url']
                file_name = f'data/images/dll_img_{hash(image_url)}.png'              
                res = requests.get(image_url, stream = True)
                with open(file_name,'wb') as f:
                    shutil.copyfileobj(res.raw, f)
                response_tg = send_photo_with_telegram(chat_id=chat_id_group,
                             file_path=file_name,
                             post_file_title=f'received-{hash(image_url)}.png',
                             bot_token=telegram_bot_api_env)
                
                print(f'response_tg: {response_tg}')
                last_textchat = (question, chat)
                
                os.remove(file_name)
                print(f'removed this file {file_name}')
        except:
            print(f'last activity not including message')
        time.sleep(1)

telegram_live_gpt_response(url_info=url_info, chat_id_group=CHAT_ID_GROUP, telegram_bot_api_env=TELEGRAM_BOT_API_ENV)  

# docker build -t kozanakyel/gpt_bot:v0.2 .
# docker run --rm --name gpt_bot -v gpt_bot_data:/data kozanakyel/gpt_bot:v0.2