from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    courses = [
        {
            'title': 'Kypc Python',
            'description': 'Учебная программа "Программирование на Python" создана для тех, кто хочет с нуля освоить 3й по популярности язык в мире, и создавать на нём от простых приложений до высоконагруженных web-сервисов.',
            'price/month': 175.99
        },
        {
            'title': 'Разработка на Java',
            'description': 'Основам программирования на языке ЈАѴА; Принципам объектно-ориентированного программирования; Понимать механизмы многопоточности Java; Уметь сериализовать и парсить данные используя JSON.',
            'price/month': 75.99
        },
        {
            'title': 'Kypc Front-end',
            'description': 'Введение в веб-технологий. Структура НТML. Форматирование текста с помощью HTML. Управлять браузерами и элементами НТМL-страниц с помощью JavaScript. Владеть фреймворками React и Angular.',
            'price/month': 87.99
        }
    ]
    return render_template('index.html', courses=courses)

@app.route('/signup')
def signup():
    return render_template('signup.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)



