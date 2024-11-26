import openai
import urllib.request
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from PIL import Image
import base64
import requests
import uuid
import firebase_admin
from firebase_admin import credentials, storage

cred = credentials.Certificate("updatepicture-3ea0e-firebase-adminsdk-egrig-039fa4e622.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'updatepicture-3ea0e.appspot.com'
})

# 初始化 Storage Bucket
bucket = storage.bucket()

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
      model="dall-e-3",
      prompt= f"Generate a landscape image with a predominant {keywords} color scheme and no palette.",
      size="1024x1024",
      quality="standard",
      n=1,
    )
    image_url = response.data[0].url
    with urllib.request.urlopen(image_url) as response:
      image_data = response.read()
      base64_encoded_data = base64.b64encode(image_data).decode('utf-8')
      img_url = upload_image_to_firebase(base64_encoded_data)
      print(img_url)
    return img_url
  except Exception as e:
    print(e)
    return None

def upload_image_to_firebase(image_data):
  filename = f"{uuid.uuid4().hex}.png"  # 為圖片生成唯一名稱
  # 上傳到 Firebase Storage
  blob = bucket.blob(filename)
  blob.upload_from_string(base64.b64decode(image_data), content_type="image/png")

  # 設置圖片為公開（可選）
  blob.make_public()

  # 返回公開圖片 URL
  return blob.public_url

def upload_image_to_imgur(image_data):
  url = "https://api.imgur.com/3/image"
  headers = {
    "Authorization": f"Client-ID ef14f9fb39946ee"
  }
  data = {
    "image": image_data,
  }
  
  response = requests.post(url, headers=headers, data=data)
  
  if response.status_code == 200:
    response_data = response.json()["data"]
    link = response_data["link"]
    deletehash = response_data["deletehash"]

      # 將 link 和 deletehash 保存到文本文件中
    with open("imgur_images.txt", "a") as file:
        file.write(f"Link: {link}, Deletehash: {deletehash}\n")

      # 返回圖片的 URL
    return link
  else:
    raise Exception(f"Failed to upload image to Imgur. Status code: {response.status_code}, Response: {response.text}")