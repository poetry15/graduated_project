from flask import Flask, request, abort, jsonify, send_file,render_template
from pymongo import MongoClient, ReturnDocument
import requests,os
from bson.json_util import dumps
from dotenv import load_dotenv
from flask_cors import CORS
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
	Configuration,
	ApiClient,
	MessagingApi,
	PushMessageRequest,
	TextMessage,
)
import time

app = Flask(__name__)
CORS(app)
load_dotenv(dotenv_path='.env')

# 連接到 MongoDB
client = MongoClient(os.getenv("ALTAS_URL"))
db = client["test"]
formdata = db["formdatas"]
parameter = db["parameters"]

# LineBot
channel_access_token = os.getenv("channel_access_token")
configuration = Configuration(access_token=channel_access_token)
handler = WebhookHandler(os.getenv("channel_secret"))
url= os.getenv("url")
print("url: " + url)

user_id=[]

# QRcode
@app.route('/', methods=['GET'])
def show_qrcode():
	# 生成第一組密碼給網頁
	# generate_pw()
	# url = "qrcode.html?data=" + str(random_number)
	return render_template("qrcode.html")

@app.route('/form', methods=['GET'])
def a():
	return render_template("/form/index.html")

@app.route('/qrcode/genpassword', methods=['POST'])
def gen_password(): # 接收生成的 pw 並存起來
	password = (request.json)["password"]
	print("gen：\t" + password)
	db["parameters"].update_one({}, {'$set' : {'password': password}}, upsert=True)
	return "get new pw."

@app.route('/check_scanres', methods=['POST'])
def get_now_password(): # 提供表單目前密碼，用於驗證位於螢幕前
	# print(request.json)
	
	reqdata = request.json
	userid =  reqdata["UserID"]
	scanresult = reqdata["ScanResult"]
	password = parameter.find_one({}, {'_id' : 0, 'password' : 1}) # 搜尋全部、去除id、要留password
	# print("scan：\t" + scanresult)
	# print("get：\t" + password['password'])
	
	if scanresult == password['password']:
		print("scan：ok")
		return "ok"
	else: # Qrcode 錯誤，訊息告知
		print("scan：ok")
		# with ApiClient(configuration) as api_client:
		# 	line_bot_api = MessagingApi(api_client)
		# 	line_bot_api.push_message(
		# 		PushMessageRequest(
		# 			to=userid,
		# 			messages=[TextMessage(text="Qrcode錯誤")]
		# 		)
		# 	)
		return "reject"

@app.route('/check_userlast', methods=['POST'])
def check_time(): # 檢查是否距離上次 5 分鐘以上
	reqdata = request.json
	userid = reqdata["LINEID"]
	ans = ''
	findtime = formdata.find({
		"LineID" : userid,
		"TimeStamp" : { "$gte" : int(time.time())-300 } # 距離不超過300秒
	})
	
	for f in findtime:
		ans += str(f) + '<br>'
	print(int(time.time()))
	print(userid, ans=='')
	# 如果findtime為空，代表5分鐘內沒有紀錄
	if ans == '': 
		return "accept"
	else:
		return "reject"



# WordCloud
@app.route("/data", methods=["GET"])
def get_data():
	try:
		HotKeyword = (db["keywords"].find())[0]
		WordcloudImage = (db["wordcloud_images"].find())[0]
		return jsonify(
			{"HotKeyword": dumps(HotKeyword), "WordcloudImage": dumps(WordcloudImage)}
		)
	except Exception as e:
		return str(e), 400


# DataRecord, 接收表單資料
@app.route("/api", methods=["POST"])
def save_data():
	try:
		# 從 request.json 獲取數據並插入到 MongoDB
		form_data = request.json
		result = formdata.insert_one(form_data)
		return jsonify({"message": "Data saved", "data": dumps(form_data)}), 201
	except Exception as error:
		print("Error saving data:", error)
		return jsonify({"error": "Error saving data"}), 500



# 回傳圖片(需要url)
@app.route("/picture", methods=["GET"])
def show_picture():
	# 指定圖片的路徑
	image_path = "assets/positive_food.png"
	return send_file(image_path, mimetype="image/png")


# LineBot回傳情緒紀錄給使用者
@app.route("/send-message", methods=["POST"])
def send_message():
	data = request.json	
	print(data)
	headers = {
		"Content-Type": "application/json",
		"Authorization": f"Bearer {channel_access_token}",
	}
	response = requests.post(
		"https://api.line.me/v2/bot/message/push", json=data, headers=headers
	)

	if response.status_code == 200:
		print(response.text)
		return jsonify({"status": "success"}), 200
	else:
		return (
			jsonify({"status": "error", "message": response.text}),
			response.status_code,
		)
	
