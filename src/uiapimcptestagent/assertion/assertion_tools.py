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

from uiapimcptestagent.ai.agents.test_assert_agent import TestAssertAgent
from uiapimcptestagent.ai.ai_res_model.test_assert_res_model import ApiTestAssertResModel
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
    @allure.step("AI判断言")
    def ai_judge(cls,  expected_data: Any, actual_data: Any):
        """
        使用AI判断预期值是否匹配实际值

        Args:
            expected_data: 期望的数据
            actual_data: 实际的数据

        Returns:

        """

        content = f"ai判断,预期结果: {expected_data}, 实际结果: {actual_data}"
        result = TestAssertAgent().invoke(content=content)
        logger.info(f"Ai判断言结果: {result["messages"][-1].content}, type: {type(result["messages"][-1].content)}")
        struct_res: ApiTestAssertResModel = ApiTestAssertResModel(**json.loads(result["messages"][-1].content))
        assert struct_res.pass_, f"AI断言失败: {struct_res.reason}"

    @classmethod
    def assert_data_field(cls, expected_data: Any, actual_data: Any):
        """
        递归验证字典字段值

        Args:
            expected_data: 期望的数据
            actual_data: 实际的数据

        Returns:

        """
        logger.info(f"验证字段值: {expected_data} -> {actual_data}")
        # 如果指定了期望值，进行验证
        if isinstance(expected_data, (str, int, float, bool)):
            # 常量值验证
            # if isinstance(expected_data, str ) and expected_data.lower().startswith("ai."):
            #     content = f"预期结果: {expected_data}, 实际结果: {actual_data}"
            #     result = TestAssertAgent().invoke(content=content)
            #     struct_res:ApiTestAssertResModel = result["structured_response"]
            #     assert struct_res.pass_, f"AI断言失败: {struct_res.reason}"
            # else:
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
                act_key = key
                ai_judge = False
                # 判断是否需要AI判断
                if isinstance(key ,str) and key.lower().startswith("ai."):
                    act_key = key[3:]
                    ai_judge = True
                # 验证字段是否存在
                assert act_key in actual_data.keys(), f"字段 '{actual_data}'缺少键 {act_key}"
                # 如果需要AI判断,则使用AI判断
                if ai_judge:
                    cls.ai_judge(expected_data=value, actual_data=actual_data[act_key])
                # 否则,递归验证字段值
                else:
                    cls.assert_data_field(expected_data=value, actual_data=actual_data[act_key])

    @classmethod
    def loop_validate_contains_dict(cls, actual_data_dict: dict, expected_dict: dict):
        """
        递归验证字典字段值,直到到最底层
        :param actual_data_dict: 实际的数据字典
        :param expected_dict: 期望的字典
        :return: bool
        """
        false_reason = []
        try:
            # 本级别验证字段
            cls.assert_data_field(expected_data=expected_dict, actual_data=actual_data_dict)
            # 验证通过
            return True, false_reason
        except AssertionError as e:
            # 当前层级不匹配，继续查找子项
            false_reason.append(e)
        # 没有验证通过，继续递归验证子项
        for data_key, data_value in actual_data_dict.items():
            if isinstance(data_value, dict):
                # 如果data_dict字典里面有一项的值里面是字典，则递归验证
                if cls.loop_validate_contains_dict(data_value, expected_dict):
                    return True, false_reason
            elif isinstance(data_value, list):
                # 如果data_dict字典里面有一项的值里面是列表，则挨个验证列表中的每个子元素
                for item in data_value:
                    if isinstance(item, dict):
                        # 列表中每一项都是字典，递归验证
                        if cls.loop_validate_contains_dict(item, expected_dict):
                            return True, false_reason
        return False, false_reason

    @classmethod
    @allure.step("验证响应包含预期字典")
    def res_contains_data(cls, expected: dict, actual: dict, ctx:Any):
        """
        递归验证预期的值,直到到最底层
        Args:
            expected: 期望的字典 dict
            actual: 实际的字典数据 dict
            ctx: 上下文信息，包含路径等信息
        """
        # if isinstance(response, requests.Response):
        #     data = cls.get_resp_json(response)
        # else:
        #     data = response
        is_pass, false_reason = cls.loop_validate_contains_dict(actual, expected)
        assert is_pass, f"验证失败: 响应中的数据没有匹配到{expected}, 原因: {false_reason}"

    @classmethod
    @allure.step("验证响应包含预期字典键")
    def res_contains_key(cls, expect: list[str], actual: dict, ctx: Any):
        """
        使用jsonpath验证预期的值
        Args:
            expect: 期望的键列表 例如 ["username", "userId]
            actual: 实际的字典数据
            ctx: 上下文信息，包含路径等信息
        """
        for expected_key in expect:
            assert expected_key in actual.keys(), f"验证失败: {actual} 中没有提取到{expected_key}"
    #
    # @classmethod
    # @allure.step("验证响应指定字段数据中有没有预期的字段值")
    # def assert_response_field(cls, response, field_path: str, expected_value: Any = None):
    #     """
    #     验证响应中的字段值,和jsonpath验证差不多（常用）
    #     Args:
    #         response: requests.Response对象
    #         field_path: 字段路径，支持嵌套，如 "data.id", 如果为""表示验证根字段
    #         expected_value: 期望的值，如果为None则只检查字段存在性。如果field_path解析后是一个列表,则挨个验证列表中的每个子元素,有一个匹配则通过
    #     """
    #     # 获取响应JSON数据
    #     data = cls.get_resp_json(response)
    #     # 解析字段路径
    #     field_path = field_path.replace(" ", "")
    #     field_keys_list = field_path.split('.') if field_path else []
    #     actual_res_value = data
    #
    #     for field in field_keys_list:
    #         if field not in actual_res_value:
    #             raise ProjectAssertionError(f"字段 '{field_path}' 不存在于响应中")
    #         actual_res_value = actual_res_value[field]
    #
    #     if expected_value is None:
    #         # 仅验证字段存在性
    #         return actual_res_value
    #     # 验证字段值
    #     if isinstance(actual_res_value, list):
    #         # 实际结果是一个列表
    #         is_pass = True
    #         for item in actual_res_value:
    #             try:
    #                 cls.assert_data_field(expected_data=expected_value, actual_data=item)
    #                 is_pass = True
    #                 break
    #             except ProjectAssertionError as e:
    #                 is_pass = False
    #                 logger.error(e)
    #         assert is_pass, f"字段 '{field_path}' 值不匹配: 预期 {expected_value}, 实际 {actual_res_value}"
    #     else:
    #         # 实际结果是其他类型
    #         cls.assert_data_field(expected_data=expected_value, actual_data=actual_res_value)
    #     logger.info(f"字段 '{field_path}' 验证通过: {actual_res_value}")
    #     return actual_res_value


    # @staticmethod
    # @allure.step("验证列表响应")
    # def assert_list_response(response, items_field: str = "data",
    #                          min_count: int = 0, max_count: int = None):
    #     """
    #     验证列表类型的响应
    #
    #     Args:
    #         response: requests.Response对象
    #         items_field: 列表数据字段名
    #         min_count: 最小记录数
    #         max_count: 最大记录数
    #     """
    #     try:
    #         data = response.json()
    #     except Exception as e:
    #         raise ProjectAssertionError(f"Failed to parse JSON response: {e}")
    #
    #     items = data.get(items_field, [])
    #     assert isinstance(items, list), f"Field '{items_field}' is not a list"
    #
    #     count = len(items)
    #     assert count >= min_count, \
    #         f"List count {count} < minimum {min_count}"
    #
    #     if max_count is not None:
    #         assert count <= max_count, \
    #             f"List count {count} > maximum {max_count}"
    #
    #     logger.info(f"List response verified: {count} items")
    #     return items

    # @staticmethod
    # @allure.step("打印响应详情")
    # def log_response_details(response, title: str = "API Response"):
    #     """
    #     记录响应详情到日志和Allure报告
    #
    #     Args:
    #         response: requests.Response对象
    #         title: 标题
    #     """
    #     with allure.step(title):
    #         allure.attach(
    #             f"URL: {response.url}\n"
    #             f"Method: {response.request.method}\n"
    #             f"Status Code: {response.status_code}\n"
    #             f"Response Time: {response.elapsed.total_seconds():.2f}s\n"
    #             f"Headers: {json.dumps(dict(response.headers), indent=2, ensure_ascii=False)}\n"
    #             f"Body: {json.dumps(response.json(), indent=2, ensure_ascii=False) if response.headers.get('content-type', '').startswith('application/json') else response.text}",
    #             name="Response Details",
    #             attachment_type=allure.attachment_type.TEXT
    #         )
    #
    #     logger.info(f"{title}: Status={response.status_code}, Time={response.elapsed.total_seconds():.2f}s")
