import fileinput
import smtplib
import datetime
import email
import csv
import traceback
from datetime import date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

secrets = {}

def days_until(exp_date):
	e = exp_date.rstrip().split("/")
	eDate = date(int(e[2]), int(e[0]), int(e[1]))
	delta = eDate - date.today()
	return delta.days
	
def getTextBody(fileName):
	output = ""
	with fileinput.FileInput(fileName) as file:
		for line in file:
			output += line
	return output
	
def send(fields):
	html = "<html><head><body><img src=\"https://cor-liv-cdn-static.bibliocommons.com/images/NC-CHAPELHILL/logo.png?1513759594701\">"
	html += getTextBody("html.html")
	html += "<p><strong>100 Library Drive</strong></p><p><strong>Chapel Hill, NC&nbsp; 27514</strong></p><p><strong>(919) 968-2777</strong></p><br>"
	html += "<p><strong>" + fields[1] + "</p></strong>"
	html += "<p><strong>" + fields[-1].split(",")[0][0:] + "</p></strong>"
	html += "<p><strong>NAME: " + fields[1] + "</p></strong>"
	html += "<p><strong>LIBRARY CARD NUMBER: " + fields[4][2:16] + "</strong></p>"
	html += "<p><strong>RENEWAL DATE: " + fields[3] + "</strong></p>"
	html += "</body></html>"
	msg = MIMEMultipart("alternative")
	msg['Subject'] = "Library Card Expiration"
	msg['From'] = secrets["senderUsername"]
	msg['To'] = fields[-1].split(",")[0][0:]
	part2 = MIMEText(html, "html")
	msg.attach(part2)
	# Send the message via SMTP server.
	s = smtplib.SMTP_SSL(secrets["smtpServer"], secrets["smtpPort"])
	s.ehlo()
	s.login(secrets["senderUsername"], secrets["password"])
	import time 
	s.sendmail(msg['From'], msg['To'], msg.as_string())
	s.quit()
	
def log(row):
	with open('logs/log.csv', 'a') as csvfile:
		writer = csv.writer(csvfile, delimiter=',', quotechar='"')
		writer.writerow(row)
	
try:
	with fileinput.input("secrets.txt", inplace = False) as file:
		secrets["senderUsername"] = file.readline()[:-1]
		secrets["password"] = file.readline()[:-1]
		secrets["smtpServer"] = file.readline()[:-1]
		secrets["smtpPort"] = file.readline()
	
	with fileinput.FileInput('active_patrons.csv') as csvfile:
		reader = csv.reader(csvfile, delimiter=',', quotechar='"')
		next(reader)
		for row in reader:
			if days_until(row[3]) == 30:
				send(row)
				# Outputs the sent address's CSV row into the log.
				row.append(str(date.today().month) + "/" + str(date.today().day) + "/" + str(date.today().year))
				log(row)
	print("The script executed successfully.")
except Exception as e:
    log([e.__class__.__name__, traceback.format_exc().replace("\n", "| ")])
    print("The script executed with errors, which have been logged.")
