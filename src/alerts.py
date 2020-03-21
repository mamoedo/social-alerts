import json
import re

TYPE_TWITTER = "twitter"
TYPE_INSTA = "instagram"
TYPES = (TYPE_INSTA, TYPE_TWITTER)
__alerts_list = []


def get_alerts_list():
    if not __alerts_list:
        load_alerts()
    return __alerts_list


def load_alerts():
    with open("alerts.json", "r") as fp:
        for alert in json.load(fp):
            if alert["type"] == TYPE_TWITTER:
                __alerts_list.append(TwitterAlert(alert))
            if alert["type"] == TYPE_INSTA:
                __alerts_list.append(InstagramAlert(alert))


def get_alerts_by_username(username):
    alert_list = []
    for alert in get_alerts_list():
        if username.lower() in map(str.lower, alert.users):
            alert_list.append(alert)
    return alert_list


def get_alerts_by_type(_type):
    return [alert for alert in get_alerts_list() if alert.type == _type]


def get_users_list(_type):
    users = []
    for alert in get_alerts_by_type(_type):
        for user in alert.users:
            users.append(user.lower())
    return users


class Alert:
    def __init__(self, alert):
        self.name = alert["name"]
        self.users = alert["users"]
        self.mail_list = alert["mail_list"]
        self.type = alert["type"]
        self.frequency = None if "frequency" not in alert else alert["frequency"]


class InstagramAlert(Alert):
    def __init__(self, alert):
        super().__init__(alert)


class TwitterAlert(Alert):
    def __init__(self, alert):
        super().__init__(alert)
        self.whitelist = alert["whitelist"]["list"]
        self.blacklist = alert["blacklist"]["list"]
        self.retweets = alert["retweets"]
        self.replies = alert["replies"]
        # Sanitize JSON regex
        self.whitelist_regex = "{}" if not alert["whitelist"]["regex"] else re.sub(r'\\\\', r'\\',
                                                                                   alert["whitelist"]["regex"])
        self.blacklist_regex = "{}" if not alert["blacklist"]["regex"] else re.sub(r'\\\\', r'\\',
                                                                                   alert["blacklist"]["regex"])
