
#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time: 2026/9/24 16:21
# Author:zhouxiaochuan
# Description:


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if "instance_id" in kwargs:
            instance_id = kwargs["instance_id"]
        else:
            instance_id = cls.__name__
        if instance_id not in cls._instances:
            cls._instances[instance_id] = super().__call__(*args, **kwargs)
        return cls._instances[instance_id]
