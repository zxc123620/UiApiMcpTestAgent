"""
API客户端基类
提供通用的HTTP请求方法，支持自动响应校验
"""
import json
import os
import time
import logging
import uuid
from typing import Dict, Optional, Type
from urllib.parse import urljoin


from pydantic import BaseModel, ValidationError
import requests
from requests.sessions import Session
from urllib3.exceptions import InsecureRequestWarning
from typing import Literal

# 获取logger
logger = logging.getLogger("api")

# 禁用SSL警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class BaseAPIClient:
    """API客户端基类"""

    def __init__(self,api_id:str,  base_url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 30):
        """
        初始化API客户端

        :param api_id: API ID
        :param base_url: 基础URL
        :param headers: 默认请求头
        :param timeout: 请求超时时间（秒）
        """
        self.api_id = api_id
        self.base_url = base_url
        self.session = Session()
        self.timeout = timeout

        # 设置默认请求头
        self.default_headers = {
            'Accept': 'application/json, text/plain, */*',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache'
        }
        
        if headers:
            self.default_headers.update(headers)
        
        self.session.headers.update(self.default_headers)
        

    def _build_url(self, endpoint: str) -> str:
        """
        构建完整的URL
        
        Args:
            endpoint: API端点路径
            
        Returns:
            完整的URL
        """
        if endpoint.startswith('http'):
            return endpoint
        return urljoin(self.base_url, endpoint)

    @staticmethod
    def _log_request(method: str, url: str, **kwargs):
        """记录请求日志"""
        logger.info(f"请求方法: {method} 请求URL: {url}")
        if 'json' in kwargs:
            logger.debug(f"请求体内容: {json.dumps(kwargs['json'], ensure_ascii=False)}")
        if 'headers' in kwargs:
            logger.debug(f"请求头信息: {kwargs['headers']}")
        if "params" in kwargs:
            logger.debug(f"请求参数: {kwargs['params']} 类型: {type(kwargs['params'])}")


    @staticmethod
    def _log_response(response: requests.Response):
        """记录响应日志"""
        logger.info(f"响应状态码: {response.status_code}")
        logger.debug(f"响应头信息: {dict(response.headers)}")
        try:
            logger.debug(f"响应体内容: {response.json()}")
        except requests.exceptions.JSONDecodeError:
            logger.warning("响应体不是JSON格式,不输出到日志中")
            # logger.debug(f"响应体内容: {response.text}")

    def request(self, method: Literal["GET", "POST", "PUT", "DELETE"],  endpoint: str,
                expected_status_code: int = 200,
                response_model: Optional[Type[BaseModel]] = None,
                **kwargs):
        """
        发送HTTP请求并自动校验响应
        
        Args:
            method: HTTP方法 (GET, POST, PUT, DELETE, etc.)
            endpoint: API端点
            expected_status_code: 期望的HTTP状态码，默认200
            response_model: Pydantic模型类，用于校验响应数据
            **kwargs: 请求参数
            
        Returns:

        Raises:
            AssertionError: 当状态码或响应数据不符合预期时
        """
        url = self._build_url(endpoint)
        
        # 合并headers
        if 'headers' in kwargs:
            headers = self.default_headers.copy()
            headers.update(kwargs['headers'])
            kwargs['headers'] = headers
        else:
            kwargs['headers'] = self.default_headers.copy()
        
        # 设置默认timeout
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        
        # 记录请求
        self._log_request(method.upper(), url, **kwargs)
        
        # 发送请求
        start_time = time.time()
        response = self.session.request(method, url, verify=False, **kwargs)
        elapsed_time = time.time() - start_time
        
        # 记录响应
        self._log_response(response)
        logger.info(f"请求总共耗时: {elapsed_time:.2f}s")
        
        # 自动校验状态码
        if response.status_code != expected_status_code:
            error_msg = f"状态码不匹配: expected {expected_status_code}, got {response.status_code}"
            logger.error(error_msg)
            # try:
            #     logger.error(f"响应体: {response.json()}")
            # except requests.exceptions.JSONDecodeError:
            #     logger.error(f"响应体: {response.text}")
            raise AssertionError(error_msg)
        
        # 自动校验响应数据
        if response_model and response.status_code == 200:
            try:
                response_data = response.json()
                validated = response_model(**response_data)
                logger.info(f"响应体校验通过模型验证: {response_model.__name__}")
                # 将验证后的数据附加到response对象上
                response.validated_data = validated
            except ValidationError  as e:
                logger.error(f"响应体校验失败: {e}")
                raise
            except requests.exceptions.JSONDecodeError as e:
                logger.error(f"响应体不是JSON格式: {e}")
                logger.info(f"响应体内容: {response.text}")
                raise

        
        return response
    def get(self, endpoint: str, params: Optional[Dict] = None,
            expected_status_code: int = 200,
            response_model: Optional[Type[BaseModel]] = None,
            **kwargs) -> requests.Response:
        """发送GET请求"""
        return self.request('GET', endpoint, params=params, 
                          expected_status_code=expected_status_code,
                          response_model=response_model, **kwargs)

    def post(self, endpoint: str, json: Optional[Dict] = None,
             expected_status_code: int = 200,
             response_model: Optional[Type[BaseModel]] = None,
             **kwargs) -> requests.Response:
        """发送POST请求"""
        return self.request('POST', endpoint, json=json,
                          expected_status_code=expected_status_code,
                          response_model=response_model, **kwargs)

    def put(self, endpoint: str, json: Optional[Dict] = None,
            expected_status_code: int = 200,
            response_model: Optional[Type[BaseModel]] = None,
            **kwargs) -> requests.Response:
        """发送PUT请求"""
        return self.request('PUT', endpoint, json=json,
                          expected_status_code=expected_status_code,
                          response_model=response_model, **kwargs)

    def delete(self, endpoint: str, expected_status_code: int = 200, **kwargs) -> requests.Response:
        """发送DELETE请求"""
        return self.request('DELETE', endpoint, expected_status_code=expected_status_code, **kwargs)

    def patch(self, endpoint: str, json: Optional[Dict] = None,
              expected_status_code: int = 200,
              response_model: Optional[Type[BaseModel]] = None,
              **kwargs) -> requests.Response:
        """发送PATCH请求"""
        return self.request('PATCH', endpoint, json=json,
                          expected_status_code=expected_status_code,
                          response_model=response_model, **kwargs)

    def set_header(self, key: str, value: str):
        """设置请求头"""
        self.default_headers[key] = value
        logger.debug(f"Header set: {key}={value}")

    def remove_header(self, key: str):
        """移除请求头"""
        if key in self.default_headers:
            del self.default_headers[key]
            logger.debug(f"Header removed: {key}")

    def set_auth_token(self, token: str, token_type: str = "Bearer"):
        """设置认证Token"""
        self.set_header('Authorization', f'{token_type} {token}')
        logger.info("设置认证Token成功")

    def close(self):
        """关闭会话"""
        self.session.close()
        logger.info("关闭会话")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    #
    # @staticmethod
    # def get_multiple_api_clients(project_name_list: list[str]):
    #     """
    #     获取多个API客户端实例
    #
    #     :param project_name_list: 项目名称列表
    #     :return: API客户端实例列表
    #     """
    #     clients = {}
    #     for project_name in project_name_list:
    #         client = APIClientService.get_api_client(project_name)
    #         clients[client.api_id] = client
    #     return clients
