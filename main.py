import sys
import os
from PyQt5 import uic
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QTextCharFormat
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from win32com.shell import shell, shellcon  # pip install pywin32
import psutil  # pip install psutil
import pyautogui as pg  # pip install
import requests
import shutil
import sqlite3
import time
import keyboard
from threading import Thread


class AddEvent(QMainWindow):
    def __init__(self):
        super(AddEvent, self).__init__()
        uic.loadUi(r'config\ui\Add.ui', self)
        self.setWindowTitle('Add')

        # кнопка сохранения
        self.pushButton.clicked.connect(self.save_event)
        self.pushButton_2.clicked.connect(self.save_categories)

        # нажатие ентера
        self.lineEdit.returnPressed.connect(self.save_event)
        self.lineEdit_2.returnPressed.connect(self.save_event)

        # скрываем, что не надо
        self.listWidget.hide()
        self.pushButton_2.hide()

        # указать категорию
        self.checkBox.stateChanged.connect(self.show_categories)

    def show_categories(self):
        if self.checkBox.isChecked():
            # показываем все, что надо
            self.pushButton.hide()
            self.listWidget.show()
            self.pushButton_2.show()
            self.label_3.setText('Выберите категорию:')
            self.lineEdit_2.hide()
            # добавляем все категории
            conn = sqlite3.connect(r'config\baseforplaner.db')
            cursor = conn.cursor()
            sql = "SELECT * FROM categories"
            cursor.execute(sql)
            answer = cursor.fetchall()

            n = 0
            for all in answer:
                text = all[1]
                n += 1
                self.listWidget.addItem(text)

            if n == 0:
                self.label_4.setText('У вас нет категорий!\nДобавить можно\nв настройках')
                self.pushButton_2.setText('Настройки')
                self.pushButton_2.clicked.connect(self.open_settings)

        else:
            # обратно все показываем
            self.listWidget.hide()
            self.pushButton_2.hide()
            self.label_3.setText('Подробнее:')
            self.lineEdit_2.show()
            self.pushButton.show()
            self.label_4.setText('')

    def open_settings(self):
        self.clean = Settings()
        self.clean.show()
        self.close()

    def save_categories(self):
        n = self.listWidget.currentRow()
        if n != -1:
            n += 1
            # получаем текст
            conn = sqlite3.connect(r'config\baseforplaner.db')
            cursor = conn.cursor()
            sql = "SELECT * FROM categories WHERE id = '{}'".format(n)
            cursor.execute(sql)
            answer = cursor.fetchall()[0]
            id = answer[0]  # id категории во 2 таблице

            date = '.'.join(str(self.calendarWidget.selectedDate())[19:-1].split(', '))
            event = self.lineEdit.text()
            if '/' not in event:
                info = f'categories - {str(id)}'

                self.conn = sqlite3.connect(r'config\baseforplaner.db')
                self.cursor = self.conn.cursor()

                self.cursor.execute("""INSERT INTO planer
                                          VALUES ('{}', '{}', '{}', 'no')""".format(date, event, info))

                # Сохраняем изменения
                self.conn.commit()

                self.label.setText('Сохранено!')
                ex.reload()
                self.close()
            else:
                self.label_4.setText("Нельзя написать '/'!")
        else:
            self.label_4.setText('Вы не выбрали категорию!')

    def save_event(self):
        date = '.'.join(str(self.calendarWidget.selectedDate())[19:-1].split(', '))
        event = self.lineEdit.text()
        info = self.lineEdit_2.text()
        if event != '':
            if '/' not in event:
                self.conn = sqlite3.connect(r'config\baseforplaner.db')
                self.cursor = self.conn.cursor()

                self.cursor.execute("""INSERT INTO planer
                                  VALUES ('{}', '{}', '{}', 'no')""".format(date, event, info))

                # Сохраняем изменения
                self.conn.commit()

                self.label.setText('Сохранено!')
                ex.reload()
                self.close()
            else:
                self.label_4.setText("Нельзя написать '/'!")
        else:
            self.label_4.setText('Не вижу задачю!')


