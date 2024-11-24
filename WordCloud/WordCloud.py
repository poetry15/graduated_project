import openai
from datetime import datetime
import datetime
import os
from wordcloud import WordCloud, ImageColorGenerator
import numpy as np
from dotenv import load_dotenv
import ast
import matplotlib.pyplot as plt
from PIL import Image
from scipy.ndimage import gaussian_gradient_magnitude
from pymongo import MongoClient
import io

load_dotenv()
# 這個優
openai.api_key = os.getenv("openai.api_key")
# 連接到 MongoDB Atlas
client = MongoClient(os.getenv("ALTAS_URL"))
db = client["test"]
formdata = db["formdatas"]
All_Keywords = db["All_Keywords"]
wordcloud_image = db["wordcloud_images"]
keyword = db['keywords']
AllDocument = formdata.find()
MoodKeyword = {}
MoodFactors = {}
text = []
HotKeywordCount = 3
today = datetime.date.today()


def clean_sensitive_content(text):
  response = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
      {
        "role": "system",
        "content": '''
        You will be provided with a block of text. Identify and replace any sensitive content (e.g., violence, hate speech, or adult material) with "*".
        Return the cleaned text without changing the rest of the content.
        '''
      },
      {
        "role": "user",
        "content": text
      }
    ],
    temperature=0.5,
  )
  message_dict = response.choices[0].to_dict()
  clean_data = message_dict["message"]["content"].strip()
  return clean_data


def extract_keywords(text):
  while openai.moderations.create(input=text).results[0].flagged:
    text = clean_sensitive_content(text)
    print("處理過的資料",text)
  while True:
    response = openai.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
      {
        "role": "system",
        "content": 
        '''
        You will be provided with a block of text, and your task is to translate text to extract a list of keywords from it.
        擷取完關鍵字後，幫我計算關鍵字出現頻率 有相似詞或同種類的詞幫我合併並算在一起，以python字典的形式回傳.
        for example: input: ['夕陽西下，天空染上橘紅色的光輝，我感受到無比的寧靜與滿足。','看著夕陽緩緩地沉入地平線，那種美麗的景象讓我心中充滿了寧靜和滿足感。','當我漫步在滿是櫻花的公園裡，花瓣隨風飄落，我感到無限的喜悅與幸福。','每一步都伴隨著櫻花的芬芳，心中充滿了春天的活力和對未來的美好期待。','夜晚的星空閃爍，繁星點點，我感到一種深深的孤獨和思索。','抬頭仰望無邊的夜空，心中彷彿也變得無限遼闊，但同時也感受到那份孤獨感。','走進那間古老的書店，書香撲面而來，我感到一種莫名的懷舊與安慰。','看著一本本承載著歲月的書籍，彷彿回到了那個簡單而美好的過去，心中充滿了溫暖。','大雨傾盆而下，雨水打在窗戶上，我感到一種說不出的哀愁與釋放。','雨水模糊了視線，也模糊了心中的煩惱，讓我在雨聲中找到了片刻的釋放和解脫。'] 
        output: {'夕陽': 2,'天空': 1,'橘紅色': 1,'光輝': 1,'寧靜': 2,'滿足': 2,'地平線': 1,'美麗': 1,'景象': 1,'心中': 2,'滿足感': 1,'櫻花': 2,'公園': 1,'花瓣': 1,'風飄落': 1,'喜悅': 1,'幸福': 1,'芬芳': 1,'春天': 1,'活力': 1,'未來': 1,'美好期待': 1,'星空': 1,'閃爍': 1,'繁星': 1,'孤獨': 2,'思索': 1,'夜空': 1,'無限遼闊': 1,'孤獨感': 1,'古老書店': 1,'書香': 1,'懷舊': 1,'安慰': 1,'書籍': 1,'歲月': 1,'簡單': 1,'美好': 1,'過去': 1,'溫暖': 1,'大雨': 1,'傾盆而下': 1,'窗戶': 1,'哀愁': 1,'釋放': 2,'視線': 1,'煩惱': 1,'雨聲': 1,'解脫': 1}
        ''',
      },
      {
        "role": "user",
        "content": f'''Extract keywords from the following text and 擷取完關鍵字後，幫我計算出現頻率。
        有相似詞或同種類的詞幫我合併並加在一起，不要有重複的詞出現，以python字典的形式回傳:
        {text}
        ''',
      }],
      temperature=0.3,
    )
    
    message_dict = response.choices[0].to_dict()
    keywords = message_dict["message"]["content"].strip()
    print(keywords)
    try:
      keywords = ast.literal_eval(keywords)
      if isinstance(keywords, dict):
        return keywords
    except (ValueError, SyntaxError):
      continue

