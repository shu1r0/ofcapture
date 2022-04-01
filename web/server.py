from flask import Flask, render_template

async_mode = None

app = Flask(__name__, static_folder="./html/dist/static", template_folder="./html/dist")
app.config['SECRET_KEY'] = "keysecret!"


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)
