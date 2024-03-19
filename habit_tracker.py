import os
import sqlite3
import time
from datetime import datetime


class Database:
    def __init__(self, db_file):
        # Create cursor and DB if it not exist
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS HABITS (
        id INTEGER PRIMARY KEY,
        HABIT TEXT NOT NULL,
        HABIT_DAYS INTEGER NOT NULL,
        LAST_CHECK TEXT NOT NULL,
        RECORD INT
        )
        ''')

        # Date today
        self.current_date = datetime.today().strftime("%d %B %Y")

    def end_task(self):
        # Commit task
        self.connection.commit()

    def exit_db(self):
        # Close connection to database
        self.cursor.close()
        self.connection.close()

    def create_habit(self, habit_name):
        # Create habit
        self.cursor.execute(
            'INSERT INTO HABITS (HABIT, HABIT_DAYS, LAST_CHECK) VALUES (?, ?, ?)', (habit_name, 1, self.current_date))

    def update_habit_name(self, habit_id, new_habit_name):
        # Update habit name in edit
        self.cursor.execute(
            'UPDATE HABITS SET HABIT = ? WHERE id = ?', (new_habit_name, habit_id))

    def edit_habit_date(self, habit_id, habit_date):
        # Edit habit date
        # Format: 17 March 2024
        self.cursor.execute(
            'UPDATE HABITS SET LAST_CHECK = ? WHERE id = ?', (habit_date, habit_id))

    def delete_habit(self, habit_id):
        # Delete habit
        self.cursor.execute('DELETE FROM HABITS WHERE id = ?', (habit_id))
        self.update_id_order()

    def update_id(self, habit_id, new_habit_id):
        # Update index primary key
        self.cursor.execute(
            'UPDATE HABITS SET id = ? WHERE id = ?', (new_habit_id, habit_id))

    def update_id_habit(self, habit_id, new_habit_id):
        # Update unique habit id to change order
        new_habit_id = int(new_habit_id)
        habit_id = int(habit_id)
        last_free_id = int(self.last_id_in_order()) + 1

        self.update_id(new_habit_id, last_free_id)
        self.update_id(habit_id, new_habit_id)
        self.update_id(last_free_id, habit_id)

    def update_id_order(self):
        # Update all habits id after deleting
        habits = self.get_habits()

        habit_counter = 1

        for row in habits:
            habit_id = row[0]
            if habit_id != habit_counter:
                self.update_id(habit_id, habit_counter)
            habit_counter += 1

    def last_id_in_order(self):
        # Return last id primary key
        self.cursor.execute('SELECT MAX(id) FROM HABITS')
        last_primary_key = self.cursor.fetchone()[0]
        return last_primary_key

    def delete_all(self):
        # Delete all habits
        self.cursor.execute('DELETE FROM HABITS')

    def null_habit(self, habit_id):
        # Set null count days to habit
        self.cursor.execute(
            'UPDATE HABITS SET HABIT_DAYS = ? WHERE id = ?', (0, habit_id))

    def update_habit_score(self, habit_id, new_habit_score):
        # Update habit score in edit
        self.cursor.execute(
            'UPDATE HABITS SET HABIT_DAYS = ? WHERE id = ?', (new_habit_score, habit_id))

    def update_habit(self, habit_id, add_days):
        # Add score days to habit

        habit = self.get_habit(
            habit_id)
        habit_days = habit[2]
        summ_habit_days = str(habit_days + int(add_days))

        self.cursor.execute(
            'UPDATE HABITS SET HABIT_DAYS = ? WHERE id = ?', (summ_habit_days, habit_id))
        self.cursor.execute(
            'UPDATE HABITS SET LAST_CHECK = ? WHERE id = ?', (self.current_date, habit_id))

    def update_record(self, habit_id, record_day):
        # Edit record
        self.cursor.execute(
            'UPDATE HABITS SET RECORD = ? WHERE id = ?', (record_day, habit_id))

    def delete_record(self, habit_id):
        # Delete record
        self.cursor.execute(
            'UPDATE HABITS SET RECORD = ? WHERE id = ?', (None, habit_id))

    def days_variance(self, habit_date):
        # Days variance between now and date in habit
        date_object = datetime.strptime(habit_date, "%d %B %Y")
        current_date = datetime.strptime(self.current_date, "%d %B %Y")
        date_variance = str(current_date - date_object)

        if " days" in date_variance:
            days_variance = date_variance[:date_variance.find(" day")]
        elif " day" in date_variance:
            days_variance = date_variance[:date_variance.find(" day")]
        else:
            hours, minutes, seconds = map(int, str(date_variance).split(":"))
            total_seconds = hours * 3600 + minutes * 60 + seconds
            days_variance = total_seconds / (24 * 3600)

        return int(days_variance)

    def get_habit(self, habit_id):
        # Return one habit
        self.cursor.execute('SELECT * FROM HABITS WHERE id = ?', (habit_id))
        habit = self.cursor.fetchone()
        return habit

    def get_habits(self):
        # Return all habits
        self.cursor.execute('SELECT * FROM HABITS')
        habits = self.cursor.fetchall()
        return habits


class Habits_print:
    def __init__(self, db):
        self.db = db
        self.main_print()

    def main_print(self):
        # Main interface
        self.print_habits()
        self.main_input()

    def main_update(self):
        # Update interface
        os.system('cls' if os.name == 'nt' else 'clear')
        self.main_print()

    def main_done(self):
        # Done function
        self.db.exit_db()
        print("Goodbye!")
        time.sleep(1)
        os.system("exit")

    def main_input(self):
        # Main tasks input
        task = input("What?: ")

        try:
            if task == "done":
                self.main_done()
                return 0
            if type(task) == str:
                self.main_tasks(task)
        except:
            sqlite3.ProgrammingError()
            print('Wrong type!')
            time.sleep(1)
            self.main_update()

    def main_tasks(self, task):
        # Tasks
        if task in "1234567890":
            self.update_habit(task)
        elif task == "add":
            self.create_habit()
        elif task == "del":
            self.delete_habit()
        elif task == "null":
            self.null_habit()
        elif task == "derec":
            self.delete_record()
        elif task == "edit":
            self.edit_habit()
        self.db.end_task()
        self.main_update()

    def update_habit(self, task):
        # Add habit score
        habit_id = str(task)
        habit = self.db.get_habit(habit_id)
        habit_last_date = habit[3]
        habit_variance = self.db.days_variance(habit_last_date)

        if habit_variance == 0:
            print("You already cheked today!")
            time.sleep(1)
        elif habit_variance >= 3:
            update_task = input("Your days row " +
                                str(habit_variance) + " days ? (y/n): ")
            if update_task == "y":
                self.db.update_habit(habit_id, habit_variance)
            else:
                self.main_update()
        elif habit_variance >= 1:
            self.db.update_habit(habit_id, 1)

    def create_habit(self):
        # Input for create habit
        habit_name = input("Write habit name: ")
        self.db.create_habit(habit_name)

    def delete_habit(self):
        # Input for delete habit
        habit_id = input("Choose habit id to delete: ")
        self.db.delete_habit(habit_id)

    def delete_record(self):
        # Input for delete record
        habit_id = input("Choose habit id to delete record: ")
        self.db.delete_record(habit_id)

    def edit_habit(self):
        # Input for edit record
        habit_id = input("Choose id to edit: ")

        name_question = input("Change name? (y/n): ")
        if name_question == "y":
            habit_name = input("Write new habit name: ")
            self.db.update_habit_name(habit_id, habit_name)
        score_question = input("Change score? (y/n): ")
        if score_question == "y":
            habit_days = input("Write your score: ")
            self.db.update_habit_score(habit_id, habit_days)
        order_task = input("Change habit order? (y/n): ")
        if order_task == "y":
            new_habit_id = input("Write new habit order (id): ")
            self.db.update_id_habit(habit_id, new_habit_id)

    def null_habit(self):
        # Input for null record
        habit_id = input("Write habit id to zero score: ")

        habit = self.db.get_habit(habit_id)
        habit_days = habit[2]
        habit_record = habit[4]

        if habit_record == None or habit_record < habit_days:
            self.db.update_record(habit_id, habit_days)

        self.db.null_habit(habit_id)

    def main_help(self):
        print("Hi! Choose id and check your habit:")
        print("1234567890 - +1 count to habit")
        print("add - add a new habit")
        print("del - remove a habit")
        print("null - count to zero habit")
        print("derec - remove a record")
        print("edit - edit habit")
        print("done - exit <-- pls, use it")

    def print_habits(self):
        # Main habit printer

        self.main_help()

        habits = self.db.get_habits()

        for row in habits:
            habit_id = str(row[0])
            habit_name = row[1]
            days_row = str(row[2])
            last_check_date = row[3]
            record_days = str(row[4])
            days_word = " days"
            habit_variance = self.db.days_variance(last_check_date)

            if days_row == "1":
                days_word = " day"

            if habit_variance == 0:
                last_check_date = "Today"

            if habit_variance == 1:
                last_check_date = "Yesterday"

            if row[4] != None:
                print(habit_id, habit_name, days_row + days_word,
                      "Last check: " + last_check_date, "| Record: " + record_days)
            else:
                print(habit_id, habit_name, days_row + days_word,
                      "Last check: " + last_check_date)


db = Database('Habits_DB.db')
ui_manager = Habits_print(db)
