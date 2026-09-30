"""
API测试断言助手
提供常用的断言方法
"""
import copy
import json
import logging
import warnings
from typing import Dict, Any, Union
import allure
import jsonpath
import requests

from uiapimcptestagent.assertion.assertion_errors import ProjectAssertionError

logger = logging.getLogger("api")


class APIAssertionTools:
    """API断言工具类"""

    @classmethod
    @allure.step("获取响应JSON数据")
    def get_resp_json(cls,response: requests.Response) -> Dict[str, Any]:
        """
        获取响应的JSON数据
        :param response: requests.Response对象
        :return: JSON数据字典
        """
        try:
            data = response.json()
        except Exception as e:
            raise ProjectAssertionError(f"无法解析JSON响应: {e}")
        return data

    @staticmethod
    @allure.step("验证状态码")
    def assert_status_code(response, expected_code: int):
        """
        验证HTTP状态码
        
        Args:
            response: requests.Response对象
            expected_code: 期望的状态码
        """
        warnings.warn(
            "已过时,发起请求时自动校验状态码",
            DeprecationWarning,  # 或 PendingDeprecationWarning
            stacklevel=2  # 让警告指向调用者，而不是这一行
        )
        actual_code = response.status_code
        assert actual_code == expected_code, \
            f"Status code mismatch: expected {expected_code}, got {actual_code}"
        logger.info(f"Status code verified: {actual_code}")

    @staticmethod
    @allure.step("验证响应时间")
    def assert_response_time(response, max_time: float = 5.0):
        """
        验证响应时间
        
        Args:
            response: requests.Response对象
            max_time: 最大允许响应时间（秒）
        """
        elapsed = response.elapsed.total_seconds()
        assert elapsed <= max_time, \
            f"Response time too slow: {elapsed:.2f}s > {max_time}s"
        logger.info(f"Response time verified: {elapsed:.2f}s")

    @classmethod
    def assert_data_field(cls, expected_data: Any, actual_data: Any):
        """
        递归验证字典字段值
        :param expected_data: 期望的数据
        :param actual_data: 实际的数据
        :return: None
        """
        # 如果指定了期望值，进行验证
        if isinstance(expected_data, (str, int, float, bool)):
            # 常量值验证
            assert actual_data == expected_data, f"值不匹配: 期望值 {expected_data}, 实际值 {actual_data}"
        elif isinstance(expected_data, list):
            # 列表值验证
            assert isinstance(actual_data, list), f" '{actual_data}' 的值不是列表"
            assert actual_data.sort() == expected_data.sort(), f"值不匹配: 期望值 {expected_data}, 实际值 {actual_data}"
        elif isinstance(expected_data, dict):
            assert isinstance(actual_data, dict), f" '{actual_data}' 的值不是字典"
            # 预期是一个字典,但是实际上一个字典
            for key, value in expected_data.items():
                # 递归验证字段
                assert key in actual_data.keys(), f"字段 '{actual_data}'缺少键 {key}"
                cls.assert_data_field(expected_data=value, actual_data=actual_data[key])

    @classmethod
    @allure.step("验证响应指定字段数据中有没有预期的字段值")
    def assert_response_field(cls, response, field_path: str, expected_value: Any = None):
        """
        验证响应中的字段值,和jsonpath验证差不多（常用）
        Args:
            response: requests.Response对象
            field_path: 字段路径，支持嵌套，如 "data.id", 如果为""表示验证根字段
            expected_value: 期望的值，如果为None则只检查字段存在性。如果field_path解析后是一个列表,则挨个验证列表中的每个子元素,有一个匹配则通过
        """
        # 获取响应JSON数据
        data = cls.get_resp_json(response)
        # 解析字段路径
        field_path = field_path.replace(" ", "")
        field_keys_list = field_path.split('.') if field_path else []
        actual_res_value = data

        for field in field_keys_list:
            if field not in actual_res_value:
                raise ProjectAssertionError(f"字段 '{field_path}' 不存在于响应中")
            actual_res_value = actual_res_value[field]

        if expected_value is None:
            # 仅验证字段存在性
            return actual_res_value
        # 验证字段值
        if isinstance(actual_res_value, list):
            # 实际结果是一个列表
            is_pass = True
            for item in actual_res_value:
                try:
                    cls.assert_data_field(expected_data=expected_value, actual_data=item)
                    is_pass = True
                    break
                except ProjectAssertionError as e:
                    is_pass = False
                    logger.error(e)
            assert is_pass, f"字段 '{field_path}' 值不匹配: 预期 {expected_value}, 实际 {actual_res_value}"
        else:
            # 实际结果是其他类型
            cls.assert_data_field(expected_data=expected_value, actual_data=actual_res_value)
        logger.info(f"字段 '{field_path}' 验证通过: {actual_res_value}")
        return actual_res_value

    @classmethod
    def loop_validate_contains_dict(cls, actual_data_dict: dict, expected_dict: dict):
        """
        递归验证字典字段值,直到到最底层
        :param actual_data_dict: 实际的数据字典
        :param expected_dict: 期望的字典
        :return: bool
        """
        try:
            # 本级别验证字段
            cls.assert_data_field(expected_data=expected_dict, actual_data=actual_data_dict)
            # 验证通过
            return True
        except AssertionError:
            # 当前层级不匹配，继续查找子项
            pass
        # 没有验证通过，继续递归验证子项
        for data_key, data_value in actual_data_dict.items():
            if isinstance(data_value, dict):
                # 如果data_dict字典里面有一项的值里面是字典，则递归验证
                if cls.loop_validate_contains_dict(data_value, expected_dict):
                    return True
            elif isinstance(data_value, list):
                # 如果data_dict字典里面有一项的值里面是列表，则挨个验证列表中的每个子元素
                for item in data_value:
                    if isinstance(item, dict):
                        # 列表中每一项都是字典，递归验证
                        if cls.loop_validate_contains_dict(item, expected_dict):
                            return True
        return False

    @classmethod
    @allure.step("验证响应包含预期字典")
    def res_contains_data(cls, response, expected_dict: dict, ctx):
        """
        递归验证预期的值,直到到最底层
        Args:
            response: requests.Response对象
            expected_dict: 期望的字典
            ctx: 上下文信息，包含路径等信息
        """
        if isinstance(response, requests.Response):
            data = cls.get_resp_json(response)
        else:
            data = response
        assert cls.loop_validate_contains_dict(data, expected_dict), f"验证失败: 响应中的数据没有匹配到{expected_dict}"

    @classmethod
    @allure.step("使用jsonpath验证响应包含预期字典")
    def assert_response_jsonpath_contains_dict(cls, response, path: str, expected_dict: dict):
        """
        使用jsonpath验证预期的值
        Args:
            response: requests.Response对象
            path: jsonpath路径
            expected_dict: 期望的字典
        """
        data = cls.get_resp_json(response)
        result = jsonpath.jsonpath(data, path)
        if not result:
            assert False, f"验证失败: {data} 中没有提取到{expected_dict}"
        # 提取到了
        result = result[0]
        cls.assert_data_field(expected_data=expected_dict, actual_data=result)

    @staticmethod
    @allure.step("验证响应包含字段")
    def assert_response_has_fields(response, fields: list):
        """
        验证响应中包含指定的字段
        
        Args:
            response: requests.Response对象
            fields: 需要验证的字段列表
        """
        warnings.warn(
            "已过时,使用pydantic模型自行校验数据结构",
            DeprecationWarning,  # 或 PendingDeprecationWarning
            stacklevel=2  # 让警告指向调用者，而不是这一行
        )
        try:
            data = response.json()
        except Exception as e:
            raise ProjectAssertionError(f"Failed to parse JSON response: {e}")

        missing_fields = []
        for field in fields:
            keys = field.split('.')
            value = data

            field_exists = True
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    field_exists = False
                    break

            if not field_exists:
                missing_fields.append(field)

        assert not missing_fields, \
            f"Missing fields in response: {missing_fields}"

        logger.info(f"All required fields present: {fields}")

    @staticmethod
    @allure.step("验证响应数据结构")
    def assert_response_structure(response, expected_structure: Dict[str, type]):
        """
        验证响应的数据结构
        
        Args:
            response: requests.Response对象
            expected_structure: 期望的字段类型字典，如 {"id": int, "name": str}
        """
        warnings.warn(
            "已过时,使用pydantic模型自行校验数据结构",
            DeprecationWarning,  # 或 PendingDeprecationWarning
            stacklevel=2  # 让警告指向调用者，而不是这一行
        )
        try:
            data = response.json()
        except Exception as e:
            raise ProjectAssertionError(f"Failed to parse JSON response: {e}")

        type_errors = []
        for field, expected_type in expected_structure.items():
            if field not in data:
                type_errors.append(f"Field '{field}' not found")
            elif not isinstance(data[field], expected_type):
                type_errors.append(
                    f"Field '{field}' type mismatch: expected {expected_type.__name__}, "
                    f"got {type(data[field]).__name__}"
                )

        assert not type_errors, \
            f"Structure validation failed: {'; '.join(type_errors)}"

        logger.info(f"Response structure verified")

    @classmethod
    @allure.step("验证业务状态码")
    def assert_business_code(cls, response, expected_code: Union[int, str] = 200,
                             code_field: str = "code"):
        """
        验证业务状态码（API返回的业务代码）
        
        Args:
            response: requests.Response对象
            expected_code: 期望的业务状态码
            code_field: 业务状态码字段名，默认为"code"
        """
        data = cls.get_resp_json(response)
        actual_code = data.get(code_field)
        assert actual_code == expected_code, \
            f"Business code mismatch: expected {expected_code}, got {actual_code}"

        logger.info(f"Business code verified: {actual_code}")

    @staticmethod
    @allure.step("验证错误响应")
    def assert_error_response(response, expected_status_codes: list = None):
        """
        验证错误响应
        
        Args:
            response: requests.Response对象
            expected_status_codes: 期望的错误状态码列表，默认[400, 401, 403, 404, 500]
        """
        warnings.warn(
            "过时,在发送请求时自行设置预期的状态码",
            DeprecationWarning,  # 或 PendingDeprecationWarning
            stacklevel=2  # 让警告指向调用者，而不是这一行
        )
        if expected_status_codes is None:
            expected_status_codes = [400, 401, 403, 404, 500]

        assert response.status_code in expected_status_codes, \
            f"Expected error status code in {expected_status_codes}, got {response.status_code}"

        logger.info(f"Error response verified: {response.status_code}")

    @staticmethod
    @allure.step("验证响应消息")
    def assert_response_message(response, expected_message: str = None,
                                message_field: str = "message"):
        """
        验证响应消息
        
        Args:
            response: requests.Response对象
            expected_message: 期望的消息内容，如果为None则只检查消息字段存在
            message_field: 消息字段名
        """
        warnings.warn(
            "后续统一用jsonpath来校验",
            DeprecationWarning,  # 或 PendingDeprecationWarning
            stacklevel=2  # 让警告指向调用者，而不是这一行
        )
        try:
            data = response.json()
        except Exception as e:
            raise ProjectAssertionError(f"Failed to parse JSON response: {e}")

        message = data.get(message_field)
        assert message is not None, f"Message field '{message_field}' not found"

        if expected_message:
            assert message == expected_message, \
                f"Message mismatch: expected '{expected_message}', got '{message}'"

        logger.info(f"Message verified: {message}")
        return message

    @staticmethod
    @allure.step("验证列表响应")
    def assert_list_response(response, items_field: str = "data",
                             min_count: int = 0, max_count: int = None):
        """
        验证列表类型的响应
        
        Args:
            response: requests.Response对象
            items_field: 列表数据字段名
            min_count: 最小记录数
            max_count: 最大记录数
        """
        try:
            data = response.json()
        except Exception as e:
            raise ProjectAssertionError(f"Failed to parse JSON response: {e}")

        items = data.get(items_field, [])
        assert isinstance(items, list), f"Field '{items_field}' is not a list"

        count = len(items)
        assert count >= min_count, \
            f"List count {count} < minimum {min_count}"

        if max_count is not None:
            assert count <= max_count, \
                f"List count {count} > maximum {max_count}"

        logger.info(f"List response verified: {count} items")
        return items

    @staticmethod
    @allure.step("打印响应详情")
    def log_response_details(response, title: str = "API Response"):
        """
        记录响应详情到日志和Allure报告
        
        Args:
            response: requests.Response对象
            title: 标题
        """
        with allure.step(title):
            allure.attach(
                f"URL: {response.url}\n"
                f"Method: {response.request.method}\n"
                f"Status Code: {response.status_code}\n"
                f"Response Time: {response.elapsed.total_seconds():.2f}s\n"
                f"Headers: {json.dumps(dict(response.headers), indent=2, ensure_ascii=False)}\n"
                f"Body: {json.dumps(response.json(), indent=2, ensure_ascii=False) if response.headers.get('content-type', '').startswith('application/json') else response.text}",
                name="Response Details",
                attachment_type=allure.attachment_type.TEXT
            )

        logger.info(f"{title}: Status={response.status_code}, Time={response.elapsed.total_seconds():.2f}s")
