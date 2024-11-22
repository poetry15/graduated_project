import openai
import urllib.request
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from PIL import Image
import base64
import requests

load_dotenv()
# 初始化 OpenAI 客戶端
openai.api_key = os.getenv("openai.api_key")

client = MongoClient(os.getenv("ALTAS_URL"))

def imagePromptGenerate(keywords):
  response = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
      {"role": "system", "content": "You are a storyteller, and based on the given keywords, imagine a scenario that can be used for AI image generation."},
      {"role": "user", "content": f"Please imagine a scenario that can be used for AI image generation. The list of keywords is as follows: {keywords}"}
    ]
  )
  message_dict = response.choices[0].to_dict()
  text = message_dict["message"]["content"].strip()
  print(text)
  return text

def imageGenerate(keywords):
  try:
    response = openai.images.generate(
      model="dall-e-2",
      prompt= f"Generate a landscape image with a predominant {keywords} color scheme and no palette. The scene should showcase natural beauty, with {keywords} as the central theme throughout the environment. Use soft gradients, detailed textures, and a harmonious composition that evokes a peaceful and immersive atmosphere. The {keywords} should enhance the visual appeal, creating depth and tranquility in the landscape.",
      size="256x256",
      quality="standard",
      n=1,
    )
    image_url = response.data[0].url
    with urllib.request.urlopen(image_url) as response:
      image_data = response.read()
      base64_encoded_data = base64.b64encode(image_data).decode('utf-8')
      img_url = upload_image_to_imgur(base64_encoded_data)
      print(img_url)
    return img_url
  except Exception as e:
    print(e)
    return None

def upload_image_to_imgur(image_data):
    url = "https://api.imgur.com/3/image"
    headers = {
        "Authorization": f"Client-ID fa8c9cac55933c1"
    }
    data = {
        "image": image_data,
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()["data"]["link"]
    else:
        raise Exception("Failed to upload image to Imgur")