from flask import Flask
from chatbot import *
from io import StringIO 
from flask import jsonify
import sys

class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout

app = Flask(__name__)

bot = ChatBot()

@app.route("/<request>",methods=['GET']) # ‘https://www.google.com/‘

def home(request):
	print(request)
	with Capturing() as output:

		entities, answer = bot.get_sample_answers(request)
		if answer != -1:
			query = sql_queries.Query(request, entities, answer)
			query.queryDB()

	output = jsonify(output)
	output.headers.add('Access-Control-Allow-Origin', '*')
    
	return output



app.run(port=5000)