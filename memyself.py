import mysql.connector
from kivy.clock import Clock
from plyer import notification
from datetime import datetime, timedelta
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard


class NavigationBarTop(MDBoxLayout):
    pass

class NavigationBar(MDBoxLayout):
    pass

class MyCard(MDCard):
    pass

class Home(Screen):
    pass

class SetPasswordScreen(Screen):
    def delete_password(self):
        app = MDApp.get_running_app()
        if app.conn:
            with app.conn.cursor() as cursor:
                cursor.execute("DELETE FROM app_password")
                app.conn.commit()
                self.show_success_popup("Password successfully deleted")
                app.root.current = 'home'
        else:
            self.show_error_popup("Database connection not available")

    def show_success_popup(self, message):
        content = MDLabel(
            text=message,
            theme_text_color='Custom',
            text_color=(1, 1, 1, 1),
            halign="center",
        )
        popup = Popup(title="Error", content=content, size_hint=(None, None), size=(300, 200))
        popup.open()
    def show_error_popup(self, message):
        content = MDLabel(
            text=message,
            theme_text_color='Custom',
            text_color=(1, 1, 1, 1),
            halign="center",
        )
        popup = Popup(title="Error", content=content, size_hint=(None, None), size=(300, 200))
        popup.open()

class EnterPasswordScreen(Screen):
    pass


class QuickPrediction(Screen):
    def calculate_prediction(self):
        try:
            date1_str = self.ids.date1.text
            date2_str = self.ids.date2.text
            date3_str = self.ids.date3.text

            date1 = datetime.strptime(date1_str, '%Y %m %d')
            date2 = datetime.strptime(date2_str, '%Y %m %d')
            date3 = datetime.strptime(date3_str, '%Y %m %d')

            diff1 = (date2 - date1).days
            diff2 = (date3 - date2).days

            averagecyclelength = (diff1 + diff2) // 2

            predicted_date = date3 + timedelta(days=averagecyclelength)

            self.show_prediction(predicted_date.strftime('%Y %m %d'))

        except ValueError:
            self.show_error_popup("Invalid date format. Please enter dates in YYYY MM DD format.")

    def show_prediction(self, predicted_date):
        diff1 = (datetime.strptime(self.ids.date2.text, '%Y %m %d') - datetime.strptime(self.ids.date1.text,
                                                                                        '%Y %m %d')).days
        diff2 = (datetime.strptime(self.ids.date3.text, '%Y %m %d') - datetime.strptime(self.ids.date2.text,
                                                                                        '%Y %m %d')).days
        average_cycle_length = (diff1 + diff2) // 2

        content = MDLabel(
            text=f"Predicted next menstrual start date:\n{predicted_date}\n\n"
                 f"Average cycle length: {average_cycle_length} days",
            theme_text_color='Custom',
            text_color=(1, 1, 1, 1),
            halign="center",
        )
        popup = Popup(title="Prediction Result", content=content, size_hint=(None, None), size=(400, 300))
        popup.open()

    def show_error_popup(self, message):
        content = MDLabel(
            text=message,
            theme_text_color='Custom',
            text_color=(1, 1, 1, 1),
            halign="center",
        )
        popup = Popup(title="Error", content=content, size_hint=(None, None), size=(400, 300))
        popup.open()

class PastData(Screen):
    def on_pre_enter(self):
        print("Loading data...")
        self.load_data()

    def load_data(self):
        app = MDApp.get_running_app()
        if app.conn:
            cursor = app.conn.cursor()
            cursor.execute('''SELECT * FROM period_data''')
            rows = cursor.fetchall()
            total_rows = len(rows)
            print("Total rows:", total_rows)  # Print the total number of rows for verification

            if rows:
                table = MDDataTable(
                    rows_num=total_rows,  # Specify the total number of rows
                    column_data=[
                        ('ID', dp(30)),
                        ('Start Date', dp(30)),
                        ('End Date', dp(30)),
                        ('Period Length', dp(30)),
                        ('Cycle Length', dp(30)),
                    ],
                    row_data=rows
                )
                self.ids.data_layout.clear_widgets()
                self.ids.data_layout.add_widget(table)
            else:
                print("No data found")
        else:
            print("Database connection not available")

    def on_enter(self):
        # This ensures the data is reloaded every time the screen is entered
        self.load_data()

class WindowManager(ScreenManager):
    pass

