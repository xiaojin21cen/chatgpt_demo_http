from flask import Flask, render_template, request, make_response, url_for, session
from flask_cors import CORS
import json
from datetime import timedelta
import openai
import os
import uuid
from mylogger import Logger

log = Logger('chatGPT.log', level='debug')

app = Flask(__name__)
app.config.from_pyfile('settings.py')
app.secret_key = "affedasafafqwe"
print("config ============== ", app.config)

app.config['SEND_FILE_MAX_AGE_DEFAULT '] = timedelta(seconds=1)

openai.api_key = app.config['OPENAI_API_KEY']
openai.organization = app.config['OPENAI_ORGANIZATION']

os.environ['http_proxy'] = app.config['HTTP_PROXY']
os.environ['https_proxy'] = app.config['HTTPS_PROXY']


@app.route('/')
def index():
    token = uuid.uuid4()
    log.logger.info("index.html ")

    session["chat_token"] = ''
    session["chat_messages"] = []

    return render_template('index.html', token=token)


@app.route('/chat', methods=['POST'])
def chat():
    log.logger.info("body = {} ".format(request.data.decode()))
    request_json = json.loads(request.data.decode())

    token = request_json['token']
    role=request_json['role']
    content = request_json['content']

    chat_token = session.get("chat_token")
    if chat_token != token:
        session["chat_token"] = token
        session["chat_messages"] = []

    # 清除上下文
    data = {}
    if content is None or content.strip()=='':
        data = {'role': 'system', "content": "您不说话怎么聊天！"}
    if content=='/rest' or content=='clr' or content=='cls' or content=='clear':
        session["chat_messages"] = []
        data = {'role': 'system', "content": "上下文已清空！"}
    else:
        chatMsg(role, content)

        all_chat_message_arr = session.get("chat_messages")

        context_line = app.config['CONTEXT_LINE']
        # 只保存20条的上下文
        all_chat_message_arr = all_chat_message_arr if len(all_chat_message_arr) <= context_line else all_chat_message_arr[len(all_chat_message_arr) - context_line:]

        try:
            completions = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=all_chat_message_arr
            )

            # 输出结果
            # print(completions)
            reply = completions.choices[0]['message']['content']
            data = chatMsg("assistant", reply)
        except Exception as ex:
            print(ex)
            data = {'role': 'system', "content": "请求异常"}

    json_str = json.dumps(data, ensure_ascii=False)
    resp = make_response(json_str)
    resp.headers["Content-Type"] = "application/json;chartset=UTF-8"  # 设置响应头
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS,PUT,DELETE'
    resp.headers['Access-Control-Allow-Headers'] = 'x-requested-with,Content-Type'
    log.logger.info(f"result = {json_str} ")
    return resp


def chatMsg(role, content):
    msg = {}
    msg["role"] = role
    msg["content"] = content

    chat_messages = session.get("chat_messages")
    chat_messages.append(msg)
    session["chat_messages"] = chat_messages

    log.logger.info(f"{role} -> {content}")
    return msg


if __name__ == '__main__':
    print(app.url_map)
    app.run(debug=True)
    CORS(app)
