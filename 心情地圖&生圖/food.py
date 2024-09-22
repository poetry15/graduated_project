import openai
import urllib.request
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from PIL import Image
import datetime
load_dotenv()
# 初始化 OpenAI 客戶端
openai.api_key = os.getenv("openai.api_key")

client = MongoClient(os.getenv("ALTAS_URL"))

def get_food_recommendation():
  response = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
      {"role": "system", "content": "You are an assistant that analyzes emotions and recommends appropriate food based on the analysis. Based on the provided keywords and the current time, analyze the positive and negative emotions and recommend one food for each. return the recommended foods, with no additional explanations, adjectives, or descriptions."},
      {"role": "user", "content": f"Currently it is {current_time}. Based on the following keywords, analyze the positive and negative emotions and recommend one food for each. Please return the recommended foods. The list of keywords is as follows: {keywords}"}
      
      # {"role": "system", "content": "You are an assistant that analyzes emotions and recommends appropriate food based on the analysis. Based on the provided keywords and the current time, analyze the positive and negative emotions and recommend one food for each. Only return the names of the recommended foods, with no additional explanations, adjectives, or descriptions."},
      # {"role": "user", "content": f"Currently it is {current_time}. Based on the following keywords, analyze the positive and negative emotions and recommend one food for each. Please return only the names of the recommended foods. The list of keywords is as follows: {keywords}"}
    ]
  )
  message_dict = response.choices[0].to_dict()
  text = message_dict["message"]["content"].strip()
  return text

db = client["test"]
All_Keywords = db["All_Keywords"]
with All_Keywords.watch() as stream:
  for change in stream:
    if change["operationType"] == "update":
      keywords = All_Keywords.find()[0]['AllKeyWords']
      current_time = datetime.datetime.now().strftime("%H:%M:%S")
      vaild = "False"
      while "False" in vaild:
        text = get_food_recommendation()
        response = openai.chat.completions.create(
          model="gpt-3.5-turbo",
          messages=[
            {"role": "system", "content": "You are an inspector. Your task is to verify if the input contains valid food names(英文中文皆可). If the input contains exactly two food items, return them in the format '[Food1], [Food2]' (replace 'Food1' and 'Food2' with the actual food names). If any of the items are not food, return False."},
            {"role": "user", "content": f"Check if this input is correct and return only the food names in the format '[Food1], [Food2]': {text}"}
            
            # {"role": "system", "content": "You are an inspector. Your task is to verify if the input contains valid food names(英文中文皆可). If the input contains exactly two food items, return them in the format '[Food1], [Food2]' (replace 'Food1' and 'Food2' with the actual food names). If any of the items are not food or the format is incorrect, return 'False'."},
            # {"role": "user", "content": f"Check if this input is correct and return only the food names in the format '[Food1], [Food2]': {text}"}
          ]
        ) 
        message_dict = response.choices[0].to_dict()
        vaild = message_dict["message"]["content"].strip()
        print(text)
        print(vaild)
      vaild = vaild.split(", ")
      response = openai.images.generate(
        model="dall-e-3",
        prompt=f"生成一張圖片，圖的左半邊是{vaild[0]}，圖的右半邊是{vaild[1]}",
        size="1792x1024",
        quality="standard",
        n=1,
      )
      image_url = response.data[0].url
      urllib.request.urlretrieve(image_url, 'assets\\positive_food.png')

# response = openai.images.generate(
#   model="dall-e-3",
#   prompt=f"{text[1]}，只能是食物，背景要是白色的",
#   size="1024x1024",
#   quality="standard",
#   n=1,
# )
# image_url = response.data[0].url
# urllib.request.urlretrieve(image_url, 'negative_food.png')
