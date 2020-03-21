import smtplib
import threading
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src import config, log
from src.alerts import get_alerts_by_type, TYPE_TWITTER

INSTA_EMAIL_SUBJECT = "{} - {} - Instagram alert"
INSTA_EMAIL_BODY = """
<html>
  <body>
    <h1><img src="https://image.flaticon.com/icons/png/128/1051/1051313.png" height="55" width="55">  Alert | Instagram | {user}</h1>
    <p><b>User: </b>{user}</p>
    <p><b>Date: </b>{date}</p>
    <p><b>Title: </b>{caption}</p>
    <p><img src="{image_url}"></p>
  </body>
</html>
"""

BATCH_NOTIFICATION_TITLE = "{} - Twitter alerts resume every {} minutes"
BASIC_NOTIFICATION_TITLE = "{} - {} - Twitter alert"
BASIC_BODY = """
<h1><img src="https://image.flaticon.com/icons/png/512/60/60580.png" height="55" width="55">  Alerta | Twitter | {user}</h1>
<p><b>User: </b>{user}</p>
<p><b>Alias: </b>{alias}</p>
<p><b>Date: </b>{date} UTC</p>
<p><b>Keywords: </b>{keyword}</p>
<br>
<p><b>Tweet:</b></p>
<div style="border:2px solid black; border-radius:5px; width:500px;">
  <div style="padding:2px; width:100%; height:100%; display:table-cell; vertical-align: middle;"> {user}</div>
  <div style="padding:2px; width:100%; height:100%; display:table-cell; vertical-align: middle;"> {tweet}</div>
</div>
<p><b>Link: </b>{tweet_link}</p>
"""
BATCH_BODY = """
<html>
    <body>
        {tweets}
    </body>
</html>
"""

"""
pending_notifications = 
{
 "mail@example.com": [notification1, notification2, notification3],
 "mail2@example.com": [notification1, notification4]
}
"""
pending_notifications = {}


class TwitterNotification:

    def __init__(self, tweet, alert):
        self.tweet = tweet
        self.alert = alert
        self.keyword = tweet.contains_word(alert.whitelist, alert.whitelist_regex)
        log.info("{} - Notification created".format(alert.name))


def setup_periodic_notifications():
    for alert in get_alerts_by_type(TYPE_TWITTER):
        if alert.frequency:
            t = threading.Thread(target=send_twitter_pending_notifications, args=(alert,), daemon=True)
            t.start()


def create_pending_notification(notification):
    for email in notification.alert.mail_list:
        log.info("Creating pending notification for {}".format(email))
        if email in pending_notifications:
            pending_notifications[email].append(notification)
        else:
            pending_notifications[email] = [notification]


def send_twitter_notification(notification):
    log.info("Sending twitter notification")
    message = MIMEMultipart("alternative")
    message['Subject'] = BASIC_NOTIFICATION_TITLE.format(notification.alert.name, notification.tweet.get_alias())
    message['From'] = config.sender_mail_address
    body = BASIC_BODY.format(user=notification.tweet.get_username(), alias=notification.tweet.get_alias(),
                             date=notification.tweet.get_created_at(),
                             tweet=notification.tweet.get_text(),
                             keyword=notification.tweet.contains_word(notification.alert.whitelist,
                                                                      notification.alert.whitelist_regex),
                             tweet_link="https://twitter.com/{}/status/{}".format(notification.tweet.get_username(),
                                                                                  notification.tweet.get_id()))
    message.attach(MIMEText(body, 'html', 'utf-8'))
    for email in notification.alert.mail_list:
        send_email(email, message)


def send_instagram_notification(feed, alert):
    log.info("Sending instagram notification")
    message = MIMEMultipart("alternative")
    message['Subject'] = INSTA_EMAIL_SUBJECT.format(alert.name, feed.username)
    message['From'] = config.sender_mail_address
    body = INSTA_EMAIL_BODY.format(image_url=feed.recent_media[0]['image'], caption=feed.recent_media[0]['caption'])
    message.attach(MIMEText(body, 'html', 'utf-8'))
    for email in alert.mail_list:
        send_email(email, message)


def send_twitter_pending_notifications(alert):
    while True:
        time.sleep(alert.frequency)
        log.info("{} - {} seconds passed. Checking pending notifications".format(alert.name, alert.frequency))
        for email in pending_notifications:
            body = ""
            for notification in pending_notifications[email]:
                if alert.name == notification.alert.name:
                    body = body + BASIC_BODY.format(user=notification.tweet.get_username(),
                                                    alias=notification.tweet.get_alias(),
                                                    date=notification.tweet.get_created_at(),
                                                    keyword=notification.keyword,
                                                    tweet=notification.tweet.get_text(),
                                                    tweet_link="https://twitter.com/{}/status/{}".format(
                                                        notification.tweet.get_username(),
                                                        notification.tweet.get_id()))
                    pending_notifications[email].remove(notification)
            if body:
                message = MIMEMultipart("alternative")
                message['Subject'] = BATCH_NOTIFICATION_TITLE.format(alert.name, alert.frequency / 60)
                message['From'] = config.sender_mail_address
                batch_body = BATCH_BODY.format(tweets=body)
                message.attach(MIMEText(batch_body, 'html', 'utf-8'))
                log.info("Sending pending notifications for {}".format(email))
                send_email(email, message)


def send_email(email, message):
    log.info("Sending email to {}".format(email))
    message['To'] = email
    with smtplib.SMTP_SSL(config.mail_smtp, config.ssl_port) as server:
        server.login(config.sender_mail_address, config.sender_mail_password)
        server.sendmail(config.sender_mail_address, email, message.as_string())
    log.info("Sent")
