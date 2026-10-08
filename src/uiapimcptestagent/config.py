#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/10/5 10:10
# Author:zhouxiaochuan
# Description:
from pathlib import Path

current_dir_path = Path(".").resolve()
project_path = Path(__file__).resolve().parent
print(f"当前路径: {current_dir_path}")
print(f"项目路径: {project_path}")