# 將步數加起來，若超過48則推播圖片，歸零(要記得測看看有沒有delay的問題)
@app.route("/moodmap", methods=["POST"])
def NowStep():
	try:
			Step = request.json
			# 更新 Steps 並獲取更新後的結果
			result1 = db["MoodMap"].find_one_and_update(
				{},
				[
					{"$set": {
						"Steps": {"$cond": {"if": {"$gt": [{"$add": ["$Steps", Step['randomPoints']]}, 48]}, "then": 1, "else": {"$add": ["$Steps", Step['randomPoints']]}}},
					}},
				],
				return_document=ReturnDocument.AFTER,
			)

			# 使用更新後的 Steps 值來更新 user_id_ub
			'''
			如果 total 等於 1，則將 user_id 設置為空陣列。
			否則，將 Step['LineID'] 添加到現有的 user_id 陣列中。
			'''
			total = result1["Steps"]
			result2 = db["MoodMap"].find_one_and_update(
				{},
				[
					{"$set": {
							"user_id": {"$cond": {"if": {"$eq": [total, 1]}, "then": [], "else": {"$concatArrays": ["$user_id", [Step['LineID']]]}}},
					}},
				],
				return_document=ReturnDocument.BEFORE,
			)
			print("現在total:", total)
			if total == 1:
				print("我要送信囉")
				user_id = result2["user_id"]
				user_id.append(Step['LineID'])
				print(user_id)
				for user in user_id:
					data = {
						"to": user,
						"messages": [{
							"type": "image",
							"originalContentUrl": url+"/picture",
							"previewImageUrl": url+"/picture",
							"size": "full",
							"aspectRatio": "1792:1024",
						}]
					}
					headers = {
						"Content-Type": "application/json",
						"Authorization": f"Bearer {channel_access_token}",
					}
					response = requests.post(
						"https://api.line.me/v2/bot/message/push", json=data, headers=headers
					)
					print(response.text)
			return jsonify({"message": "Data saved", "data": dumps(total)}), 201
	except Exception as error:
		print("Error saving data:", error)	
		return jsonify({"error": "Error saving data"}), 500

# MoodMap
@app.route("/moodmap", methods=["GET"])
def get_moodmap():
	try:
		MoodMap = (db["MoodMap"].find())[0]
		return jsonify(dumps(MoodMap))
	except Exception as e:
		return str(e), 400


@app.route("/callback", methods=["POST"])
def callback():
	# get X-Line-Signature header value
	signature = request.headers["X-Line-Signature"]

	# get request body as text
	body = request.get_data(as_text=True)
	app.logger.info("Request body: " + body)
	# handle webhook body
	try:
		handler.handle(body, signature)
	except InvalidSignatureError:
		app.logger.info(
			"Invalid signature. Please check your channel access token/channel secret."
		)
		abort(400)
	return "OK"

if __name__ == "__main__":
	app.run(debug=True)

# ------------------- 測試用 -------------------------------
# 有問必答hello world
# @handler.add(MessageEvent, message=TextMessageContent)
# def handle_message(event):
# 	with ApiClient(configuration) as api_client:
# 		line_bot_api = MessagingApi(api_client)
# 		line_bot_api.reply_message_with_http_info(
# 			ReplyMessageRequest(
# 				reply_token=event.reply_token,
# 				messages=[TextMessage(text="hello world")],
# 			)
# 		)
# 測試的時候用於清空整個collection的，盡量不要使用
# @app.route('/delete/cleanData', methods=['GET'])
# def deleteall():
#     try:
#         result = formdata.drop()
#         return jsonify({'message': 'Drop all data', "data": "OK"}), 201
#     except Exception as e:
#         print("error", e)

# 查詢訊息使用情況 
# @app.route("/quota", methods=["GET"])
# def test():
# 	quota_url = 'https://api.line.me/v2/bot/message/quota'
# 	headers = {
#     'Authorization': f'Bearer {channel_access_token}'
# 	}
# 	quota_response = requests.get(quota_url, headers=headers)
# 	if quota_response.status_code == 200:
# 		quota_data = quota_response.json()
# 		return quota_data
# 	else:
# 		return quota_response.text

# @app.route("/consumption", methods=["GET"])
# def test1():
# 	consumption_url = 'https://api.line.me/v2/bot/message/quota/consumption'
# 	headers = {
#     'Authorization': f'Bearer {channel_access_token}'
# 	}
# 	consumption_response = requests.get(consumption_url, headers=headers)
# 	if consumption_response.status_code == 200:
# 		consumption_data = consumption_response.json()
# 		return consumption_data
# 	else:
# 		return consumption_response.text

# ngrok config add-authtoken 2Ptq2vGVnvGqUJ2mOZkNQka6FKY_6Z4wUzdgXrtFatCRRSrch