class MyApp(MDApp):
    conn = None
    password = None

    def build(self):
        print('Inside build method')
        self.create_db_table()
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = 'Pink'
        #self.root = Builder.load_file('my.kv')

        if self.conn:
            with self.conn.cursor() as cursor:
                cursor.execute('''SELECT password FROM app_password''')
                rows = cursor.fetchall()
                if len(rows) >= 1:
                    self.root.current = 'enter_password'
                    if len(rows) <= 0:
                        self.root.current = 'home'
        return None

        #return Builder.load_file('my.kv')

    def set_password(self, password, confirm_password):
        print('Inside set_password method')
        if self.conn:
            with self.conn.cursor() as cursor:
                cursor.execute('''SELECT password FROM app_password''')
                rows = cursor.fetchall()
                if len(rows) >= 1:
                    self.show_error_popup("Password already set. Cannot set a new password.")
                elif password == confirm_password:
                    cursor = self.conn.cursor()
                    cursor.execute("INSERT INTO app_password (password) VALUES (%s)", (password,))
                    self.conn.commit()
                    cursor.close()
                    self.show_success_popup("Password successfully set")
                    self.root.current = 'home'
                else:
                    self.show_error_popup("Password not set. Retry")


        print('Exiting set_password method')

    def show_error_popup(self, message):
        content = MDLabel(
            text=message,
            theme_text_color='Custom',
            text_color=(1, 1, 1, 1),
            halign="center",
        )
        popup = Popup(title="Error", content=content, size_hint=(None, None), size=(300, 200))
        popup.open()

    def show_success_popup(self, message):
        content = MDLabel(
            text=message,
            theme_text_color='Custom',
            text_color=(1, 1, 1, 1),
            halign="center",
        )
        popup = Popup(title="Error", content=content, size_hint=(None, None), size=(300, 200))
        popup.open()

    def verify_password(self, password):
        print('Inside verify_password method')
        if self.conn:
            with self.conn.cursor() as cursor:
                cursor.execute('''SELECT password FROM app_password''')
                stored_password = cursor.fetchone()[0]
                if password == stored_password:
                    self.root.current = 'home'
                else:
                    self.show_error_popup("Incorrect password. Please try again.")
        else:
            self.show_error_popup("Database connection not available")
        print('Exiting verify_password method')

    def calculate_average_cycle_length(self):
        print('Inside calculate_average_cycle_length method')
        if self.conn:
            with self.conn.cursor() as cursor:
                cursor.execute('''SELECT cycle_length FROM period_data ORDER BY id DESC LIMIT 3''')
                rows = cursor.fetchall()
                if len(rows) > 1:
                    cycle_lengths = [row[0] for row in rows if row[0] is not None]
                    if cycle_lengths:
                        average_cycle_length = sum(cycle_lengths) // len(cycle_lengths)
                        return average_cycle_length
            return None

    def calculate_predicted_start_date(self):
        print('Inside calculate_predicted_start_date method')
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''SELECT end_date FROM period_data ORDER BY id DESC LIMIT 1''')
            last_end_date_row = cursor.fetchone()
            if last_end_date_row is not None:
                last_end_date = last_end_date_row[0]
                average_cycle_length = self.calculate_average_cycle_length()
                if average_cycle_length:
                    predicted_start_date = last_end_date + timedelta(days=average_cycle_length)
                else:
                    predicted_start_date = last_end_date + timedelta(days=28)
                cursor.execute('''INSERT INTO predicted_start_date (predicted_date) VALUES (%s) 
                                ON DUPLICATE KEY UPDATE predicted_date = VALUES(predicted_date)''',
                               (predicted_start_date,))
                self.conn.commit()
                cursor.close()
                return predicted_start_date
        return None


    def get_last_period_length(self):
        print('Inside get_last_period_length method')
        if self.conn:
            with self.conn.cursor() as cursor:
                cursor.execute('''SELECT period_length FROM period_data ORDER BY id DESC LIMIT 1''')
                row = cursor.fetchone()
                if row:
                    return row[0]
        return None
    def get_last_cycle_length(self):
        print('Inside get_last_period_length method')
        if self.conn:
            with self.conn.cursor() as cursor:
                cursor.execute('''SELECT cycle_length FROM period_data ORDER BY id DESC LIMIT 1''')
                row = cursor.fetchone()
                if row:
                    return row[0]
        return None
    def update_home_page(self):
        print('Inside update_home_page method')
        average_cycle_length = self.calculate_average_cycle_length()
        predicted_start_date = self.calculate_predicted_start_date()
        home_screen = self.root.get_screen('home')

        if average_cycle_length is not None:
            home_screen.ids.cycle_info.text = f'Average Cycle Length:\n {average_cycle_length} days'
        else:
            home_screen.ids.cycle_info.text = 'Average Cycle Length: N/A'

        if predicted_start_date:
            home_screen.ids.prediction_info.text = f'Predicted Start Date:\n {predicted_start_date.strftime("%Y-%m-%d")}'
        else:
            home_screen.ids.prediction_info.text = 'Predicted Start Date: N/A'
            if len(self.get_period_data()) == 1:
                end_date = self.get_period_data()[0][2]
                predicted_start_date = end_date + timedelta(days=28)
                home_screen.ids.prediction_info.text = f'Predicted Start Date:\n {predicted_start_date.strftime("%Y-%m-%d")}'

        period_length = self.get_last_period_length()
        if period_length is not None:
            if period_length >= 7:
                home_screen.ids.medical_advice1.text = "Period is too long, seek medical advice!."
        cycle_length = self.get_last_cycle_length()
        if cycle_length is not None:
            if cycle_length < 21:
                home_screen.ids.medical_advice.text = "Cycle length is too low, seek medical advice!."
            elif cycle_length > 35:
                home_screen.ids.medical_advice.text = "Cycle length is too long, seek medical advice!."
            else:
                home_screen.ids.medical_advice.text = ''
        else:
            home_screen.ids.medical_advice.text = ''

        print('Exiting update_home_page method')

    def on_start(self):
        print('Inside on_start method')
        self.update_home_page()
        self.check_for_notification()
        print('Exiting on_start method')

    def create_db_table(self):
        print('Inside create_db_table method')
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="donkey123"
        )
        cursor = self.conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS period_tracker")
        cursor.execute("USE period_tracker")
        cursor.execute('''CREATE TABLE IF NOT EXISTS period_data
                     (id INT AUTO_INCREMENT PRIMARY KEY,
                      start_date DATE,
                      end_date DATE,
                      period_length INT,
                      cycle_length INT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS app_password
                         (id INT AUTO_INCREMENT PRIMARY KEY,
                          password VARCHAR(255))''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS predicted_start_date
                                 (id INT AUTO_INCREMENT PRIMARY KEY,
                                  predicted_date DATE)''')
        self.conn.commit()
        cursor.close()
        print('Exiting create_db_table method')

    def on_save(self, instance, value, date_range):
        print('Inside on_save method')
        start_date = date_range[0]
        end_date = date_range[-1]
        period_length = (end_date - start_date).days
        try:
            if self.conn:
                cursor = self.conn.cursor()
                cursor.execute('''INSERT INTO period_data (start_date, end_date, period_length) VALUES (%s, %s, %s)''',
                               (start_date, end_date, period_length))
                self.conn.commit()
                self.update_cycle_lengths(cursor)
                self.update_home_page()
        finally:
            cursor.close()  # Ensure cursor is closed even in case of exceptions
        home_screen = self.root.get_screen('home')
        home_screen.ids.date_label.text = f'Cycle dates: {start_date} - {end_date}'
        print('Exiting on_save method')

    def update_cycle_lengths(self, cursor):
        int('Inside update_cycle_lengths method')
        try:
            cursor.execute('''SELECT id, start_date, end_date FROM period_data ORDER BY id DESC LIMIT 2''')
            rows = cursor.fetchall()
            if len(rows) == 2:
                id1, start_date1, end_date1 = rows[1]
                id2, start_date2, end_date2 = rows[0]
                cycle_length = (start_date2 - end_date1).days
                cursor.execute('''UPDATE period_data SET cycle_length = %s WHERE id = %s''', (cycle_length, id2))
                self.conn.commit()
        finally:
            cursor.close()  # Ensure cursor is closed even in case of exceptions
        print('Exiting update_cycle_lengths method')

    def on_cancel(self, instance, value):
        print('Inside on_cancel method')
        home_screen = self.root.get_screen('home')
        home_screen.ids.date_label.text = "Cycle dates: Cancelled"
        print('Exiting on_cancel method')

    def show_date_picker(self):
        print('Inside show_date_picker method')
        date_dialog = MDDatePicker(mode='range')
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()
        print('Exiting show_date_picker method')

    def check_for_notification(self):
        predicted_start_date = self.calculate_predicted_start_date()
        current_date = datetime.now().date()

        # Calculate the date two days before the predicted start date
        notification_date = predicted_start_date - timedelta(days=2)

        print(f"Predicted start date: {predicted_start_date.strftime('%Y-%m-%d')}")
        print(f"Notification date: {notification_date.strftime('%Y-%m-%d')}")
        print(f"Current date: {current_date.strftime('%Y-%m-%d')}")

        # Check if the current date matches the notification date
        if current_date == notification_date:
            self.send_notification()

    def send_notification(self):
        # Logic to send notification
        print("Notification: Your period is predicted to start in 2 days.")
    def get_period_data(self):
        print('Inside get_period_data method')
        if self.conn:
            with self.conn.cursor() as cursor:
                cursor.execute('''SELECT * FROM period_data ORDER BY id DESC''')
                rows = cursor.fetchall()
                return rows
        return []
    
if __name__ == '__main__':
    MyApp().run()