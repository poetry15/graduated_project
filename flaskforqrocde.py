from pymongo import MongoClient
import requests,os
from flask import Flask, request, abort, jsonify,render_template
from flask_cors import CORS
from dotenv import load_dotenv



app = Flask(__name__)
CORS(app)
load_dotenv()

client = MongoClient(os.getenv("ALTAS_URL"))
db = client["test"]
parameter = db["parameters"]

@app.route('/qrcode/genpassword', methods=['POST'])
def gen_password(): # 接收生成的 pw 並存起來
	password = (request.json)["password"]
	print("gen：\t" + password)
	db["parameters"].update_one({}, {'$set' : {'password': password}}, upsert=True)
	return "get new pw."

if __name__ == "__main__":
    app.run(debug=True, port=8000)