class Settings(QMainWindow):
    def __init__(self):
        super(Settings, self).__init__()
        uic.loadUi(r'config\ui\CleanerPlaner.ui', self)
        self.setWindowTitle('Cleaner')

        # кнопка сохранения
        self.pushButton.clicked.connect(self.save_settings)

        # достаем из конфига галочки
        f = open(r'config\CleanCFG.txt', 'r')
        answer = f.read()
        if str(answer[2]) == '1':
            self.checkBox.setChecked(True)
        if str(answer[1]) == '1':
            self.checkBox_2.setChecked(True)
        if str(answer[0]) == '1':
            self.checkBox_3.setChecked(True)

        # добавление дела
        self.pushButton_2.clicked.connect(self.add_categories)
        self.lineEdit.returnPressed.connect(self.add_categories)

    def add_categories(self):
        # текст
        text = self.lineEdit.text()
        # число (id)
        conn = sqlite3.connect(r'config\baseforplaner.db')
        cursor = conn.cursor()
        sql = "SELECT * FROM categories"
        cursor.execute(sql)
        answer = cursor.fetchall()
        # список всех уже существующих
        lst = []
        for i in answer:
            lst.append(i[1])

        if text not in lst:
            n = len(answer) + 1
            # добавляем категорию
            self.conn = sqlite3.connect(r'config\baseforplaner.db')
            self.cursor = self.conn.cursor()

            self.cursor.execute("""INSERT INTO categories
                                      VALUES ('{}', '{}')""".format(n, text))

            # Сохраняем изменения
            self.conn.commit()

            self.close()
        else:
            self.lineEdit.setText('Такая категория уже есть!')

    def save_settings(self):
        # Сохраняем галочки в конфиге
        f = open(r'config\CleanCFG.txt', 'w')
        answer = ''

        if self.checkBox_3.isChecked() is True:
            answer += '1'
        else:
            answer += '0'

        if self.checkBox_2.isChecked() is True:
            answer += '1'
        else:
            answer += '0'

        if self.checkBox.isChecked() is True:
            answer += '1'
        else:
            answer += '0'

        f.write(answer)
        f.close()

        # Меняем текст
        self.pushButton.setText('Настройки успешно сохранены!')
        time.sleep(0.1)
        self.close()


