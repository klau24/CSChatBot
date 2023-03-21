from flask import Flask
from chatbot import *
from io import StringIO 
from flask import jsonify
import sys

app = Flask(__name__)

bot = ChatBot()


@app.route("/<request>",methods=['GET']) # ‘https://www.google.com/‘

def home(request):
	print("Request:", request)
	response = get_response(request, bot)
	print("Response:", response)
	output = jsonify(response)
	output.headers.add('Access-Control-Allow-Origin', '*')
	return output

app.run(port=5000)