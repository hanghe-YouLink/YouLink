import hashlib

import jwt
from flask import Flask, render_template, jsonify, request, redirect, url_for

app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.dbyoulink
SECRET_KEY = 'YOULINK'


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
    # 글쓰기 페이지에 사용자 닉네임을 띄워주는 api
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"user_ID": payload['user_ID']})
        return render_template('detail.html', nickname=user_info["user_NICK"])
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

# 메인페이지 닉네임
@app.route('/')
def main_nickname():
    # 메인 페이지에 사용자 닉네임을 띄워주는 api
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"user_ID": payload['user_ID']})
        return render_template('index.html', nickname=user_info["user_NICK"])
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# ID 중복 확인 api
@app.route('/api/membership', methods=['POST'])
def api_membership():
    user_id_receive = request.form['user_id_give']
    exists = bool(db.users.find_one({'user_ID': user_id_receive}))
    return jsonify({'result': 'success', 'exists': exists})


# NICK_NAME 중복 확인 api
@app.route('/api/membership2', methods=['POST'])
def api_membership2():
    user_nick_receive = request.form['user_nick_give']
    exists2 = bool(db.users.find_one({'user_NICK': user_nick_receive}))
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
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


# 로그인
@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    # pw 암호화
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    # db에서 유저ID PW를 찾는다.
    result = db.users.find_one({'user_ID': id_receive, 'user_PW': pw_hash})

    # 찾으면 JWT 토큰 발급
    if result is not None:
        payload = {
            'user_ID': id_receive
            # 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=5) 토큰 만료 시간 코드
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        # token값을 넘긴다.
        return jsonify({'result': 'success', 'token': token})
    # 없으면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# 글 작성하기
@app.route('/api/posting', methods=['POST'])
def posting():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_nick = db.users.find_one({"user_ID": payload['user_ID']}, {'_id': False})['user_NICK']
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
            'user_NICK': user_nick,
            'title': title_receive,
            'channel_title': ogTitle,
            'url': ogUrl,
            'image': ogImage,
            'comment': comment_receive
        }

        db.posts.insert_one(doc)
        return jsonify({'msg': '작성 완료!'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('/'))


# 등록된 글 보내기
@app.route('/api/sending', methods=['GET'])
def mainPosting():
    postings = list(db.posts.find({}, {'_id': False}))
    return jsonify({'all_postings': postings})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
