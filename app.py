from flask import Flask, render_template, jsonify, request

app = Flask(__name__)
import hashlib
import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.dbsparta

# 메인페이지
@app.route('/')
def main():
    return render_template("index.html")

# 로그인페이지
@app.route('/login')
def login():
    return render_template("login.html")

# 회원가입페이지
@app.route('/join')
def join():
    return render_template("join.html")

# 글작성페이지
@app.route('/detail')
def detail():
    return render_template("detail.html")


# ID 중복 확인 api
@app.route('/api/membership', methods=['POST'])
def api_membership():
    user_id_receive = request.form['user_id_give']
    exists = bool(db.youlink.find_one({'user_ID': user_id_receive}))
    return jsonify({'result': 'success', 'exists': exists})


# NICK_NAME 중복 확인 api
@app.route('/api/membership2', methods=['POST'])
def api_membership2():
    user_nick_receive = request.form['user_nick_give']
    exists2 = bool(db.youlink.find_one({'user_NICK': user_nick_receive}))
    return jsonify({'result': 'success', 'exists': exists2})


# 회원가입 api
@app.route('/api/sign_up', methods=['POST'])
def sign_up():
    user_id_receive = request.form['user_id_give']
    user_pw_receive = request.form['user_pw_give']
    password_hash = hashlib.sha256(user_pw_receive.encode('utf-8')).hexdigest()
    user_nick_receive = request.form['user_nick_give']

    doc = {
        'user_ID': user_id_receive,
        'user_PW': password_hash,
        'user_NICK': user_nick_receive
    }
    db.youlink.insert_one(doc)
    return jsonify({'result': 'success'})

# 글 작성하기
@app.route('/api/posting', methods=['POST'])
def posting():
    title_receive = request.form['title_give']
    url_receive = request.form['url_give']
    comment_receive = request.form['comment_give']

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    ogTitle = soup.select_one('meta[property="og:title"]')['content']
    ogImage = soup.select_one('meta[property="og:image"]')['content']
    ogUrl = soup.select_one('meta[property="og:url"]')['content']

    doc = {
        'title': title_receive,
        'channel_title': ogTitle,
        'url': ogUrl,
        'image': ogImage,
        'comment': comment_receive
    }

    db.youlink.insert_one(doc)
    return jsonify({'msg': '작성 완료!'})


# @app.route('/')
# def showArticles():
#     articles = requests.get('특정 페이지의 div같은 태그명 또는 bs4로 긁어오기, 그중 상위 몇개만])
#     모두 다 들고오면 로딩 시 페이지 느릴 수 있음
#     return render_template('index.html', articles = articles)


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)