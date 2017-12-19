import fileinput
import smtplib
import datetime
from datetime import date
from email.mime.text import MIMEText

secrets = {}
with fileinput.input("secrets-which-should-not-be-in-an-unsecured-text-file-like-this.txt", inplace = False) as file:
	secrets["senderUsername"] = file.readline()[:-1]
	secrets["password"] = file.readline()[:-1]
	secrets["smtpServer"] = file.readline()[:-1]
	secrets["smtpPort"] = file.readline()
	#print(secrets)

def days_until(exp_date):
	e = exp_date.rstrip().split("/")
	eDate = date(int(e[2]), int(e[0]), int(e[1]))
	delta = eDate - date.today()
	return delta.days
	
def send(fields):
	string = "Dear" + fields[2][:-1] + " " + fields[1][1:] + ",\n\nYour library card will expire on " + fields[4] + "."
	string += "\n\nClick here for instruction on how to renew it.\n\nSincerely,\n\nChapel Hill Public Library"
	#print(string)
	msg = MIMEText(string)
	msg['Subject'] = "Library Card Expiration"
	msg['From'] = secrets["senderUsername"]
	msg['To'] = fields[-1]
	# Send the message via SMTP server.
	s = smtplib.SMTP_SSL(secrets["smtpServer"], secrets["smtpPort"])
	s.ehlo()
	s.login(secrets["senderUsername"], secrets["password"])
	print("Email sent.")
	import time 
	time.sleep(.5)
	s.sendmail(msg['From'], msg['To'], msg)
	s.quit()
	

with fileinput.input('PatronsExampleTest.csv', inplace = False) as file:
	next(file)
	for line in file:
		fields = line.rstrip().split(",")
		if days_until(fields[4]) < 31:
			send(fields)