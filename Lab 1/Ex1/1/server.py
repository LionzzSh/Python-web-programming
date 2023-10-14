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