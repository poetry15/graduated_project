from moodmap.Exterior import imageGenerate
from dotenv import load_dotenv
from pymongo import MongoClient
import os

load_dotenv()
client = MongoClient(os.getenv("ALTAS_URL"))
db = client["test"]
All_Keywords = db["All_Keywords"]
keywords = All_Keywords.find()[0]['AllKeyWords']
print(imageGenerate("#fcba03"))
# from pymongo import MongoClient, errors
# import osx
# from dotenv import load_dotenv

# # 載入環境變數
# load_dotenv()

# # 獲取 MongoDB 連接字符串
# mongo_url = "mongodb+srv://jimmy147156:DeOw1n6fZVOcyi0t@cluster0.zbbv4pu.mongodb.net/"

# # 連接到 MongoDB
# try:
#     client = MongoClient(mongo_url)
#     # 測試連接
#     client.admin.command('ping')
#     print("Successfully connected to MongoDB Atlas")
# except errors.ServerSelectionTimeoutError as err:
#     print(f"Failed to connect to MongoDB Atlas: {err}")
# except errors.ConnectionFailure as err:
#     print(f"Connection to MongoDB Atlas failed: {err}")
# except Exception as e:
#     print(f"An error occurred: {e}")