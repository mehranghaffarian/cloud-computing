import requests

if __name__ == '__main__':
    response = requests.post(
        "https://api.mailgun.net/v3/sandboxa24d58344eb74bd9b73f39aedc34c3ff.mailgun.org/messages/",
        auth=("api", "ab5b6638da085196bca42114b98dcbd8-b02bcf9f-0c9fd7c4"),
        data={"from": "M <mailgun@sandboxa24d58344eb74bd9b73f39aedc34c3ff.mailgun.org>",
              "to": "mehranghaffarian1381@gmail.com",
              "subject": "recommended songs",
              "text": "test text"})

    print(response)
