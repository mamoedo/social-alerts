[![module-twitter](https://img.shields.io/badge/module-Twitter-00aced)](https://www.twitter.com/)
[![module-instagram](https://img.shields.io/badge/module-Instagram-bc2a8d)](https://www.instagram.com/)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![python-version](https://img.shields.io/badge/python-3.5%20|%203.6%20|%203.7%20|%203.8-blue)](https://www.python.org/download/releases/3.0/)
[![license](https://img.shields.io/pypi/l/ansicolortags.svg)](https://github.com/mamoedo/social-alerts/blob/master/LICENSE.md)
[![open-source-love](https://badges.frapsoft.com/os/v1/open-source.png?v=103)](https://opensource.guide/)

# Social Alerts

Get notified instantly when your users of interest speak about something.

## Set up

### Install

First, clone the repository:

```
git clone https://github.com/mamoedo/social-alerts.git
cd social-alerts
```

Install the requirements in a new python virtual environment. Python3 is mandatory:

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configure

Configure the email used to send the alerts and the social media API tokens and secrets in the conf file. Fill the config files, located in the `conf` directory. Logging is set by default to store the log in the project root.

#### Google

Gmail configuration is used by default, so you just have to fill the user and password fields.
Using an [application password](https://support.google.com/accounts/answer/185833?hl=en) is recommended. Besides, you will probably need to allow non-secure apps [in Google](https://myaccount.google.com/lesssecureapps).

### Test

It's important to test the notifications before running the main program. If there's a problem with the email configuration, it will show up now.

In test_notifications.py, set the mail which will receive the test email
`mail_to = "xxx@gmail.com"`

Run the test
`python test/test_notifications.py`

Check out your inbox, you should have an email.

### Set up the alerts

Alert name. It will be shown in the alert title.
`"name": "HongKong Disturbs"`

Alert type. For the moment, only Twitter and Instagram are available.
`"type": "twitter",`

Users to monitorize.
```
"users": [
  "free_hk",
  "riots_hk",
  "united_protestors_hk",
  "annonymous_hk"
]
```

Keywords that trigger the alarm and its regex. Note that the backslash must be escaped to form a valid JSON. 
```
"whitelist": {
  "regex": "\\W{}(?=\\W)",
  "list": [
    "attack",
    "block",
    "protest",
    "meet",
    "destroy"
  ]
}
```

Words that, if present, won't fire an alarm.
```
"blacklist": {
  "regex": "",
  "list": [
    "peaceful",
    "love"
  ]
}
```

Mandatory for twitter alerts. Enable alerts based on tweets that are replies or retweets from the user list.
```
"retweets": false,
"replies": true,
```

Mail list to send the alerts.
```
"mail_list": [
  "example1@mail.com",
  "example2@mail.com"
  ]
},
```

Please note that the users mentioned are intended to be fake. I did not search them all to check if they exist.

### Deploy
 
You can run it in background in your RaspberryPi or your favourite device through SSH using [screen](https://gist.github.com/jctosta/af918e1618682638aa82):
```
screen -S alerts
python main.py
[Ctrl-A] + D (Detach the session)
```
And watch what's happening:
`tail -F logfile.log`

## Instagram module
Instagram usually asks for login if many consecutive requests are made, so I recommend to keep the user list as small as possible.

## TODO
* Bypass Instagram requests limits (by scrapping 1 profile every X minutes)
* Improve notifications CSS
* Implement Hashtags or Topics alerts for Twitter
* Improve error description when Instagram profile cannot be retrieved

## Contributing

I would be very happy to add other social modules made by the community. Try to follow the architecture and open a pull request. 

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
