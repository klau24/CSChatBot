from flask import Flask
from chatbot import *
from io import StringIO 
from flask import jsonify
import sys

app = Flask(__name__)

bot = ChatBot()


@app.route("/<request>",methods=['GET']) # ‘https://www.google.com/‘

def home(request):
	print(request)
	entities, answer = bot.split_queries(request)
	responses = []
	for a in answer:
		if a != -1:
			query = sql_queries.Query(request, entities, a)
			responses.append(query.queryDB())
	print(". ".join(responses)+".")

	output = jsonify(". ".join(responses)+".")
	output.headers.add('Access-Control-Allow-Origin', '*')
    
	return output



app.run(port=5000)