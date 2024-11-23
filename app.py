from flask import Flask, request, abort, jsonify,render_template
from flask_socketio import SocketIO,emit
from moodmap.Exterior import imageGenerate, upload_image_to_imgur
from gen_round.gen import round_photo_generator, read_image_from_url
from WordCloud.WordCloud import dealAllData, dealSingleData
from pymongo import MongoClient
import requests,os
import threading
import json
import datetime
from bson import ObjectId
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
import threading

for thread in threading.enumerate():
    print(f"Thread Name: {thread.name}, Thread ID: {thread.ident}, Daemon: {thread.daemon}")


app = Flask(__name__)
CORS(app)
class JSONEncoder(json.JSONEncoder):
	def default(self, o):
		if isinstance(o, ObjectId):
			return str(o)
		return json.JSONEncoder.default(self, o)
app.json_encoder = JSONEncoder
socketio = SocketIO(app, cors_allowed_origins="*",async_mode='threading')
load_dotenv()


# 連接到 MongoDB
client = MongoClient(os.getenv("ALTAS_URL"))
db = client["test"]
formdata = db["formdatas"]
parameter = db["parameters"]
moodmap = db["MoodMap"]
image = db["ImageMap"]
map = db["Map"]
dealAllData()

# LineBot
channel_access_token = os.getenv("channel_access_token")
configuration = Configuration(access_token=channel_access_token)
handler = WebhookHandler(os.getenv("channel_secret"))
url= os.getenv("url")
session_ID = {}
print("url: " + url)


# 系統檢查設定開關
scancode_flag = False
check5min_flag = False
quick_flag = True
image_flag = False
people_limit = 12
min_limit = 5

# 定義一個函數，用於每小時檢查並發送消息
def send_at_every_hour():
	while True:
		now = datetime.datetime.now()
		# 檢查是否是整點（分鐘為 0）
		# print(now.minute, now.second)
		if ((now.minute == 42 and now.second == 40) or image_flag):
			map_info = list(map.find({"state": "active"}))
			for info in map_info:
				if info["people_count"] >= min_limit or info["update_count"] >= min_limit:	
					map.find_one_and_update({"_id": info["_id"]}, {"$set": {"state": "completed"}})
			map_info = list(map.find({}))
			for info in map_info:	
				if (info["state"] == "completed"):
					print("i'm here")
					socketio.emit('message', {'action': 'finish', 'round_ID': str(info["_id"])})
			time.sleep(60)  # 避免在同一分鐘內重複多次發送
		time.sleep(1)  # 每秒檢查一次



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
# 心情日記取資料用
@app.route('/getuserform', methods=['POST'])
def get_user_form():
	reqdata = request.json
	userid = reqdata["LineID"]
	if userid:
		user_form = list(formdata.find({"LineID": userid}).sort("Time", -1))
		# print(user_form)
		if user_form:
			for f in user_form:
				f.pop('_id')
			return jsonify(user_form), 200
		else:
			return jsonify([]), 200
	return jsonify([]), 404

@app.route('/getoneform', methods=['POST'])
def get_one_form():
	reqdata = request.json
	userid = reqdata["LineID"]
	time = reqdata["Time"]
	if userid:
		user_form = list(formdata.find({"LineID": userid, "Time": time}).limit(1))
		print(user_form)
		if user_form:
			for f in user_form:
				f.pop('_id')
			return jsonify(user_form), 200
		else:
			return jsonify([]), 200
	return jsonify([]), 404

@socketio.on('connect')
def handle_connect():
	print('connected')

@socketio.on('message')
def handle_message(data):
	userid_list = []
	action = data['action']
	print(data)
	if action == 'updateMap': # 要記得round_ID
		round_ID = data['round_ID']
		map_updates = data['map']
		update_fields = {}
		for item in map_updates:
			id = int(item['id'])-1
			color = item['color']
			update_fields[f"map.{id}"] = color

		map_data = db["Map"].find_one_and_update({"_id": ObjectId(round_ID)}, {"$set": update_fields, "$inc": {"update_count": 1}}, upsert=True, return_document=True)
		emit('message', {'action': 'updateMap', 'map': map_updates, 'round_ID': round_ID},broadcast=True)
		update_count = map_data['update_count']

		if update_count == people_limit:
			print(f"{people_limit}筆資料已經收集完畢")
			map.find_one_and_update({"_id": ObjectId(round_ID)}, {"$set": {"state": "completed"}})

	elif action == 'finish':
		image_data_split = data['img'].split(",")[1]
		threading.Thread(target=generate_image, args=(image_data_split, userid_list, data['round_ID'])).start()
		
