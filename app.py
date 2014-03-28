#!/usr/bin/python3
import flask
from uuid import uuid4

app = flask.Flask(__name__)
app.secret_key = 'superasdf'

chatroom = []

def event_stream():
   oldmsglist = []
   while True:
      for u in chatroom:
         if u["id"] not in oldmsglist:
            msg = u['msg']
            oldmsglist.append(u["id"])
            yield 'data: [{}]: {}\n\n'.format(u['user'], msg)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
        flask.session['user'] = flask.request.form['user']
        return flask.redirect('/')
    return '<form action="" method="post">user: <input name="user">'

@app.route('/post', methods=['POST'])
def post():
    if 'user' not in flask.session:
        return flask.redirect('/login')
    message = flask.request.form['message']
    user = flask.session.get('user')
    chatroom.append({"msg": message, "user":user, "id":uuid4()})
    return flask.Response(status=204)


@app.route('/stream')
def stream():
    return flask.Response(event_stream(), mimetype="text/event-stream")

@app.route('/')
def home():
    if 'user' not in flask.session:
        return flask.redirect('/login')
    user = flask.session.get('user')
    return """
        <!doctype html>
        <title>chat</title>
        <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>
        <style>body { max-width: 500px; margin: auto; padding: 1em; background: black; color: #fff; font: 16px/1.6 menlo, monospace; }</style>
        <p><b>hi, %s!</b></p>
        <p>Message: <input id="in" /></p>
        <div id="out"></div>
        <script>
            function sse() {
                var source = new EventSource('/stream');
                var out = document.getElementById('out');
                source.onmessage = function(e) {
                    // XSS in chat is fun
                    out.innerHTML =  e.data + '<br>' + out.innerHTML;
                };
            }
            $('#in').keyup(function(e){
                if (e.keyCode == 13) {
                    $.post('/post', {'message': $(this).val()});
                    $(this).val('');
                }
            });
            sse();
        </script>

    """ % flask.session['user']



if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=7000, threaded=True)

