import json
import time
import random
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import os
import zipfile
import webbrowser


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'


f = open('logfile.txt', 'w')
selected_grafs = []
bd = []
zadach = ['', '']
timetest = []
logtext = []
k = 0
submitier = [""]
ierog_files = [f for f in os.listdir('static/ierog') if os.path.isfile(os.path.join('static/ierog', f))]


def bdload():
    database = open('uploads/database.txt', 'r')
    db = [x.split(':') for x in database]
    for i in range(len(db)):
        db[i][1] = db[i][1][:-1]
        db[i][1] = db[i][1].split(',')
        bd.append(db[i])
    database.close()


def foundindex(a):
    for i in range(len(bd)):
        if bd[i][0] == a[:-4]:
            zadach[0] = bd[i][0]
            zadach[1] = bd[i][1]
    for j in range(0,len(zadach[1])):
        zadach[1][j] += '.png'


def selfile(a):
    cor = []
    for i in range(len(a)):
        cor.append(a[i][:-4])
    return cor

def submitgrafems():
    zadacha = list(zadach[1])
    print(zadacha)
    s = sorted(selected_grafs)
    z = sorted(zadacha)
    count = 0
    if len(s) == len(z):
        for i in range(len(s)):
            if s[i] == z[i]:
                count += 1
        if count == len(s):
            return 1
        else:
            return 0
    else:
        return 0

def sortir(a):
    b = selfile(a)
    dostup = []
    clearr = []
    for i in range(0, len(bd) - 1):
        if all(elem in bd[i][1] for elem in b):
            for elem in bd[i][1]:
                if (elem + '.png') not in dostup:
                    dostup.append(elem + ".png")
    for j in range(0,len(a)-1):
        if a.count(a[j]) >= 9:
            clearr.append(a[j])
    if len(a) > 0:
        return sorted(dostup)
    else:
        return [f for f in os.listdir('static/graf') if os.path.isfile(os.path.join('static/graf', f))]


def logfilewrite(f):
    logfile = open('logfile.txt', 'w')
    n = 0
    if n == 0:
        logfile.write("Эксперемент начался!\n")
        n += 1
    logfile.writelines(f)
    logfile.close()

def randomier():
    global ierog_files
    if not ierog_files:
        ierog_files = [f for f in os.listdir('static/ierog') if os.path.isfile(os.path.join('static/ierog', f))]
    file = random.choice(ierog_files)
    ierog_files.remove(file)
    return file

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/test', methods=['GET', 'POST'])
def test():
    global selected_grafs,k,getier
    bdload()
    if len(selected_grafs) > 0:
        folder1_images = sortir(selected_grafs)
    else:
        folder1_images = [f for f in os.listdir('static/graf') if os.path.isfile(os.path.join('static/graf', f))]
    print(submitier)
    if submitier[-1] == "1":
        submitier.append("0")
        folder2_image = randomier()
        print(111111222,folder2_image)
        foundindex(folder2_image)
        return render_template('test.html', folder1_images=folder1_images, folder2_image=folder2_image,
                               selected_grafs=selected_grafs)

    elif k == 0:
        folder2_image = randomier()
        print(111111000, randomier())
        foundindex(folder2_image)
        k += 1
    else:
        folder2_image = zadach[0] + '.bmp'
    return render_template('test.html', folder1_images=folder1_images, folder2_image=folder2_image,
                           selected_grafs=selected_grafs)

@app.route('/set_remove', methods=['POST'])
def set_remove():
    global isremove
    remove = request.form.get('remove')
    isremove = remove
    return jsonify({'status': 'ok'})

@app.route('/submit_selected_grafems', methods=['POST'])
def submit_selected_grafems():
    print('123123')
    if submitgrafems() == 1:
        selected_grafs.clear()
        submitier.append("1")

        return jsonify({'result': 'correct'})
    else:
        submitier.append("0")
        return jsonify({'result': 'incorrect'})

@app.route('/select_image', methods=['POST'])
def select_image():
    global selected_grafs
    global timetest
    image_name = request.form['image_name']
    if isremove:
        selected_grafs.remove(image_name)
        print('del', selected_grafs)
    else:
        selected_grafs.append(image_name)
        print('add', selected_grafs)
    print('zadach', zadach)
    return jsonify({'selected_grafs': selected_grafs})


@app.route('/update_selected_grafs', methods=['POST'])
def update_selected_grafs():
    selected_grafs = request.form['selected_grafs']
    selected_grafs = json.loads(selected_grafs)
    return jsonify({'selected_grafs': selected_grafs})

@app.route('/update_timer', methods=['POST'])
def update_timer():
    hours = request.form['hours']
    minutes = request.form['minutes']
    seconds = request.form['seconds']
    timess = str(hours)+':'+str(minutes)+":"+str(seconds)
    timetest.append(timess)
    print('times',timess)
    # Do something with the timerElapsed variable here
    return jsonify({'status': 'success'})


@app.route('/download', methods=['GET', 'POST'])
def download():
    if request.method == 'POST' and request.files:
        graf = request.files["graf"]
        path = 'static/graf/'
        if graf.filename:
            for filename in os.listdir(path):
                file_path = os.path.join(path, filename)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            graf.save(os.path.join(app.config['UPLOAD_FOLDER'], graf.filename))
            with zipfile.ZipFile('uploads/Графемы.zip', 'r') as zip_ref:
                zip_ref.extractall('static/graf/')
        ier = request.files["ier"]
        path = 'static/ierog/'
        if ier.filename:
            for filename in os.listdir(path):
                file_path = os.path.join(path, filename)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            ier.save(os.path.join(app.config['UPLOAD_FOLDER'], ier.filename))
            with zipfile.ZipFile('uploads/Иероглифы.zip', 'r') as zip_ref:
                zip_ref.extractall('static/ierog/')
        baza = request.files["baza"]
        path = 'uploads/database.txt'
        if baza.filename:
            if os.path.isfile(path):
                os.remove(path)
            baza.save(os.path.join(app.config['UPLOAD_FOLDER'], baza.filename))
        shablon = request.files["shablon"]
        path = 'uploads/shablon.txt'
        if shablon.filename:
            if os.path.isfile(path):
                os.remove(path)
            shablon.save(os.path.join(app.config['UPLOAD_FOLDER'], shablon.filename))
        return redirect(url_for('success'))

    return render_template('download.html')


@app.route('/success', methods=['GET', 'POST'])
def success():
    bdload()
    return render_template('success.html')


@app.route('/clear', methods=['GET', 'POST'])
def clear():
    q = 'static/graf'
    w = 'static/ierog'
    e = 'uploads/'
    for filename in os.listdir(q):
        file_path = os.path.join(q, filename)
        if os.path.isfile(file_path):
            os.unlink(file_path)
    for filename in os.listdir(w):
        file_path = os.path.join(w, filename)
        if os.path.isfile(file_path):
            os.unlink(file_path)
    for filename in os.listdir(e):
        file_path = os.path.join(e, filename)
        if os.path.isfile(file_path):
            os.unlink(file_path)
    return render_template('clear.html')


if __name__ == '__main__':
    my_url = 'http://127.0.0.1:5000'
    webbrowser.open(my_url, new=0, autoraise=True)
    app.run(debug=True)