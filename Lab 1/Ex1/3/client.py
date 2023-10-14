# Імпортуємо бібліотеку для роботи з сокетами
import socket

# Створюємо клієнтський сокет
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Вказуємо адресу та порт сервера, до якого будемо підключатися
server_address = ('127.0.0.1', 8080)

# Встановлюємо з'єднання із сервером за вказаною адресою та портом
client_socket.connect(server_address)

while True:
    # Запитуємо користувача про текст для відправки на сервер
    message = input("Введіть текст для відправки на сервер (або 'exit' для завершення): ")
    
    # Надсилаємо повідомлення на сервер, закодоване у байти, використовуючи UTF-8
    client_socket.send(message.encode('utf-8'))

    # Якщо користувач ввів "exit", виходимо з циклу та завершуємо чат
    if message.lower() == 'exit':
        print('Ви покинули чат')
        break

# Закриваємо клієнтський сокет
client_socket.close()
