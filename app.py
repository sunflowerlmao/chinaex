import json
import time
import random
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
import os
import zipfile
import webbrowser

# Создание экземпляра приложения Flask
app = Flask(__name__)
# Настройка папки для загрузки файлов
app.config['UPLOAD_FOLDER'] = 'uploads'

# Глобальные переменные для хранения данных и состояния приложения
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
    """
    Функция для загрузки базы данных из текстового файла.
    Читает данные из 'uploads/database.txt' и заполняет глобальный список bd.
    """
    database = open('uploads/database.txt', 'r')
    db = [x.split(':') for x in database]
    for i in range(len(db)):
        db[i][1] = db[i][1][:-1]
        db[i][1] = db[i][1].split(',')
        bd.append(db[i])
    print(bd)
    database.close()


def foundindex(a):
    """
    Функция для поиска индекса элемента в базе данных.
    Обновляет глобальный список zadach с найденными значениями.

    Аргументы:
    a (str): Имя файла для поиска.
    """
    for i in range(len(bd)):
        if bd[i][0] == a[:-4]:
            zadach[0] = bd[i][0]
            zadach[1] = bd[i][1]
    for j in range(0, len(zadach[1])):
        zadach[1][j] += '.png'


def selfile(a):
    """
    Функция для удаления расширения из имен файлов.

    Аргументы:
    a (list): Список имен файлов.

    Возвращает:
    list: Список имен файлов без расширений.
    """
    cor = []
    for i in range(len(a)):
        cor.append(a[i][:-4])
    return cor


def submitgrafems():
    """
    Функция для проверки правильности выбранных графем.

    Возвращает:
    int: 1 если все графемы выбраны правильно, иначе 0.
    """
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
    """
    Функция для сортировки графем по доступности.

    Аргументы:
    a (list): Список графем для сортировки.

    Возвращает:
    list: Отсортированный список доступных графем.
    """
    b = selfile(a)
    dostup = []
    clearr = []

    # Проверка наличия всех элементов в базе данных
    for i in range(0, len(bd) - 1):
        if all(elem in bd[i][1] for elem in b):
            for elem in bd[i][1]:
                if (elem + '.png') not in dostup:
                    dostup.append(elem + ".png")

    # Удаление дубликатов из списка
    for j in range(0, len(a) - 1):
        if a.count(a[j]) >= 9:
            clearr.append(a[j])

    # Возврат отсортированного списка или всех файлов в директории
    if len(a) > 0:
        return sorted(dostup)
    else:
        return [f for f in os.listdir('static/graf') if os.path.isfile(os.path.join('static/graf', f))]


def averagetime(f):
    """
    Функция для расчета среднего времени ввода иероглифа.

    Аргументы:
    f (list): Список данных для записи в лог.

    Возвращает:
    list: Список с информацией о количестве иероглифов и среднем времени ввода.
    """
    temp = ['\n', 'Количество иероглифов: ', '\n', 'Среднее время ввода иероглифа: ', '\n']
    temp.insert(2, str(len(timetest)))

    # Расчет среднего времени ввода


tempt = str(sum(timetest) / len(timetest))
temp.insert(5, tempt)
return temp


def logfilewrite(f):
    """
    Функция для записи логов в файл logfile.txt.

    Аргументы:
    f (list): Данные для записи в лог-файл.
    """
    logfile = open('logfile.txt', 'w')
    logfile.truncate()
    logfile.writelines(f)

    # Запись среднего времени, если есть данные о времени ввода
    if len(timetest) > 0:
        logfile.writelines(averagetime(f))

    logfile.writelines('Время проведения эксперимента - ' + str(formtime))
    logfile.close()


def randomier():
    """
    Функция для выбора случайного иероглифа из списка или шаблона.

    Возвращает:
    str: Имя случайного файла иероглифа.
    """
    global ierog_files, filenum

    # Проверка наличия файла шаблона и загрузка иероглифов из него
    if os.path.isfile('uploads/shablon.txt'):
        shablon = open('uploads/shablon.txt', 'r')
        if len(ierog_files) == 0:
            for line in shablon:
                ierog_files.append(str(line.strip()) + '.bmp')
        file = ierog_files[filenum]
        filenum += 1
    else:
        # Если шаблон отсутствует, выбираем случайный файл из директории
        if len(ierog_files) == 0:
            ierog_files = [f for f in os.listdir('static/ierog') if os.path.isfile(os.path.join('static/ierog', f))]
        file = random.choice(ierog_files)
        ierog_files.remove(file)

    return file


@app.route('/')
def index():
    """
    Главная страница приложения.

    Возвращает:
    HTML: Шаблон главной страницы index.html.
    """
    return render_template('index.html')


@app.route('/test', methods=['GET', 'POST'])
def test():
    """
    Страница тестирования.

    Обрабатывает запросы на получение изображений и результатов теста.

    Возвращает:
    HTML: Шаблон страницы тестирования test.html с изображениями графем и иероглифов.
    """
    global selected_grafs, k

    bdload()  # Загрузка базы данных перед началом теста

    logfilewrite(logtext)  # Запись логов

    # Получение доступных изображений графем
    if len(selected_grafs) > 0:
        folder1_images = sortir(selected_grafs)
    else:
        folder1_images = [f for f in os.listdir('static/graf') if os.path.isfile(os.path.join('static/graf', f))]

    # Проверка состояния отправки результатов теста
    if submitier[-1] == "1":
        submitier.append("0")
        folder2_image = randomier()  # Выбор случайного изображения иероглифа
        foundindex(folder2_image)  # Поиск индекса изображения в базе данных

        return render_template('test.html', folder1_images=folder1_images, folder2_image=folder2_image,
                               selected_grafs=selected_grafs)

    else:
        if k == 0:
            folder2_image = randomier()  # Первый случайный выбор изображения иероглифа
            foundindex(folder2_image)
            k += 1
        else:
            folder2_image = zadach[0] + '.bmp'  # Выбор изображения по заданию

    return render_template('test.html', folder1_images=folder1_images, folder2_image=folder2_image,
                           selected_grafs=selected_grafs)


