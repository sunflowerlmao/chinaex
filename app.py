import json
import time
import random
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
import os
import zipfile
import webbrowser


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

selected_grafs = []
bd = []
zadach = ['', '']
timetest = []
logtext = []
k = 0
submitier = [""]
ierog_files = []
start_time = 0
running = False
filenum = 0
timeofstart = time.localtime(time.time())
formtime = time.strftime("%H.%M.%S", timeofstart)


def bdload():
    database = open('uploads/database.txt', 'r')
    db = [x.split(':') for x in database]
    for i in range(len(db)):
        db[i][1] = db[i][1][:-1]
        db[i][1] = db[i][1].split(',')
        bd.append(db[i])
    print(bd)
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

def averagetime(f):
    temp = ['\n','Количество иероглифов: ','\n','Среднее время ввода иероглифа: ','\n']
    temp.insert(2,str(len(timetest)))
    tempt = str(sum(timetest)/len(timetest))
    temp.insert(5,tempt)
    return temp
def logfilewrite(f):
    logfile = open('logfile.txt', 'w')
    logfile.truncate()
    logfile.writelines(f)
    if len(timetest) > 0:
        logfile.writelines(averagetime(f))
    logfile.writelines('Время проведения эксперимента - '+str(formtime))
    logfile.close()

def randomier():
    global ierog_files,filenum
    if os.path.isfile('uploads/shablon.txt'):
        shablon = open('uploads/shablon.txt','r')
        if len(ierog_files) == 0:
            for line in shablon:
                ierog_files.append(str(line.strip())+'.bmp')
        file = ierog_files[filenum]
        filenum += 1
    else:
        if len(ierog_files) == 0:
            ierog_files = [f for f in os.listdir('static/ierog') if os.path.isfile(os.path.join('static/ierog', f))]
        file = random.choice(ierog_files)
        ierog_files.remove(file)
    return file
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/test', methods=['GET', 'POST'])
def test():
    global selected_grafs,k
    bdload()
    logfilewrite(logtext)
    if len(selected_grafs) > 0:
        folder1_images = sortir(selected_grafs)
    else:
        folder1_images = [f for f in os.listdir('static/graf') if os.path.isfile(os.path.join('static/graf', f))]

    if submitier[-1] == "1":
        submitier.append("0")
        folder2_image = randomier()
        foundindex(folder2_image)
        return render_template('test.html', folder1_images=folder1_images, folder2_image=folder2_image,
                               selected_grafs=selected_grafs)
    else:
        if k == 0:
            folder2_image = randomier()
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
    global elapsed_time
    if submitgrafems() == 1:
        selected_grafs.clear()
        submitier.append("1")
        logtext.append(str(zadach[0]) +':'+ str(int(elapsed_time // 3600))+'.'+str(int((elapsed_time % 3600) // 60))+'.'+str(int(elapsed_time % 60))+'\n')
        timetest.append(int(str(elapsed_time).split('.')[0]))
        return jsonify({'result': 'correct'})
    else:
        submitier.append("0")
        return jsonify({'result': 'incorrect'})

@app.route('/select_image', methods=['POST'])
def select_image():
    global selected_grafs
    image_name = request.form['image_name']
    if isremove:
        selected_grafs.remove(image_name)
        print('del', selected_grafs)
    else:
        selected_grafs.append(image_name)
        print('add', selected_grafs)
    return jsonify({'selected_grafs': selected_grafs})


@app.route('/update_selected_grafs', methods=['POST'])
def update_selected_grafs():
    selected_grafs = request.form['selected_grafs']
    selected_grafs = json.loads(selected_grafs)
    return jsonify({'selected_grafs': selected_grafs})
@app.route("/start", methods=["POST"])
def start_timer():
    global start_time, running,k
    if k == 1:
        start_time = time.time()
        running = True
        k += 1
        return "Timer started"
@app.route("/stop", methods=["POST"])
def stop_timer():
    global running
    running = False
    return "Timer stopped"
@app.route("/time", methods=["GET"])
def get_time():
    global start_time, running, elapsed_time
    if running:
        elapsed_time = time.time() - start_time
        return f"{int(elapsed_time // 3600):02d}:{int((elapsed_time % 3600) // 60):02d}:{int(elapsed_time % 60):02d}"
    else:
        return "Эксперимент остановлен!"

@app.route('/download', methods=['POST'])
def download_file():
    return send_file('logfile.txt', as_attachment=True)
@app.route('/upload', methods=['GET', 'POST'])
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

    return render_template('upload.html')


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