#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/9/24 09:10
# Author:zhouxiaochuan
# Description:
from sqlalchemy import create_engine

from uiapimcptestagent import current_dir_path

db_path = current_dir_path / "test_data.db"
db_engine = create_engine(f"sqlite:///{db_path}", echo=True)
