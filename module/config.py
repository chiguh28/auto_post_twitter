import json
import os

base = os.path.dirname(os.path.abspath(__file__))
print(base)
api_json = os.path.normpath(os.path.join(base, '../setting/api.json'))

json_file = open(api_json, 'r')
api_key = json.load(json_file)

# tweepyのキー設定ファイル
CONFIG = {
    "API_KEY": api_key['API_KEY'],
    "API_SECRET_KEY": api_key['API_SECRET_KEY'],
    "LOGIN_ID": "@hiro25793926",
    "LOGIN_PW": "xxgk5717",
}
