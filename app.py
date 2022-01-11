from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def main():
    return render_template("index.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/join')
def join():
    return render_template("join.html")

@app.route('/detail')
def detail():
    return render_template("detail.html")




# 중복 확인 api
@app.route('/api/membership', methods=['POST'])
def api_membership():

    userid_receive = request.form['userid_give']
    exists = bool(db.dbdbdb.find_one({'userID': userid_receive}))
    return jsonify({'result': 'sucess', 'exists': exists})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)