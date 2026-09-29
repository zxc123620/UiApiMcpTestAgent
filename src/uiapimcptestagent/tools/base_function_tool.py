#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time:2026/6/7 17:59
# Author:zhouxiaochuan
# Description: 函数助手
import datetime
import random
import string
import uuid
import hashlib
import base64

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5, DES
from Crypto.Util.Padding import pad

from uiapimcptestagent.db.process.string_method_executor import StringMethodExecutor


class BaseFunctionTool:
    """函数助手"""

    @staticmethod
    @StringMethodExecutor.register("get_random_str")
    def get_random_str(data: str = None, length: int = 8) -> str:
        """
        获取随机字符串
        :param data: 数据源 默认为字母和数字
        :param length: 字符串长度
        :return: 随机字符串
        """
        data = data if data else string.ascii_letters + string.digits
        return ''.join(random.choices(data, k=length))

    @staticmethod
    @StringMethodExecutor.register("get_random_int")
    def get_random_int(length: int = 8) -> int:
        """
        获取随机整数
        :param length: 整数长度
        :return: 随机整数
        """
        return int(''.join(random.choices(string.digits, k=length)))

    @staticmethod
    @StringMethodExecutor.register("get_uuid")
    def get_uuid() -> str:
        """
        获取uuid
        :return: uuid
        """
        return str(uuid.uuid1().hex)

    @staticmethod
    @StringMethodExecutor.register("get_datetime")
    def get_datetime() -> str:
        """
        获取当前时间
        :return: 当前时间
        """
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    @StringMethodExecutor.register("md5_encrypt")
    def md5_encrypt(data: str) -> str:
        """
        md5加密
        :param data: 数据
        :return: md5加密后的数据
        """
        return hashlib.md5(data.encode()).hexdigest()


    @staticmethod
    @StringMethodExecutor.register("des_encrypt")
    def des_encrypt(data: str):
        """
        des加密
        :param data: 数据
        :return: des加密后的数据
        """
        # data = data.encode("utf-8")
        # des = DES.new(key=b"12345678", iv=b'\x00' * 8, mode=DES.MODE_CBC)
        # padded_data = pad(data, DES.block_size)
        # cipher_data = des.encrypt(padded_data)
        pad_str = "pkcs7"  # pkcs7 iso10126 none zeroes
        key = "12345678"  # key AES-16/24/32byte DES-8byte 3DES-8/16/24byte
        # 加密
        cipher = DES.new(key=key.encode("utf-8"),mode=DES.MODE_ECB)
        # 填充数据（除了CTR模式不需要填充）
        padded_data = pad(data.encode('utf-8'), cipher.block_size, style=pad_str)
        _encrypted = cipher.encrypt(padded_data)
        result = base64.b64encode(_encrypted).decode('utf-8')

        return result

    # ========== 生成 RSA 密钥对 ==========
    @staticmethod
    @StringMethodExecutor.register("generate_rsa_keys")
    def generate_rsa_keys():
        """生成 RSA 密钥对"""
        key = RSA.generate(2048)
        _private_key = key.export_key().decode('utf-8')
        _public_key = key.publickey().export_key().decode('utf-8')
        return _private_key, _public_key


    # ========== RSA + Base64 加密 ==========
    @staticmethod
    @StringMethodExecutor.register("rsa_encrypt")
    def rsa_encrypt(data: str, public_key: str) -> str:
        """
        RSA 加密 + Base64 编码

        Args:
            data: 要加密的原始字符串
            public_key: RSA 公钥（PEM格式）

        Returns:
            Base64 编码后的密文字符串
        """
        # 1. 导入公钥
        rsa_key = RSA.import_key(public_key)
        cipher = PKCS1_v1_5.new(rsa_key)

        # 2. 加密（需要将字符串转为字节）
        plaintext = data.encode('utf-8')
        ciphertext = cipher.encrypt(plaintext)

        # 3. Base64 编码
        encrypted_b64 = base64.b64encode(ciphertext).decode('utf-8')

        return encrypted_b64


    # ========== Base64 解码 + RSA 解密 ==========
    @staticmethod
    @StringMethodExecutor.register("rsa_decrypt")
    def rsa_decrypt(encrypted_b64: str, private_key: str) -> str:
        """
        Base64 解码 + RSA 解密

        Args:
            encrypted_b64: Base64 编码的密文
            private_key: RSA 私钥（PEM格式）

        Returns:
            解密后的原始字符串
        """
        # 1. Base64 解码
        ciphertext = base64.b64decode(encrypted_b64)

        # 2. 导入私钥并解密
        rsa_key = RSA.import_key(private_key)
        cipher = PKCS1_v1_5.new(rsa_key)

        # 3. 解密（需要指定块大小）
        plaintext = cipher.decrypt(ciphertext, None)

        return plaintext.decode('utf-8')

    # @staticmethod
    # @StringMethodExecutor.register("get_image_code")
    # def get_image_code(image_bytes: bytes) -> str:
    #     """
    #     获取图片验证码
    #     :param image_bytes: 图片字节流
    #     :return: 图片验证码
    #     """
    #     captcha_text = ocr.classification(image_bytes)
    #     logging.info(f"识别到图片验证码:{captcha_text}")
    #     return captcha_text

    @staticmethod
    @StringMethodExecutor.register("random_hex_color")
    def random_hex_color() -> str:
        """
        获取随机十六进制颜色
        :return: 随机十六进制颜色
        """
        return f"#{random.randint(0, 0xFFFFFF):06X}"
    #
    # @staticmethod
    # def data_convert(data_raw:str=None):
    #     """
    #     数据转换
    #     :param data_raw: 原始数据
    #     :return: 转换后的数据
    #     """
    #     logging.info(f"转换数据:{data_raw}")
    #     if data_raw is None:
    #         return data_raw
    #     def replace_params(match):
    #         param_name = match.group(1)
    #         if param_name in ["1", "2"]:
    #             return "12345"
    #         else:
    #             return "hhh"
    #     data_re = re.sub(r"\$\{(.*?)}", replace_params, data_raw)
    #     logging.info(f"转换完成后:{data_re}")
    #     return data_re

