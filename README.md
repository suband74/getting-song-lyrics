[![Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![Tests](https://github.com/suband74/getting-song-lyrics/actions/workflows/python-app.yml/badge.svg)


# Проект в виде консольной утилиты для получения текстов песен.

- Проект реализует получения текста песни:
  - в виде текста
  - в виде картинки "Облако слов"
- Слова песен получаются с API сайта [Genius]https://genius.com


### Установка проекта на локальный компьютер

1. Должен быть предустановлен менеджер зависимостей `poetry`. Или установите `poetry` любым удобным способом. 
   Например: `curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -` 
2. Выполните клонирование репозитория: `git clone https://github.com/inkoit/sudoku-solver-task.git`
3. Затем выполните установку зависимостей проекта: `poetry install`


### Получение текста песни.

- Необходимо ввести следующие элементы команды для поиска слов песни:
  - Обязательная часть: `python3 src/getting_song_lyrics/main.py`
- Далее в произвольном порядке:
   1. Путь до выходного файла с решением с опцией "-о":
      - Имя файла произвольное
      - Расширение файла :
        - "txt" для получения простого текста песни
        - "png" для получения текста в виде "Облака слов"
   2. Путь до файла с ключом авторизации на сайте "Genius"
   3. Первые символы названия песни (чем больше тем лучше) заключенные в ковычки.
- Пример ввода команды: `python3 src/getting_song_lyrics/main.py "shape of my heart" -o result.png -c key.json` для получения картинки
- Пример ввода команды: `python3 src/getting_song_lyrics/main.py -o result.txt -c key.json "my heart my soul modern talking"` для получения текста


#### Внешние зависимости

- Тестирование кода с помощью [pytest](https://docs.pytest.org/en/6.2.x/)
- Контроль качества кода с помощью [flake8](https://flake8.pycqa.org/en/latest/)
- Форматирование кода с помощью [black](https://github.com/psf/black)
- Консольное решение с помощью [click](https://click.palletsprojects.com/en/8.0.x/)
