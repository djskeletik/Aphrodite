from config import DB_CONFIG
from DataBase import DB


def main():
    db = DB(DB_CONFIG['host'], DB_CONFIG['user'], DB_CONFIG['password'], DB_CONFIG['db'])


if __name__ == "__main__":
    main()
