import configparser
import sys
from pathlib import Path
from time import sleep

import yaml

from config.settings import DEFAULT_CONFIG

APP_BASEPATH = Path(__file__).resolve(strict=True).parents[1]
LAST_DATA = Path(DEFAULT_CONFIG['CONFIG_DIR'], DEFAULT_CONFIG['LAST_DATA'])


def get_config(configfile: Path) -> configparser.ConfigParser:
    """
    Load configuration file with INI structure,
    return configparser object with content of configuration file

    configfile: relative path to app folder
    """
    inifile = APP_BASEPATH.joinpath(configfile)
    with open(inifile, mode='r', encoding='utf-8') as f:
        config = configparser.ConfigParser()
        print(f"Loading '{inifile}' was success.")
        sleep(1)
        config.read_file(f)

    return config


def read_yaml(configfile) -> dict:
    yamlfile = APP_BASEPATH.joinpath(configfile)

    with open(yamlfile, mode='r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

        if not isinstance(data, dict):
            sys.exit(f"'{yamlfile}' is not made with dictionary structure")

        print(f"Loading '{yamlfile}' was success.")
        sleep(1)
        return data


def write_to_yaml(data, yamlfile):
    """Write new data to exist file.

    Parameters:
    data - dictionary
    file - string or pathlib object
    """
    filepath = APP_BASEPATH.joinpath(yamlfile)

    with open(filepath, mode='w', encoding='UTF-8') as f:
        yaml.safe_dump(data, stream=f, allow_unicode=True)
        print(f"Data was written to '{filepath}'")
        sleep(1)




