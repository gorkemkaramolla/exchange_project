from tkinter import *
from tkinter import ttk
from db import db_instance
from datetime import datetime, timedelta
import requests
import json
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

class HomeScreen:
    def __init__(self, root, user, logout_callback):
        self.root = root
        self.user = user  
        self.logout_callback = logout_callback
        self.setup_ui()
        

    def setup_ui(self):
        self.root.title("Ana Ekran")
        self.root.geometry("800x600")


        logout_button = ttk.Button(self.root, text="Çıkış Yap", command=self.logout)
        logout_button.place(anchor='nw', relx=0, rely=0)


        self.menu_frame = ttk.Frame(self.root)
        self.menu_frame.place(anchor='ne', relx=1, rely=0)

        username_label = ttk.Label(self.menu_frame, text=self.user[1], font=('Helvetica', 14, 'bold'))
        username_label.pack(anchor='ne', padx=10, pady=5)

        container = ttk.Frame(self.root, padding=20)
        container.place(anchor='center', relx=0.5, rely=0.5)

        self.currency_var = StringVar()
        currency_label = ttk.Label(container, text="Para Birimi Seçin:")
        currency_label.pack(pady=5)
        self.currency_combobox = ttk.Combobox(container, textvariable=self.currency_var)
        self.currency_combobox['values'] = ('USD', 'EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'CNY', 'SEK', 'NZD', 'ALTIN(GRAM)')
        self.currency_combobox.pack(pady=5)

        self.amount_var = StringVar()
        amount_label = ttk.Label(container, text="Miktarı Girin:")
        amount_label.pack(pady=5)
        self.amount_entry = ttk.Entry(container, textvariable=self.amount_var)
        self.amount_entry.pack(pady=5)

        deposit_button = ttk.Button(container, text="Yatır", command=self.deposit)
        deposit_button.pack(pady=5)

        refresh_button = ttk.Button(container, text="Güncelle", command=self.refresh_rates)
        refresh_button.pack(pady=5)

        total_graph_button = ttk.Button(container, text="Toplam Grafiği Göster", command=self.show_graph)
        total_graph_button.pack(pady=5)

        self.display_user_funds()

    def get_exchange_rate(self, base_currency='USD', target_currency='TRY', force_update=False):
        if base_currency == 'ALTIN':
            db_instance.cursor.execute('SELECT rate, last_updated FROM exchange_rates WHERE base_currency = "ALTIN"')
            row = db_instance.cursor.fetchone()
            if row and not force_update:
                rate, last_updated = row
                last_updated = datetime.strptime(last_updated, '%Y-%m-%d %H:%M:%S')
                if datetime.now() - last_updated < timedelta(days=1):
                    return rate

            url = "https://api.collectapi.com/economy/goldPrice"
            headers = {
                'content-type': "application/json",
                'authorization': "apikey 1ZEyjOoTARN56ebsNrELhF:7MlpGbzG0m6Sj6OBm1EJ02"
            }
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    rate = float(data['result'][0]['buying'])  
                    db_instance.cursor.execute('REPLACE INTO exchange_rates (base_currency, target_currency, rate, last_updated) VALUES (?, ?, ?, ?)',
                                               ("ALTIN", "TRY", rate, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                    db_instance.conn.commit()
                    return rate
                else:
                    print(f"API yanıtında hata: {data}")
                    return 0
            else:
                print(f"Hata: {response.status_code} - {response.text}")
                return 0

        else:
            db_instance.cursor.execute('SELECT rate, last_updated FROM exchange_rates WHERE base_currency = ? AND target_currency = ?', (base_currency, target_currency))
            row = db_instance.cursor.fetchone()
            if row and not force_update:
                rate, last_updated = row
                last_updated = datetime.strptime(last_updated, '%Y-%m-%d %H:%M:%S')
                if datetime.now() - last_updated < timedelta(days=1):
                    return rate

            url = f"https://api.collectapi.com/economy/exchange?to={target_currency}&base={base_currency}"
            headers = {
                'content-type': "application/json",
                'authorization': "apikey 1ZEyjOoTARN56ebsNrELhF:7MlpGbzG0m6Sj6OBm1EJ02"
            }
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    rate = float(data['result']['data'][0]['calculated'])
                    db_instance.cursor.execute('REPLACE INTO exchange_rates (base_currency, target_currency, rate, last_updated) VALUES (?, ?, ?, ?)',
                                               (base_currency, target_currency, rate, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                    db_instance.conn.commit()
                    return rate
                else:
                    print(f"API yanıtında hata: {data}")
                    return 0
            else:
                print(f"Hata: {response.status_code} - {response.text}")
                return 0

    def display_user_funds(self):
        for widget in self.menu_frame.winfo_children():
            widget.pack_forget()

        username_label = ttk.Label(self.menu_frame, text=self.user[1], font=('Helvetica', 14, 'bold'))
        username_label.pack(anchor='ne', padx=10, pady=5)

        db_instance.cursor.execute('SELECT currency_amount, currency_type FROM user_funds WHERE user_id = ?', (self.user[0],))
        user_funds = db_instance.cursor.fetchall()

        self.user_funds_data = user_funds  

        total_try = 0
        profit_loss = self.calculate_profit_loss(user_funds)
        for fund in user_funds:
            amount, currency_type = fund
            exchange_rate = self.get_exchange_rate(currency_type, 'TRY')
            amount_in_try = amount * exchange_rate
            total_try += amount_in_try
            profit = profit_loss.get(currency_type, 0)
            balance_label = ttk.Label(self.menu_frame, text=f"{currency_type} = {amount} (≈ {amount_in_try:.2f} TRY, Kar/Zarar: {profit:.2f} TRY)", font=('Helvetica', 12))
            balance_label.pack(anchor='ne', padx=10, pady=5)
            currency_graph_button = ttk.Button(self.menu_frame, text=f"{currency_type} Grafiği Göster", command=lambda c=currency_type: self.show_currency_graph(c))
            currency_graph_button.pack(anchor='ne', padx=10, pady=5)

        total_label = ttk.Label(self.menu_frame, text=f"Toplam TRY: {total_try:.2f}", font=('Helvetica', 14, 'bold'))
        total_label.pack(anchor='ne', padx=10, pady=10)

        db_instance.cursor.execute('SELECT MAX(last_updated) FROM exchange_rates')
        last_updated = db_instance.cursor.fetchone()[0]
        if last_updated:
            last_updated_label = ttk.Label(self.menu_frame, text=f"Son Güncelleme: {last_updated}", font=('Helvetica', 10))
            last_updated_label.pack(anchor='ne', padx=10, pady=5)

    def deposit(self):
        currency = self.currency_var.get()
        amount = float(self.amount_var.get())
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db_instance.insert_transaction(self.user[0], amount, date, 'Yatırma', currency)
        self.display_user_funds()

    def fetch_data_for_graph(self):
        db_instance.cursor.execute('SELECT transaction_date, currency_amount, currency_type FROM transactions WHERE user_id = ?', (self.user[0],))
        transactions = db_instance.cursor.fetchall()

        db_instance.cursor.execute('SELECT rate, last_updated FROM exchange_rates WHERE target_currency = "TRY"')
        exchange_rates = db_instance.cursor.fetchall()
        return transactions, exchange_rates

    def match_rate(self, transaction_date, currency_type, exchange_rates):
        closest_rate = None
        min_time_diff = timedelta.max
        transaction_datetime = datetime.strptime(transaction_date, '%Y-%m-%d %H:%M:%S')
        for rate, last_updated in exchange_rates:
            rate_datetime = datetime.strptime(last_updated, '%Y-%m-%d %H:%M:%S')
            if abs(rate_datetime - transaction_datetime) < min_time_diff:
                min_time_diff = abs(rate_datetime - transaction_datetime)
                closest_rate = rate
        return closest_rate

    def filter_last_30_days(self, data):
        today = datetime.now().date()
        last_30_days = today - timedelta(days=30)
        return {date: value for date, value in data.items() if last_30_days <= date <= today}

    def calculate_profit_loss(self, user_funds):
        profit_loss = {}
        transactions, exchange_rates = self.fetch_data_for_graph()

        for transaction_date, amount, currency_type in transactions:
            rate_at_transaction = self.match_rate(transaction_date, currency_type, exchange_rates)
            if rate_at_transaction:
                initial_value_in_try = amount * rate_at_transaction
                current_rate = self.get_exchange_rate(currency_type, 'TRY')
                current_value_in_try = amount * current_rate
                profit_loss[currency_type] = profit_loss.get(currency_type, 0) + (current_value_in_try - initial_value_in_try)

        return profit_loss

    def refresh_rates(self):
        db_instance.cursor.execute('SELECT DISTINCT currency_type FROM user_funds WHERE user_id = ?', (self.user[0],))
        currencies = db_instance.cursor.fetchall()

        for currency, in currencies:
            self.get_exchange_rate(currency, 'TRY', force_update=True)

        self.display_user_funds()

    def show_graph(self):
        transactions, exchange_rates = self.fetch_data_for_graph()

        if not transactions:
            print("Hiç işlem bulunamadı.")
            return

        date_to_total_try = {}

        for transaction_date, amount, currency_type in transactions:
            rate = self.match_rate(transaction_date, currency_type, exchange_rates)
            if rate:
                value_in_try = amount * rate
                date = datetime.strptime(transaction_date, '%Y-%m-%d %H:%M:%S').date()
                if date not in date_to_total_try:
                    date_to_total_try[date] = 0
                date_to_total_try[date] += value_in_try
            else:
                print(f"{transaction_date} tarihinde işlem için kur bulunamadı")

        date_to_total_try = self.filter_last_30_days(date_to_total_try)

        sorted_dates = sorted(date_to_total_try.keys())
        total_values_in_try = [date_to_total_try[date] for date in sorted_dates]

        if sorted_dates and total_values_in_try:
            plt.figure(figsize=(10, 5))
            plt.plot(sorted_dates, total_values_in_try, marker='o', linestyle='-', color='red')
            plt.title('TRY Üzerinden Varlıkların Toplam Değeri (Son 30 Gün)')
            plt.xlabel('Tarih')
            plt.ylabel('TRY Değeri')
            plt.grid(True)
            plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
            plt.gca().set_xlim([sorted_dates[0], sorted_dates[-1]])  
            plt.gcf().autofmt_xdate()  
            plt.show()
        else:
            print("Hata: Tarih ve değer listelerinde uyumsuzluk veya kullanılabilir değer yok.")

    def show_currency_graph(self, currency_type):
        transactions, exchange_rates = self.fetch_data_for_graph()

        if not transactions:
            print("Hiç işlem bulunamadı.")
            return

        date_to_currency_try = {}

        for transaction_date, amount, trans_currency_type in transactions:
            if trans_currency_type == currency_type:
                rate = self.match_rate(transaction_date, trans_currency_type, exchange_rates)
                if rate:
                    value_in_try = amount * rate
                    date = datetime.strptime(transaction_date, '%Y-%m-%d %H:%M:%S').date()
                    if date not in date_to_currency_try:
                        date_to_currency_try[date] = 0
                    date_to_currency_try[date] += value_in_try
                else:
                    print(f"{transaction_date} tarihinde işlem için kur bulunamadı")

        date_to_currency_try = self.filter_last_30_days(date_to_currency_try)

        sorted_dates = sorted(date_to_currency_try.keys())
        currency_values_in_try = [date_to_currency_try[date] for date in sorted_dates]

        if sorted_dates and currency_values_in_try:
            plt.figure(figsize=(10, 5))
            plt.plot(sorted_dates, currency_values_in_try, marker='o', linestyle='-', color='blue')
            plt.title(f'{currency_type} Üzerinden Varlıkların TRY Değeri (Son 30 Gün)')
            plt.xlabel('Tarih')
            plt.ylabel('TRY Değeri')
            plt.grid(True)
            plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
            plt.gca().set_xlim([sorted_dates[0], sorted_dates[-1]])  
            plt.gcf().autofmt_xdate()  
            plt.show()
        else:
            print(f"Hata: {currency_type} için tarih ve değer listelerinde uyumsuzluk veya kullanılabilir değer yok.")

    def logout(self):
        self.logout_callback()
