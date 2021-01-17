import sqlite3

conn = sqlite3.connect(r'config\baseforplaner.db')
cursor = conn.cursor()

# Создание таблицы
cursor.execute("""CREATE TABLE planer
                  (date, event, info, isdo)
               """)

cursor.execute("""CREATE TABLE categories
                  (id, text)
               """)
