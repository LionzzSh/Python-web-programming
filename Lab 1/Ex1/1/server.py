# Імпортуємо бібліотеки, необхідні для роботи з сокетами та часом
import socket
import time

# Створюємо серверний сокет
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Вказуємо адресу та порт, на якому сервер буде працювати
server_address = ('127.0.0.1', 8080)

# Зв'язуємо серверний сокет із вказаною адресою
server_socket.bind(server_address)

# Режим очікування підключень, може обслуговувати до 5 клієнтів одночасно
server_socket.listen(5)

# Виводимо повідомлення про те, що сервер працює та вказуємо адресу та порт
print("Сервер працює на: {}:{}".format(*server_address))

while True:
    # Приймаємо запит на підключення від клієнта
    client_socket, client_address = server_socket.accept()
    
    # Виводимо повідомлення про підключеного користувача та його адресу
    print("Під'єднався користувач: {}".format(client_address))

    # Очікуємо та приймаємо дані від клієнта (максимум 1024 байти)
    data = client_socket.recv(1024)

    # Якщо дані отримано, виводимо їх та час отримання
    if data:
        print("Отриманий текст: {}".format(data.decode('utf-8')))
        print("Час отримання: {}".format(time.ctime()))

    # Закриваємо сокет для даного клієнта
    client_socket.close()