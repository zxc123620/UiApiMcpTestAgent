import os
import logging.config

import dotenv

from uiapimcptestagent.config import current_dir_path, db_path
from uiapimcptestagent.db.engine import db_engine
from uiapimcptestagent.db.tables import Base
import logging

from uiapimcptestagent.tools.package_tool import auto_load_module


def init_env():
    """
    初始化环境变量
    :return:
    """
    dotenv.load_dotenv()

def init_logger_config():
    """
    初始化日志配置
    """
    log_dir_path = current_dir_path / "logs"
    if not log_dir_path.exists():
        log_dir_path.mkdir()
    log_config_data = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "format": "%(asctime)s|%(name)s|%(levelname)s|%(filename)s|%(lineno)d: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "simple",
                "stream": "ext://sys.stdout"
            },
            "info_file_handler": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "level": "INFO",
                "formatter": "simple",
                "interval": 1,
                "backupCount": 30,
                "filename": log_dir_path / "info.log",
                "when": "midnight",

                "encoding": "utf8"
            },
            "error_file_handler": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "level": "ERROR",
                "formatter": "simple",
                "filename": log_dir_path / "errors.log",
                "when": "midnight",
                "interval": 1,
                "backupCount": 30,
                "encoding": "utf8"
            },
            "debug_file_handler": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "level": "DEBUG",
                "formatter": "simple",
                "filename": log_dir_path / "debug.log",
                "when": "midnight",
                "interval": 1,
                "backupCount": 30,
                "encoding": "utf8"
            },
            "api_file_handler": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "level": "DEBUG",
                "formatter": "simple",
                "filename": log_dir_path / "api.log",
                "when": "midnight",
                "interval": 1,
                "backupCount": 30,
                "encoding": "utf8",

            }
        },
        "loggers": {
            "watchfiles": {"level": "WARNING"},
            "uvicorn": {"level": "INFO"},
            "uvicorn.access": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "fastapi": {"level": "INFO"},
            "api": {
                "level": os.getenv("LOG_LEVEL", "INFO"),
                "handlers": ["api_file_handler", "console"],
                "propagate": False,
            }
        },
        "root": {
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "handlers": ["console", "info_file_handler", "error_file_handler", "debug_file_handler"]
        }
    }
    logging.config.dictConfig(log_config_data)

def init_db_tables():
    """
    初始化数据库表
    Returns:

    """
    if not db_path.exists():
        Base.metadata.create_all(db_engine)
        logging.info("数据库表初始化完成")
    else:
        logging.info("数据库表已存在")


def init_api_res_models():
    """
    初始化API响应模型
    Returns:

    """
    package_name = os.getenv("API_RES_MODEL_PACKAGE_NAME", "models")
    auto_load_module(package_name)

init_env()
init_logger_config()
init_db_tables()
init_api_res_models()