class ToDoPlaner(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(r'config\ui\uiplaner.ui', self)
        self.setWindowTitle('To Do Planer')

    # кнопка добавления
        self.pushButton_3.clicked.connect(self.open_add)
    # кнопка изменения (сделано)
        self.pushButton_4.clicked.connect(self.delete_event)

        self.color_calendar()

# лейбл
    # получаем дату для запроса

        self.conn = sqlite3.connect(r'config\baseforplaner.db')
        self.cursor = self.conn.cursor()
        self.question = '.'.join(str(self.calendarWidget.selectedDate())[19:-1].split(', '))
        # запрос
        sql = "SELECT * FROM planer WHERE date = '{}'".format(str(self.question))
        self.cursor.execute(sql)
        answer = self.cursor.fetchall()

        f = open(r'config\Temp', 'w')
        n = 0
        for i in answer:
            f.write(i[1])
            f.write('/')
            self.listWidget.addItem(i[1])
            if i[3] == 'yes':
                self.listWidget.item(n).setForeground(Qt.darkGreen)
            n += 1

        # лейбл с айпи
        try:
            self.label_4.setText(f'your ip: {requests.get("https://ramziv.com/ip").text}')
        except Exception as e:
            self.label_4.setText('')

        # текст приветствия
        self.label.setText(f'Привет, {os.getlogin()}!')

        # текст дела на сегодня
        answer = str(self.calendarWidget.selectedDate())[19:-1].split(', ')  # список
        self.label_2.setText(f'Вот дела на {answer[2]}.{answer[1]}.{answer[0]}:')

        # кнопка настроек
        self.pushButton.clicked.connect(self.settings)
        self.pushButton.setText('')
        self.pushButton.setIcon(QIcon(r'config\textures\settings.png'))
        self.pushButton.setIconSize(QSize(25, 25))
        self.pushButton.clicked.connect(self.settings)

        # прогресс бар на свободное место
        self.progressBar_2.setValue(self.procent())

        # кнопка очистки
        self.pushButton_2.clicked.connect(self.clear)

        # progress bar time
        self.timenow = int(str(time.ctime(time.time()))[11:-11])
        answertime = int(self.timenow * 100 / 24)
        self.progressBar.setValue(answertime)
        self.label_5.setText(str(time.ctime(time.time()))[11:-8])

        # логотип
        pixmap = QPixmap(r'config\textures\logotype.png')
        self.label_6.setPixmap(pixmap)

        # двойной клик по делу (дело готово)
        self.listWidget.itemDoubleClicked.connect(self.ready)

        # одинарный клик по делу (информация о деле)
        self.listWidget.itemClicked.connect(self.information)
        self.label_7.setText('')

        # изменилась дата на календаре
        self.calendarWidget.selectionChanged.connect(self.reload)

        # мотиватор
        self.label_8.setText(f'До завтра\nпримерно\n{24 - int(str(time.ctime(time.time()))[11:-11])} час(ов)')

        # поиск
        self.lineEdit.textChanged.connect(self.chearch)

        if n >= 13:
            self.lineEdit.show()
            self.label_9.show()
        else:
            self.lineEdit.hide()
            self.label_9.hide()

    def chearch(self):
        if self.lineEdit.text() != '':
            que = self.lineEdit.text()
            f = open(r'config\Temp')
            text = f.read().split('/')  # список дел, что были до нажатия кнопки
            f.close()

            n = 0
            for i in text:
                if que in i:
                    break
                n += 1
            self.listWidget.setCurrentRow(n)

    def del_dates(self):
        f = open(r'config\dates', 'r')
        text = f.read().rstrip('\n').split('/')  # 2020.11.10

        self.format = QTextCharFormat()
        self.format.setFontPointSize(8)

        true_dates = self.take_date()

        for date in text:
            if date != '':
                dt = f'{int(date[:4])}.{int(date[5:6])}.{int(date[7:])}'
                date = (int(date[:4]), int(date[5:6]), int(date[7:]))
                if date not in true_dates:
                    self.dt = QDate(int(dt[:4]), int(dt[5:6]), int(dt[7:]))
                    self.calendarWidget.setDateTextFormat(self.dt, self.format)

    def color_calendar(self):
        self.del_dates()
        # получаем список дат
        dates = self.take_date()
        for date in dates:
            self.dt1 = QDate(date[0], date[1], date[2])  # дата, которую необходимо выделить
            self.format = QTextCharFormat()
            self.format.setFontPointSize(13)
            # self.format.setBackground(Qt.darkCyan)
            self.calendarWidget.setDateTextFormat(self.dt1, self.format)

    def information(self):
        n = self.listWidget.currentRow()

        f = open(r'config\Temp')
        text = f.read().split('/')
        f.close()
        event = text[n]

        self.conn = sqlite3.connect(r'config\baseforplaner.db')
        self.cursor = self.conn.cursor()
        # запрос
        sql = "SELECT * FROM planer WHERE event = '{}'".format(event)
        self.cursor.execute(sql)
        answer = self.cursor.fetchall()[0][2]  # текст дополнительно

        if 'categories - ' in answer:
            que = answer.replace('categories - ', '')

            self.conn = sqlite3.connect(r'config\baseforplaner.db')
            self.cursor = self.conn.cursor()
            # запрос
            sql = "SELECT * FROM categories WHERE id = '{}'".format(que)
            self.cursor.execute(sql)
            answer = self.cursor.fetchall()[0]
            self.label_7.setText(answer[1])
        elif answer != '':
            if len(answer) >= 50:
                answer = answer[:50] + '-\n' + answer[50:]
            self.label_7.setText(f'Дополнительно: {answer}')
        else:
            self.label_7.setText('')

    def take_date(self):
        conn = sqlite3.connect(r'config\baseforplaner.db')
        cursor = conn.cursor()
        # запрос
        sql = '''SELECT * FROM planer'''
        cursor.execute(sql)
        answer = cursor.fetchall()
        lst = []

        f = open(r'config\dates', 'w')

        for all in answer:
            if all[3] == 'no':
                all = all[0]

                f.write(all)
                f.write('/')

                tpl = (int(all[:4]), int(all[5:6]), int(all[7:]))

                # проверка, что такой даты еще не было
                if tpl not in lst:
                    lst.append(tpl)

        return lst

    def open_add(self):
        self.addmenu = AddEvent()
        self.addmenu.show()

    def settings(self):
        self.clean = Settings()
        self.clean.show()

    def ready(self):
        n = self.listWidget.currentRow()

        if n != -1:

            f = open(r'config\Temp')
            text = f.read().split('/')  # список дел
            f.close()

            self.listWidget.item(n).setForeground(Qt.darkGreen)

            event = text[n]

            conn = sqlite3.connect(r'config\baseforplaner.db')
            cursor = conn.cursor()
            sql = """
            UPDATE planer 
            SET isdo = 'yes' 
            WHERE event = '{}'
            """.format(event)
            cursor.execute(sql)
            conn.commit()

            self.reload()

    def delete_event(self):
        self.label_7.setText('')

        self.n = self.listWidget.currentRow()
        if self.n != -1:
            f = open(r'config\Temp')
            text = f.read().split('/')  # список дел, что были до нажатия кнопки
            f.close()

            accept = QMessageBox.question(self, 'Удаление', f"Вы точно хотите удалить дело '{text[self.n]}'?",
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if accept == QMessageBox.Yes:

                conn = sqlite3.connect(r'config\baseforplaner.db')
                cursor = conn.cursor()
                question = '.'.join(str(self.calendarWidget.selectedDate())[19:-1].split(', '))

                sql = "DELETE FROM planer WHERE event = '{}' and date = '{}'".format(text[self.n], question)

                cursor.execute(sql)
                conn.commit()

                del text[self.n]
                self.listWidget.takeItem(self.n)

                f = open(r'config\Temp', 'w')
                n = 0
                for i in text:
                    f.write(i)
                    f.write('/')
                    n += 1

                self.color_calendar()

            if self.listWidget.count() >= 13:
                self.lineEdit.show()
                self.label_9.show()
            else:
                self.lineEdit.hide()
                self.label_9.hide()

    def delete(self, directory):
        folder = directory
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                pass

    def del_bin(self, confirm=True, show_progress=True, sound=True):
        flags = 0
        if not confirm:
            flags |= shellcon.SHERB_NOCONFIRMATION
        if not show_progress:
            flags |= shellcon.SHERB_NOPROGRESSUI
        if not sound:
            flags |= shellcon.SHERB_NOSOUND
        shell.SHEmptyRecycleBin(None, None, flags)

    def clear(self):
        f = open(r'config\CleanCFG.txt', 'r')
        answer = f.read()

        if str(answer[2]) == '1':
            # Нижний чекбокс - папка Temp в винде
            self.delete(r'C:\Windows\Temp')

        if str(answer[1]) == '1':
            # Средний чекбокс - корзина
            try:
                self.del_bin()
            except Exception as e:
                pass

        if str(answer[0]) == '1':
            # Верхний чекбокс - Temp в appdata
            self.delete(rf'C:\Users\{os.getlogin()}\AppData\Local\Temp')
            pass

        # меняем текст
        pg.alert(text='Очистка выполнена успешно!', title='Очистка', button='OK')

        # обновляем прогресс бар места
        self.progressBar_2.setValue(self.procent())

    def reload(self):
        self.label_7.setText('')

        # удаляем существующие дела
        self.listWidget.clear()

        # меняем даты в тексте приветствия
        answer = str(self.calendarWidget.selectedDate())[19:-1].split(', ')  # список
        self.label_2.setText(f'Вот дела на {answer[2]}.{answer[1]}.{answer[0]}:')

        # получаем дату для запроса
        self.conn = sqlite3.connect(r'config\baseforplaner.db')
        self.cursor = self.conn.cursor()
        self.question = '.'.join(str(self.calendarWidget.selectedDate())[19:-1].split(', '))
        # запрос
        sql = "SELECT * FROM planer WHERE date = '{}'".format(str(self.question))
        self.cursor.execute(sql)
        answer = self.cursor.fetchall()

        f = open(r'config\Temp', 'w')

        n = 0
        for i in answer:
            f.write(i[1])
            f.write('/')
            self.listWidget.addItem(i[1])
            if i[3] == 'yes':
                self.listWidget.item(n).setForeground(Qt.darkGreen)
            n += 1

        if n >= 13:
            self.lineEdit.show()
            self.label_9.show()
        else:
            self.lineEdit.hide()
            self.label_9.hide()

        # обновляем прогрессбар (время)
        self.timenow = int(str(time.ctime(time.time()))[11:-11])
        answertime = int(self.timenow * 100 / 24)
        self.progressBar.setValue(answertime)
        self.label_5.setText(str(time.ctime(time.time()))[11:-8])

        self.color_calendar()

    def procent(self):
        DISK = 'C:'
        total = int(psutil.disk_usage(DISK).total / (1024 * 1024 * 1024))
        free = int(psutil.disk_usage(DISK).free / (1024 * 1024 * 1024))
        procent = 100 - int(free * 100 / total)
        return procent


def listen():
    keyboard.add_hotkey('ENTER', ex.ready)
    keyboard.wait()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ToDoPlaner()
    ex.show()

    # горячие клавиши
    t1 = Thread(target=listen)
    t1.start()

    sys.exit(app.exec_())
