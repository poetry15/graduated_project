from flask import Flask, request, abort, jsonify, send_file,render_template
from flask_socketio import SocketIO,emit
from moodmap.Exterior import imageGenerate
from WordCloud.WordCloud import dealAllData, dealSingleData
from pymongo import MongoClient
import requests,os
import json
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
socketio = SocketIO(app, cors_allowed_origins="*")
load_dotenv()

# 連接到 MongoDB
client = MongoClient(os.getenv("ALTAS_URL"))
db = client["test"]
formdata = db["formdatas"]
parameter = db["parameters"]
moodmap = db["MoodMap"]
image = db["ImageMap"]
dealAllData()

# LineBot
channel_access_token = os.getenv("channel_access_token")
configuration = Configuration(access_token=channel_access_token)
handler = WebhookHandler(os.getenv("channel_secret"))
url= os.getenv("url")
userid_list=[]
session_ID = {}
print("url: " + url)

# 系統檢查設定開關
scancode_flag = False
check5min_flag = False

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
def get_now_password(): # 提供表單驗證是否正確，用於驗證位於螢幕前
	if scancode_flag == False: # 不進行檢查
		return "ok"
	
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
		with ApiClient(configuration) as api_client:
			line_bot_api = MessagingApi(api_client)
			line_bot_api.push_message(
				PushMessageRequest(
					to=userid,
					messages=[TextMessage(text="Qrcode錯誤，請重新掃描")],
				)
			)
		return "reject"

@app.route('/check_userlast', methods=['POST'])
def check_time(): # 檢查是否距離上次 5 分鐘以上
	if check5min_flag == False: # 不進行檢查
		return "accept"

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

@socketio.on('connect')
def handle_connect():
	print('connected')

@socketio.on('message')
def handle_message(data):
	action = data['action']
	if action == 'initMap':
		image_data_list = list(image.find())
		map_data = db["Map"].find_one()
		image_data = [img['image'] for img in image_data_list if 'image' in img]
		if map_data:
			map_values = map_data['map']
		else:
			map_values = [0] * 36
			db["Map"].insert_one({'map': map_values})
		emit('message', {'action': 'initMap', 'map': map_values, 'image': image_data})

	elif action == 'updateMap':
		map_updates = data['map']
		for item in map_updates:
			id = int(item['id'])-1
			color = item['color']
			db["Map"].find_one_and_update({}, {"$set": {f"map.{id}": color}}, upsert=True)
		emit('message', {'action': 'updateMap', 'map': map_updates},broadcast=True)
	elif action == 'socketID':
		session_ID[request.sid] = data['data']

@socketio.on('disconnect')
def handle_disconnect():
	sid = request.sid
	if sid in session_ID:
		session_data = json.loads(session_ID[sid])
		if moodmap.count_documents({"LineID": session_data["LineID"]}) > 0:
			try:
				response = requests.post(
					os.getenv("url") + "/moodmap",
					json=session_data
				)
				if response.status_code == 200:
					print("成功發送資料到 /moodmap")
				else:
					print("發送資料到 /moodmap 失敗", response.status_code, response.text)
			except requests.exceptions.RequestException as e:
				print("請求 /moodmap 時出錯:", e)

	# 清理 session_ID 中的 sid 紀錄
	del session_ID[sid]


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
		formdata.insert_one(form_data)
		dealSingleData(form_data)
		imageUrl = imageGenerate(form_data["MoodColor"])
		image.insert_one({'image':imageUrl})
		socketio.emit('message', {'action': 'generateImage', 'image': imageUrl })
		return jsonify({"message": "Data saved", "data": dumps(form_data)}), 201
	except Exception as error:
		print("錯誤:", error)
		return jsonify({"error": "Error saving data"}), 500
	
# 回傳圖片(需要url)
@app.route("/picture", methods=["GET"])
def show_picture(	):
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


#moodmap
@app.route("/moodmap",methods=["POST"])
def NowStep():
	try:
		Info = request.json
		print(Info)
		if (Info["randomPoints"] == 0):
			moodmap.find_one_and_update(
				{"LineID": Info["LineID"],"MoodValue": Info["MoodValue"]},
				{"$set": {"LineID": Info["LineID"]+'-1', "randomPoints": Info["randomPoints"]}},
			)
		else:
			moodmap.insert_one(Info)
		print(moodmap.count_documents({"randomPoints": 0}))
		if moodmap.count_documents({"randomPoints": 0}) > 12:
			print("12筆資料已經收集完畢")
			lastest_data = list(moodmap.find({"randomPoints":0}).sort("_id",1).limit(12))
			lastest_image = image.find().sort("_id", 1).limit(12)
			user_ids=[entry["LineID"].split('-')[0] for entry in lastest_data]
			print(user_ids)
			# send_images_to_users(user_ids)
			delete_image = [record["_id"] for record in lastest_image]
			image.delete_many({"_id": {"$in": delete_image}})
			moodmap.delete_many({"_id": {"$in": [entry["_id"] for entry in lastest_data]}})
		return jsonify({"message": "Data received and processed"}), 200
	except Exception as error:
		print(error)
		return jsonify({"error": str(error)}), 500

def send_images_to_users(user_id):
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

# MoodMap
@app.route("/moodmap", methods=["GET"])
def get_moodmap():
	try:
		user_id = request.args.get("UserID")
		if user_id:
			MoodMap = list(db["MoodMap"].find({"LineID": user_id}))
			if MoodMap:
				return jsonify(dumps(MoodMap[0])), 200
			else: 
				return jsonify([]), 200
		return jsonify([]), 404
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
	socketio.run(app,debug=True)

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

# 