#!/usr/bin/env python3
# -*- encoding:utf-8 -*-
"""
Breafs : Sample code for ChatGPT API for translater with Slack.
Requirements : pip install openai slack_skd
References : https://platform.openai.com/docs/api-reference/authentication
"""
import json
import threading
import slack_sdk
import openai
from flask import Flask, request, make_response

# Init
with open("honyaku_credentials.json") as f:
  credentials = json.load(f)
  OPENAI_API_KEY = credentials["openai_api_key"]
  SLACK_BOT_TOKEN = credentials["slack_bot_token"]
  SLACK_VERIFICATION_TOKEN = credentials["slack_verification_token"]
  TEAM_ID = credentials["team_id"]

slack_client = slack_sdk.WebClient(SLACK_BOT_TOKEN)

openai.api_key = OPENAI_API_KEY 
app = Flask(__name__)


def write_log(log_str):
  if 1:
    log_file = "honyaku.log"
    with open(log_file, "a") as f:
      log_str += "\n"
      f.write(log_str)
  return



def post_answer(channel, bot_id, user_id, thread_ts, text):
    global slack_client
    prompt = f"This is a Japanese/English translator.\n{text}"
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )
    answer = response.choices[0].text.strip()
   
    log_str = "="*5 + "\n"
    log_str += answer
    write_log(log_str)
    
    response = slack_client.chat_postMessage(channel=channel, text=answer, thread_ts=thread_ts)



@app.route("/", methods=["GET", "POST"])
def index():
    global SLACK_VERIFICATION_TOKEN, TEAM_ID
    log_str = "="*20 + "\n"
    log_str += json.dumps(request.json, indent=2) + "\n"
    resp = None
    if request.method == "POST":
      data = request.json
      slack_team_id = data.get("team_id")
      slack_token = data.get("token")
      if (slack_team_id and slack_team_id != TEAM_ID) or slack_token != SLACK_VERIFICATION_TOKEN:
        resp = make_response("Authentication Error", 401)
      else:
        slack_type = data.get("type")
        if slack_type == "url_verification":
          slack_challenge = data.get("challenge")
          resp = make_response(slack_challenge, 200)
          resp.mimetype = "text/plain"
        elif slack_type == "event_callback":
          event = data.get("event")
          event_type = event.get("type")
          channel_type = event.get("channel_type")
          if event_type in ["app_mention", "message"]:
            channel = event.get("channel")
            user_id = event.get("user")
            text = event.get("text","")
            thread_ts = event.get("thread_ts")
            if thread_ts is None:
              thread_ts = event.get("ts")
            authorizations = data.get("authorizations")
            bot_id = authorizations[0].get("user_id")
            if (event_type == "app_mention" or channel_type == "im") and user_id != bot_id:
              # Answer
              args = (channel, bot_id, user_id, thread_ts, text)
              thread = threading.Thread(target=post_answer, args=args)
              thread.start()
              log_str += text + "\n"
            log_str += "return 200 with Received"
            resp = make_response("Received", 200)
          else:
            resp = make_response("Received", 200)
        else:
          resp = make_response("Received", 200)
    if resp is None:
      resp = make_response("Bad Request", 400)
      log_str += "return 400"
    write_log(log_str)
    return resp


if __name__ == "__main__":
    app.run(host='0.0.0.0')
    #app.run(debug=False, port=443, ssl_context=('.\certs\server.crt', '.\certs\server.key'), host='0.0.0.0')
