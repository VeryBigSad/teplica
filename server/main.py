from constants import HOSTNAME, PORT
from server import Server
from bot.bot import TeplicaBot
import os
from dotenv import load_dotenv



def main():
    load_dotenv()
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

    # start telegram bot in a separate thread
    bot = TeplicaBot(TELEGRAM_TOKEN)
    bot.start_polling_in_a_thread()

    # start server
    server = Server(HOSTNAME, PORT, "db.sqlite3")
    server.start_listening()

    while True:
        clientsocket, addr = server.wait_for_client()
        server.process_request(clientsocket, addr)


if __name__ == "__main__":
    main()

