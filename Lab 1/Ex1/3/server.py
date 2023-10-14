# Імпортуємо бібліотеки для роботи з сокетами, потоками та часом
import socket
import threading
import time

# Функція для обробки клієнта
def handle_client(client_socket, client_address):
    print(f"З'єднання від клієнта {client_address}")

    while True:
        # Очікуємо та приймаємо дані від клієнта (максимум 1024 байти)
        data = client_socket.recv(1024)
        if not data:
            break
        message = data.decode('utf-8')
        print(f"Повідомлення від клієнта {client_address}: {message}")
        print("Час отримання: {}".format(time.ctime()))

        # Якщо клієнт відправив "exit", виходимо з циклу обробки клієнта
        if message.strip().lower() == 'exit':
            print(f"Клієнт {client_address} покинув чат")
            break

    # Закриваємо з'єднання з клієнтом
    client_socket.close()

# Створюємо серверний сокет
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Вказуємо адресу та порт, на якому сервер буде працювати
server_address = ('127.0.0.1', 8080)

# Зв'язуємо серверний сокет із вказаною адресою
server_socket.bind(server_address)

# Режим очікування підключень, може обслуговувати до 5 клієнтів одночасно
server_socket.listen(5)

# Виводимо повідомлення про те, що сервер працює на вказаній адресі та порту
print("Сервер працює на {}:{}".format(*server_address))

while True:
    # Приймаємо запит на підключення від клієнта
    client_socket, client_address = server_socket.accept()

    # Створюємо окремий потік для обробки клієнта
    client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_handler.start()
