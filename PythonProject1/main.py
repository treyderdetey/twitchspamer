import socket
import tkinter as tk
from tkinter import ttk, filedialog
from threading import Thread
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *


class TwitchBotGUI:
    def __init__(self, master):
        self.master = master
        master.title("Twitch Bot Manager")
        master.geometry("600x450")
        style = ttkb.Style(theme="darkly")

        self.accounts = []
        self.status_text = tk.StringVar()
        self.status_text.set("Готов к работе")

        # Основные фреймы
        main_frame = ttkb.Frame(master, padding=10)
        main_frame.pack(fill=BOTH, expand=True)

        # Панель управления
        control_frame = ttkb.Frame(main_frame)
        control_frame.pack(fill=X, pady=5)

        self.load_btn = ttkb.Button(
            control_frame,
            text="Загрузить аккаунты",
            command=self.load_accounts,
            bootstyle=SUCCESS
        )
        self.load_btn.pack(side=LEFT, padx=5)

        # Поле канала
        channel_frame = ttkb.LabelFrame(main_frame, text="Целевой канал", padding=10)
        channel_frame.pack(fill=X, pady=5)

        self.channel_entry = ttkb.Entry(channel_frame, width=30)
        self.channel_entry.pack(side=LEFT, padx=5)


        # Выбор аккаунта
        account_frame = ttkb.LabelFrame(main_frame, text="Аккаунт отправителя", padding=10)
        account_frame.pack(fill=X, pady=5)

        self.account_combo = ttkb.Combobox(account_frame, state="readonly", width=25)
        self.account_combo.pack(side=LEFT, padx=5)

        # Поле сообщения
        message_frame = ttkb.LabelFrame(main_frame, text="Сообщение", padding=10)
        message_frame.pack(fill=BOTH, expand=True, pady=5)

        self.message_text = tk.Text(message_frame, height=5, wrap=WORD)
        self.message_text.pack(fill=BOTH, expand=True)

        # Кнопка отправки
        self.send_btn = ttkb.Button(
            main_frame,
            text="Отправить сообщение",
            command=self.start_send_thread,
            bootstyle=PRIMARY
        )
        self.send_btn.pack(pady=10)

        # Кнопка отправки всем аккаунтам
        self.send_all_btn = ttkb.Button(
            main_frame,
            text="Отправить всем аккаунтам",
            command=self.start_send_all_thread,
            bootstyle=INFO
        )
        self.send_all_btn.pack(pady=5)

        # Статус бар
        self.status_bar = ttkb.Label(
            master,
            textvariable=self.status_text,
            bootstyle=(INFO, INVERSE),
            padding=5
        )
        self.status_bar.pack(fill=X, side=BOTTOM)

    def load_accounts(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if not file_path:
            return

        self.accounts.clear()
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            self.accounts.append({'nick': parts[0], 'token': parts[1]})

            self.account_combo['values'] = [acc['nick'] for acc in self.accounts]
            if self.accounts:
                self.account_combo.current(0)
                self.update_status(f"Загружено {len(self.accounts)} аккаунтов", "success")
        except Exception as e:
            self.update_status(f"Ошибка загрузки: {str(e)}", "danger")

    def start_send_thread(self):
        Thread(target=self.send_message, daemon=True).start()

    def start_send_all_thread(self):
        Thread(target=self.send_message_to_all, daemon=True).start()

    def update_status(self, message, style="info"):
        self.status_text.set(message)
        self.status_bar.configure(bootstyle=style)
        self.master.after(5000, lambda: self.status_text.set("Готов к работе"))

    def send_message(self):
        selected_nick = self.account_combo.get()
        channel = self.channel_entry.get().strip()
        message = self.message_text.get("1.0", tk.END).strip()

        if not selected_nick or not channel or not message:
            self.update_status("Заполните все поля!", "danger")
            return

        account = next((acc for acc in self.accounts if acc['nick'] == selected_nick), None)
        if not account:
            self.update_status("Аккаунт не найден", "danger")
            return

        try:
            sock = socket.socket()
            sock.connect(("irc.chat.twitch.tv", 6667))

            sock.send(f"PASS {account['token']}\r\n".encode())
            sock.send(f"NICK {account['nick']}\r\n".encode())

            channel = f"#{channel.lstrip('#')}"
            sock.send(f"JOIN {channel}\r\n".encode())

            sock.send(f"PRIVMSG {channel} :{message}\r\n".encode())

            response = sock.recv(2048).decode()
            print("Ответ сервера:", response)

            sock.close()
            self.update_status(f"Сообщение отправлено в {channel}!", "success")
            self.message_text.delete("1.0", END)
        except Exception as e:
            self.update_status(f"Ошибка: {str(e)}", "danger")

    def send_message_to_all(self):
        channel = self.channel_entry.get().strip()
        message = self.message_text.get("1.0", tk.END).strip()

        if not channel or not message:
            self.update_status("Заполните все поля!", "danger")
            return

        for account in self.accounts:
            try:
                sock = socket.socket()
                sock.connect(("irc.chat.twitch.tv", 6667))

                sock.send(f"PASS {account['token']}\r\n".encode())
                sock.send(f"NICK {account['nick']}\r\n".encode())

                channel_formatted = f"#{channel.lstrip('#')}"
                sock.send(f"JOIN {channel_formatted}\r\n".encode())

                sock.send(f"PRIVMSG {channel_formatted} :{message}\r\n".encode())

                response = sock.recv(2048).decode()
                print(f"Ответ сервера от {account['nick']}:", response)

                sock.close()
            except Exception as e:
                print(f"Ошибка при отправке от {account['nick']}: {str(e)}")

        self.update_status(f"Сообщение отправлено всем аккаунтам в {channel}!", "success")
        self.message_text.delete("1.0", END)


if __name__ == "__main__":
    app = ttkb.Window("darkly")
    TwitchBotGUI(app)
    app.mainloop()
