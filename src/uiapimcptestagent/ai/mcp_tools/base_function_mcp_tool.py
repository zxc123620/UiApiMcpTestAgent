#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Time:2026/6/7 17:59
# Author:zhouxiaochuan
# Description: 函数助手
import datetime
import logging
import random
import string
import uuid
import hashlib
import base64

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5, DES
from Crypto.Util.Padding import pad
from fastmcp.tools import tool

from uiapimcptestagent.apps import csrd_api_mcp
from uiapimcptestagent.tools.base_function_tool import BaseFunctionTool


class BaseFunctionMcpTool:
    """函数助手"""
    @tool()
    def get_random_str(self, data: str = None, length: int = 8) -> str:
        """
        获取随机长度的字符串数据
        Args:
            data: 自定义数据内容
            length: 长度

        Returns:

        """
        return BaseFunctionTool.get_random_str(data, length)


    @tool()
    def get_random_int(self, length: int = 8) -> int:
        """
        获取随机长度的整数数据
        Args:
            length: 长度

        Returns:

        """
        return BaseFunctionTool.get_random_int(length)

    @tool()
    def get_uuid(self) -> str:
        """
        获取uuid
        :return: uuid
        """
        return BaseFunctionTool.get_uuid()

    @tool()
    def get_datetime(self) -> str:
        """
        获取当前时间
        :return: 当前时间
        """
        return BaseFunctionTool.get_datetime()

    @tool()
    def md5_encrypt(self, data: str) -> str:
        """
        md5加密
        :param data: 数据
        :return: md5加密后的数据
        """
        return BaseFunctionTool.md5_encrypt(data)

    @tool()
    def des_encrypt(self, data: str):
        """
        des加密
        :param data: 数据
        :return: des加密后的数据
        """
        # data = data.encode("utf-8")
        # des = DES.new(key=b"12345678", iv=b'\x00' * 8, mode=DES.MODE_CBC)
        # padded_data = pad(data, DES.block_size)
        # cipher_data = des.encrypt(padded_data)
        return BaseFunctionTool.des_encrypt(data)

    @tool()
    def generate_rsa_keys(self):
        """生成 RSA 密钥对"""
        return BaseFunctionTool.generate_rsa_keys()



    @tool()
    def rsa_encrypt(self, data: str, public_key: str) -> str:
        """
        RSA 加密 + Base64 编码

        Args:
            data: 要加密的原始字符串
            public_key: RSA 公钥（PEM格式）

        Returns:
            Base64 编码后的密文字符串
        """
        return BaseFunctionTool.rsa_encrypt(data, public_key)



    @tool()
    def rsa_decrypt(self, encrypted_b64: str, private_key: str) -> str:
        """
        Base64 解码 + RSA 解密

        Args:
            encrypted_b64: Base64 编码的密文
            private_key: RSA 私钥（PEM格式）

        Returns:
            解密后的原始字符串
        """
        return BaseFunctionTool.rsa_decrypt(encrypted_b64, private_key)

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

    @tool()
    def random_hex_color(self) -> str:
        """
        获取随机十六进制颜色
        :return: 随机十六进制颜色
        """
        return BaseFunctionTool.random_hex_color()


base_function_tool = BaseFunctionMcpTool()
csrd_api_mcp.add_tool(base_function_tool.get_random_str)
csrd_api_mcp.add_tool(base_function_tool.get_random_int)
csrd_api_mcp.add_tool(base_function_tool.get_uuid)
csrd_api_mcp.add_tool(base_function_tool.get_datetime)
csrd_api_mcp.add_tool(base_function_tool.des_encrypt)
csrd_api_mcp.add_tool(base_function_tool.generate_rsa_keys)
csrd_api_mcp.add_tool(base_function_tool.rsa_encrypt)
csrd_api_mcp.add_tool(base_function_tool.rsa_decrypt)
csrd_api_mcp.add_tool(base_function_tool.md5_encrypt)
csrd_api_mcp.add_tool(base_function_tool.random_hex_color)




