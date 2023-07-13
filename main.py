import config
from DataBase import DB
from bot_main import AphBot

def main():
    db = DB(config.DB_CONFIG['host'], config.DB_CONFIG['user'], config.DB_CONFIG['password'], config.DB_CONFIG['db'])
    bot = AphBot(config.BOT_TOKEN, db)
    bot.run()


if __name__ == "__main__":
    main()
