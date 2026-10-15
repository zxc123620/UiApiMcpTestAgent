#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/10/15 18:30
# Author:zhouxiaochuan
# Description:


import importlib
import pkgutil
import logging
from pathlib import Path

def auto_load_module(package_name: str = "models"):
    """
    自动加载指定包下的所有模块
    Args:
        package_name: 包名，默认值为"models"

    Returns:

    """
    package = importlib.import_module(package_name)
    package_path = Path(package.__file__ or "").parent

    for _, module_name, _ in pkgutil.walk_packages(
        [str(package_path)], prefix=f"{package_name}."
    ):
        try:
            importlib.import_module(module_name)
        except Exception as e:
            logging.error(f"导入模型模块 {module_name} 失败: {e}")