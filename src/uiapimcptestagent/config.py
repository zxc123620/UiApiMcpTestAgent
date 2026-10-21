#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/10/5 10:10
# Author:zhouxiaochuan
# Description:
import os
from pathlib import Path

import dotenv

dotenv.load_dotenv()

current_dir_path = Path(".").resolve()
project_path = Path(__file__).resolve().parent
db_path =  Path(os.getenv("DB_PATH", (current_dir_path / "test_data.db").as_posix() ))
print(f"当前路径: {current_dir_path}")
print(f"项目路径: {project_path}")
print(f"数据库路径: {db_path}")
