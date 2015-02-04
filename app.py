from flask import Flask, render_template, request, redirect
import twilio.twiml
import requests
import jinja2
import os

app = Flask(__name__)
DEBUG = False

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

def submit_form(phone_number, email, city="", state=""):
	formatted_url = GOOGLE_FORM_URL.format(phone=phone_number, email=email, city=city, state=state)
	r = requests.get(url=formatted_url)

def is_email(email):
	return "@" in email and "." in email

@app.route('/phone', methods=['GET', 'POST'])
def phone():
	if request.method == 'POST':
		phone_number = request.form.get('From').strip()
		city = request.form.get('FromCity').strip()
		state = request.form.get('FromState').strip()
		email = request.form.get('Body').strip()
		resp = twilio.twiml.Response()
		if is_email(email):
			submit_form(phone_number, email, city, state)
			resp.message("SUCCESS MESSAGE")
		else:
			resp.message("FAILURE MESSAGE")
		return str(resp)
	else:
		return redirect("http://ycombinator.com")

@app.route('/', methods=['GET'])
def index():
	return render_template("index.html")

@app.route('/create_phone', methods=['GET','POST'])
def create_phone():
	if request.method != 'POST':
		return
	google_docs_url = request.form.get('google_docs_url').strip()
	success_msg = request.form.get('success_msg').strip()
	failure_msg = request.form.get('failure_msg').strip()
	# print google_docs_url, success_msg, failure_msg
	return render_template("create_phone.html", phone_url=make_url(google_docs_url))

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 8000))
	app.run(host='0.0.0.0', port=port, debug=DEBUG)