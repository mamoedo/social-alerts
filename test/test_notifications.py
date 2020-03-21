import os
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from src.config import sender_mail_address
from src.notifications import send_email

mail_to = "xxx@gmail.com"
title = "Alert name - User - Twitter alert"
body = """
<h1><img src="https://image.flaticon.com/icons/png/512/60/60580.png" height="55" width="55">  Alert | Twitter | user</h1>
<p><b>User: </b>user</p>
<p><b>Alias: </b>alias</p>
<p><b>Date: </b>date UTC</p>
<p><b>Keywords: </b>keyword</p>
<br>
<p><b>Tweet:</b></p>
<div style="border:2px solid black; border-radius:5px; width:500px;">
  <div style="padding:2px; width:100%; height:100%; display:table-cell; vertical-align: middle;"> user</pre>
  <div style="padding:2px; width:100%; height:100%; display:table-cell; vertical-align: middle;"> tweet</div>
</div>
<p><b>Link: </b>tweet_link</p>
"""

message = MIMEMultipart("alternative")
message['Subject'] = title
message['From'] = sender_mail_address
message.attach(MIMEText(body, 'html', 'utf-8'))
send_email(mail_to, message)
