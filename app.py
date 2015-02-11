from flask import Flask, render_template, request, redirect
import twilio.twiml
import requests
import jinja2
import os
from pymongo import MongoClient
import datetime

app = Flask(__name__)
DEBUG = True

MONGO_DB_URL = os.getenv('MONGOLAB_URI')
client = MongoClient(MONGO_DB_URL)
db = client.get_default_database()
phones_db = db.phones

GOOGLE_FORM_URL=""

def make_url(url):
	base_url = url.split('/viewform')[0]
	s = '"><div class="ss-q-title">'
	text = requests.get(url).text
	get_variables = {}
	get_variables['email'] = text.split(s + "Email")[0].split('for="')[-1]
	get_variables['phone'] = text.split(s + "Phone")[0].split('for="')[-1]
	get_variables['city'] = text.split(s + "City")[0].split('for="')[-1]
	get_variables['state'] = text.split(s + "State")[0].split('for="')[-1]
	return base_url + "/formResponse?ifq&" + \
				get_variables['email'] + "={email}" + \
				get_variables['phone'] + "={phone}" + \
				get_variables['city'] + "={city}" + \
				get_variables['state'] + "={state}" + \
				"&submit=Submit"

def submit_form(google_form_url, phone_number, email, city="", state=""):
	formatted_url = google_form_url.format(phone=phone_number, email=email, city=city, state=state)
	r = requests.get(url=formatted_url)

def is_email(email):
	return "@" in email and "." in email

@app.route('/phone/<mongo_uid>/', methods=['GET', 'POST'])
def phone(mongo_uid):
	if mongo_uid is None:
		return render_template("create_phone.html", phone_msg="ERROR 404: Page not found"), 404
	if request.method != 'POST':
		return render_template("create_phone.html", phone_msg="Phone created! Change the Messagine Request URL on Twilio the current URL.", phone_url="http://emailcollector.herokuapp.com/phone/" + mongo_uid)
	phone = phones_db.find_one({"_id" : ObjectId(mongo_uid)})
	print phone
	if phone is None or phone.count() < 1:
		return render_template("create_phone.html", phone_msg="ERROR 404: Page not found"), 404
	import pdb; pdb.set_trace()
	phone_number = request.form.get('From').strip()
	city = request.form.get('FromCity').strip()
	state = request.form.get('FromState').strip()
	email = request.form.get('Body').strip()
	resp = twilio.twiml.Response()
	if is_email(email):
		submit_form(phone.get('google_docs_url'), phone_number, email, city, state)
		resp.message(phone.get('success_msg'))
	else:
		resp.message(phone.get('failure_msg'))
	return str(resp)

@app.route('/', methods=['GET'])
def index():
	return render_template("index.html")

@app.route('/create_phone', methods=['GET','POST'])
def create_phone():
	if request.method != 'POST':
		return
	google_docs_url = make_url(request.form.get('google_docs_url').strip())
	success_msg = request.form.get('success_msg').strip()
	failure_msg = request.form.get('failure_msg').strip()
	_id = phones_db.insert({"google_docs_url": google_docs_url, "success_msg": success_msg, "failure_msg": failure_msg, "date_created": datetime.datetime.now()})
	if _id:
		return redirect('/phone/' + str(_id))
	# print google_docs_url, success_msg, failure_msg
	return render_template("create_phone.html", phone_msg="ERROR")

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 8000))
	app.run(host='0.0.0.0', port=port, debug=DEBUG)