@app.route('/set_remove', methods=['POST'])
def set_remove():
    """
    Обработка запроса на удаление выбранного изображения.

    Возвращает статус выполнения операции в формате JSON.
    """
    global isremove
    remove = request.form.get('remove')
    isremove = remove

    return jsonify({'status': 'ok'})


@app.route('/submit_selected_grafems', methods=['POST'])
def submit_selected_grafems():
    """
    Обработка отправки выбранных графем.

    Возвращает результат проверки в формате JSON.
    """
    global elapsed_time

    if submitgrafems() == 1:  # Проверка правильности выбранных графем
        selected_grafs.clear()  # Очистка списка выбранных графем
        submitier.append("1")

        logtext.append(str(zadach[0]) + ':' + str(int(elapsed_time // 3600)) + '.' + str(
            int((elapsed_time % 3600) // 60)) + '.' + str(int(elapsed_time % 60)) + '\n')
        timetest.append(int(str(elapsed_time).split('.')[0]))  # Запись времени ввода в лог

        return jsonify({'result': 'correct'})

    else:
        submitier.append("0")
        return jsonify({'result': 'incorrect'})


@app.route('/select_image', methods=['POST'])
def select_image():
    """
    Обработка выбора изображения пользователем.

    Возвращает обновленный список выбранных графем в формате JSON.
    """
    global selected_grafs
    image_name = request.form['image_name']

    # Добавление или удаление изображения из списка выбранных графем в зависимости от состояния isremove
    if isremove:
        selected_grafs.remove(image_name)
        print('del', selected_grafs)
    else:
        selected_grafs.append(image_name)
        print('add', selected_grafs)

    return jsonify({'selected_grafs': selected_grafs})


@app.route('/update_selected_grafs', methods=['POST'])
def update_selected_grafs():
    """
    Обновление списка выбранных графем на основе данных из запроса.

    Возвращает обновленный список в формате JSON.
    """
    selected_grafs = request.form['selected_grafs']
    selected_grafs = json.loads(selected_grafs)

    return jsonify({'selected_grafs': selected_grafs})


@app.route("/start", methods=["POST"])
def start_timer():
    """
    Запуск таймера эксперимента.

    Возвращает сообщение о запуске таймера.
    """
    global start_time, running, k

    if k == 1:
        start_time = time.time()
        running = True
        k += 1
        return "Timer started"


@app.route("/stop", methods=["POST"])
def stop_timer():
    """
    Остановка таймера эксперимента.

    Возвращает сообщение о остановке таймера.
    """
    global running

    running = False
    return "Timer stopped"


@app.route("/time", methods=["GET"])
def get_time():
    """
    Получение текущего времени эксперимента.

    Возвращает строку с временем в формате ЧЧ:ММ:СС или сообщение об остановке эксперимента.
    """
    global start_time, running, elapsed_time

    if running:
        elapsed_time = time.time() - start_time
        return f"{int(elapsed_time // 3600):02d}:{int((elapsed_time % 3600) // 60):02d}:{int(elapsed_time % 60):02d}"
    else:
        return "Эксперимент остановлен!"


@app.route('/download', methods=['POST'])
def download_file():
    """
    Обработка запроса на скачивание файла логов.

    Возвращает файл logfile.txt как вложение.
    """
    return send_file('logfile.txt', as_attachment=True)


@app.route('/upload', methods=['GET', 'POST'])
def download():
    """
    Обработка загрузки файлов пользователем.

    Загруженные файлы сохраняются на сервере и распаковываются при необходимости.
    Возвращает HTML-страницу загрузки upload.html или перенаправляет на страницу успеха после завершения загрузки.
    """
    if request.method == 'POST' and request.files:
        graf = request.files["graf"]
        path = 'static/graf/'

        # Очистка папки перед загрузкой нового файла графемы
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

        # Очистка папки перед загрузкой нового файла иероглифов
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

        # Замена базы данных при загрузке нового файла базы данных
        if baza.filename:
            if os.path.isfile(path):
                os.remove(path)
            baza.save(os.path.join(app.config['UPLOAD_FOLDER'], baza.filename))

        shablon = request.files["shablon"]
        path = 'uploads/shablon.txt'

        # Замена шаблона при загрузке нового файла шаблона
        if shablon.filename:
            if os.path.isfile(path):
                os.remove(path)
            shablon.save(os.path.join(app.config['UPLOAD_FOLDER'], shablon.filename))

        return redirect(url_for('success'))

    return render_template('upload.html')


@app.route('/success', methods=['GET', 'POST'])
def success():
    """
    Страница успешной загрузки файлов.

    Загружает базу данных после успешной загрузки файлов и возвращает шаблон success.html.
    """
    bdload()
    return render_template('success.html')


@app.route('/clear', methods=['GET', 'POST'])
def clear():
    """
    Очистка всех загруженных файлов из папок.

    Возвращает шаблон clear.html после завершения очистки файлов.
    """
    q = 'static/graf'
    w = 'static/ierog'
    e = 'uploads/'

    # Очистка папок от файлов графем и иероглифов
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
    """ 
    Запуск приложения Flask. Открывает веб-браузер с адресом приложения. 

    Запускает сервер в режиме отладки (debug).
    """
    my_url = 'http://127.0.0.1:5000'
    webbrowser.open(my_url, new=0, autoraise=True)
    app.run(debug=True)