def wordcloud(items):
	# mask與color
	d = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()
	color = np.array(Image.open(os.path.join(d, "assets/alice_color.png")))
	color = color[::3, ::3]

	mask = color.copy()
	mask[mask.sum(axis=2) == 0] = 255
	edges = np.mean(
		[gaussian_gradient_magnitude(color[:, :, i] / 255.0, 2) for i in range(3)],
		axis=0,
	)
	mask[edges > 0.08] = 255

	# font
	fontpath = "assets/msjh.ttc"

	# Generate a word cloud image
	wordcloud = WordCloud(
		min_font_size=5,
		mask=mask,
		font_path=fontpath,
		max_font_size=40,
		random_state=42,
		relative_scaling=0,
		prefer_horizontal=1.0,
		scale=3,  # 增加圖片解析度
	).generate_from_frequencies(items)
	# 繪圖
	# plt.figure()
	plt.imshow(wordcloud)

	image_colors = ImageColorGenerator(color)
	wordcloud.recolor(color_func=image_colors)
	plt.imshow(wordcloud, interpolation="bilinear")
	wordcloud.to_file("assets/wordcloud.png")
	# 將圖片保存到二進位資料
	img_buffer = io.BytesIO()
	wordcloud.to_image().save(img_buffer, format="PNG")
	img_binary = img_buffer.getvalue()
	return img_binary

def dealAllData():
  global MoodKeyword, MoodFactors, text, today
  for document in AllDocument:
    time_str =  document.get("Time", "")
    time_str = time_str.replace("上午", "AM").replace("下午", "PM")
    time_obj = datetime.datetime.strptime(time_str, "%Y/%m/%d %p%I:%M:%S")
    if (document and today != time_obj.date()): # 如果日期等於今天，繼續加入資料
      continue
    mood_word = document.get("MoodWord", "") # 情緒文字
    mood_factor = document.get("MoodFactor", "") # 情緒因子
    Mood = document.get("MoodKeyWord", "") # 情緒關鍵字
    if (mood_word):
      text.append(mood_word)
    if(mood_factor):
      for i in mood_factor.split(", "):
        if i in MoodFactors:
          MoodFactors[i] += 1
        else:
          MoodFactors[i] = 1
    if(Mood):
      for i in Mood.split(", "):
        if i in MoodKeyword:
          MoodKeyword[i] += 1
        else:
          MoodKeyword[i] = 1

  arr = sorted(MoodKeyword.items(),key= lambda x: x[1], reverse=True)
  items = {}
  if (text):
    items = extract_keywords(', '.join(text))
  items.update(MoodFactors)
  All_Keywords.update_one({},{"$set":{"AllKeyWords": items}},upsert=True)
  print(items)
  if (items):
    img_binary=wordcloud(items)
    wordcloud_image.update_one({},{"$set":{"image": img_binary}},upsert=True)
  length = len(arr)
  if length < HotKeywordCount:
    KeywordData = {
      "HotKeywords": arr[:length],
    }
  else:
    KeywordData = {
      "HotKeywords": arr[:HotKeywordCount],
    }
  keyword.update_one({},{"$set":KeywordData},upsert=True)

def dealSingleData(document):
  global MoodKeyword, MoodFactors, text, length,today
  time_str =  document.get("Time", "")
  print(time_str)
  time_str = time_str.replace("上午", "AM").replace("下午", "PM")
  time_obj = datetime.datetime.strptime(time_str, "%Y/%m/%d %p%I:%M:%S")
  if (document and today < time_obj.date()): # 如果日期比今天晚，今天變成文件的日期，資料清空
    MoodKeyword = {}
    MoodFactors = {}
    text = []
    today = document.get("Time", "")
  elif (document and today > time_obj.date()): # 如果日期比今天早，跳過
    return
  mood_word = document.get("MoodWord", "")
  mood_factor = document.get("MoodFactor", "")
  if(mood_word):  
    text.append(mood_word)

  if(mood_factor):
      for i in mood_factor.split(", "):
        if i in MoodFactors:
          MoodFactors[i] += 1
        else:
          MoodFactors[i] = 1
  items = {}
  if (text):
    items = extract_keywords(', '.join(text))
  items.update(MoodFactors)
  All_Keywords.update_one({},{"$set":{"AllKeyWords": items}},upsert=True)
  if (items):
    img_binary=wordcloud(items)
    wordcloud_image.update_one({},{"$set":{"image": img_binary}},upsert=True)   
  Mood = document.get("MoodKeyWord", "")
  for i in Mood.split(", "):
    if i in MoodKeyword:
      MoodKeyword[i] += 1
    else:
      MoodKeyword[i] = 1
  arr = sorted(MoodKeyword.items(),key= lambda x: x[1], reverse=True)
  length = len(arr)
  if length < HotKeywordCount:
    KeywordData = {
      "HotKeywords": arr[:length],
    }
  else:
    KeywordData = {
      "HotKeywords": arr[:HotKeywordCount],
    }
  keyword.update_one({},{"$set":KeywordData},upsert=True)
