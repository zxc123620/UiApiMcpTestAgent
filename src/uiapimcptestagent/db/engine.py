#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/9/24 09:10
# Author:zhouxiaochuan
# Description:
from sqlalchemy import create_engine
db_engine = create_engine("sqlite:///test_data.db", echo=True)