def generate_image(image_data,userid_list, round_ID):
	try:
		image_url = upload_image_to_imgur(image_data)
		pixeled_image = read_image_from_url(image_url)
		url = round_photo_generator(pixeled_image, 0)
		print(f"生成的圖片 URL: {url}")
		send_images_to_users(userid_list,url)

		# 將結束的輪次資料刪除
		latest_data = list(moodmap.find({"round_ID": round_ID}).sort("_id",1).limit(people_limit))
		userid_list = list(set([entry["LineID"] for entry in latest_data]))

		latest_image = image.find({"round_ID": round_ID}).sort("_id", 1).limit(people_limit)
		delete_image = [record["_id"] for record in latest_image]
		image.delete_many({"_id": {"$in": delete_image}})
		moodmap.delete_many({"_id": {"$in": [entry["_id"] for entry in latest_data]}})
		map.delete_one({"_id": ObjectId(round_ID)})
		socketio.emit('message', {'action': 'deleteData', 'round_ID': round_ID})
	except Exception as e:
		print(f"生成圖片時出現錯誤: {e}")

# @socketio.on('disconnect')
# def handle_disconnect():
# 	if (exit_flag):
# 		sid = request.sid
# 		if sid in session_ID:
# 			session_data = json.loads(session_ID[sid])
# 			if moodmap.count_documents({"LineID": session_data["LineID"]}) > 0:
# 				try:
# 					response = requests.post(
# 						os.getenv("url") + "/moodmap",
# 						json=session_data
# 					)
# 					if response.status_code == 200:
# 						print("成功發送資料到 /moodmap")
# 					else:
# 						print("發送資料到 /moodmap 失敗", response.status_code, response.text)
# 				except requests.exceptions.RequestException as e:
# 					print("請求 /moodmap 時出錯:", e)
# 		# 清理 session_ID 中的 sid 紀錄
# 		del session_ID[sid]


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
		if (quick_flag == False):
			imageUrl = imageGenerate(form_data["MoodColor"])
		else:
			imageUrl = "https://i.imgur.com/hwNs4fY.jpeg"

		round_ID = setRound()
		image.insert_one({'image':imageUrl, 'Line_ID': form_data['LineID'], 'round_ID': round_ID})
		socketio.emit('message', {'action': 'generateImage', 'image': imageUrl,'round_ID': round_ID})
		return jsonify({"message": "Data saved", "image": imageUrl, "round_ID": round_ID}), 201
	except Exception as error:
		print("錯誤:", error)
		return jsonify({"error": "Error saving data"}), 500

def setRound():
	latest_map = map.find_one_and_update(
		filter={"state": "active", "people_count": {"$lt": people_limit}},  # 條件：當前狀態為 active 且 people_count 小於 people_limit
		update={"$inc": {"people_count": 1}},  # 將 people_count 增加 1
		sort=[("_id", -1)],  # 按照 _id 降序取最新的一筆資料
		return_document=True  # 返回更新後的文件
	)
	round_ID = ''

	if latest_map is None:
		new_map_info = {
			"map": [0] * 64,
			"people_count": 1,
			"state": "active",
			"update_count": 0
		}
		result = map.insert_one(new_map_info)
		round_ID = str(result.inserted_id)
	
	else:
		round_ID = str(latest_map["_id"])

	return round_ID




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
		print()
		print(Info)
		print()
		if (Info["randomPoints"] == 0):
			print('Hello World')
			result = moodmap.find_one_and_update(
				{"LineID": Info["LineID"],"MoodValue": Info["MoodValue"], "randomPoints": {"$ne": 0}},
				{"$set": {"LineID": Info["LineID"], "randomPoints": Info["randomPoints"]}},
			)
			print(result)
		else:
			moodmap.insert_one(Info)
		return jsonify({"message": "Data received and processed"}), 200
	except Exception as error:
		print(error)
		return jsonify({"error": str(error)}), 500

def send_images_to_users(user_id,url):
	for user in user_id:
		data = {
			"to": user,
			"messages": [{
				"type": "image",
				"originalContentUrl": url,
				"previewImageUrl": url,
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
			MoodMap = list(db["MoodMap"].find({"LineID": user_id,"randomPoints": {"$ne": 0}}))
			if MoodMap:
				return jsonify(dumps(MoodMap[0])), 200
			else: 
				return jsonify([]), 200
		return jsonify([]), 404
	except Exception as e:
		return str(e), 400

@app.route("/map",methods=["GET"])
def get_map():
	try:
		map_all_info = list(map.find({}))
		image_all_info = list(image.find({}))
		if map_all_info or image_all_info:
			result = {
				"map": convert_objectid(map_all_info),
				"image": convert_objectid(image_all_info)
			}
			return jsonify(result), 200
		else:
			return jsonify([]),200
	except Exception as e:
		return str(e), 400

def convert_objectid(data):
	if isinstance(data, list):
		return [convert_objectid(item) for item in data]
	elif isinstance(data, dict):
		return {key: convert_objectid(value) for key, value in data.items()}
	elif isinstance(data, ObjectId):
		return str(data)
	else:
		return data

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
	# 啟動線程，保持運行，檢查時間
	threading.Thread(target=send_at_every_hour, daemon=True).start()
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
