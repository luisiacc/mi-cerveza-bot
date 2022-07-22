from configparser import ConfigParser

configuration_path = "../config.ini"


def get_config():
    parser = ConfigParser()
    parser.read(configuration_path)
    return {"token": parser.get("DEFAULT", "token")}
