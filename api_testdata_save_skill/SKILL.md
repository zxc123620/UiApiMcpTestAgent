---
name: 接口测试用例保存规则
description:  接口测试用例保存到数据库的规则。当用户要求将接口测试用例\数据保存到数据库时使用。
---
# 说明

1. 将生成的测试数据存储到数据库时，需要按照如下结构来插入数据。
2. 数据生成后可以给一个简单的说明文档，说明干了什么事情。
## 测试用例生成约束
1. 单个用例能单独执行。用例之间不产生依赖关系。
2. 用例执行完成后应保证被测系统干净，不产生遗留数据。以`模块`即`module_name`为最小单位来产生/清除遗留数据，而不是以用例为单位, 执行用例时也以模块为单位来执行, 整个模块的最后一条用例执行完成后，才执行清除数据操作。因有些数据可能在整个测试流程中使用，比如一些初始化的数据，这种数据可以不做数据清除。
3. 如果知道需要获取的数据内容，并且能使用jsonpath做验证或者获取到数据,就尽量不要用ai断言。ai断言尽量做语义判断用，例如提示信息。
## 测试数据生成约束
1. 数据必须模拟现实情况、有规律并且能一眼看到是测试数据。比如用户名叫"张xx-测试","周xx-测试"， 而不是叫"测试用户"。
## 数据库表结构
**api_info表**
存放接口信息
```
-- api_info definition

CREATE TABLE api_info (
	id INTEGER NOT NULL, 
	name VARCHAR(255),  --接口名称
	project_name VARCHAR(255),  --所属项目名称
	module_name VARCHAR(255),  -- 所属模块名称
	sub_module_name VARCHAR(255),  -- 子模块名称
	description VARCHAR(255),  -- 接口描述
	endpoint VARCHAR(255),  -- 后缀地址
	method VARCHAR(255),  -- 请求方法
	response_model VARCHAR(255),  -- 响应模型(固定为空)
	swagger_md_text TEXT,  -- 接口文档(固定为空)
	PRIMARY KEY (id)
);

CREATE INDEX ix_api_info_id ON api_info (id);
```

**api_test_case表**
存放存放接口测试用例

```
-- api_test_case definition

CREATE TABLE api_test_case (
	id INTEGER NOT NULL, 
	"key" VARCHAR(255) NOT NULL,  -- 唯一值，需要有实际意义例如user.add.success，可以是拼音也可以是英文,不能是中文
	module_name VARCHAR(255),  -- 模块名称
	sub_module_name VARCHAR(255),   -- 子模块名称
	title VARCHAR(255),  -- 测试数据标题
	description VARCHAR(255),  -- 测试数据描述
	pre_requisites JSON,  -- 前置条件
        post_steps JSON,  -- 后置步骤
	test_steps JSON,  -- 测试步骤
	is_active INTEGER DEFAULT (1),  -- 是否启用
	order INTEGER DEFAULT (0),  -- 排序，用于在模块内排序，默认0,如果是清场的用例，则应该设置为模块内最大的order+1

	PRIMARY KEY (id)
);

CREATE INDEX ix_api_test_case_key ON api_test_case ("key");
CREATE INDEX ix_api_test_case_id ON api_test_case (id);
```

**api_test_data表**
存放接口测试数据
```
-- api_test_data definition

CREATE TABLE api_test_data (
	id INTEGER NOT NULL, 
	"key" VARCHAR(255) NOT NULL,  -- 唯一值 需要有实际意义例如user.add.success，可以是拼音也可以是英文,不能是中文
	name VARCHAR(255),  -- 名称
	description VARCHAR(255),  -- 描述
	headers JSON,  -- 请求头
	api_info_id INTEGER NOT NULL, -- 接口信息id 
	data JSON,  -- json请求体
	params JSON,  -- 请求参数
	extract JSON,  -- 请求结果提取
	PRIMARY KEY (id), 
	FOREIGN KEY(api_info_id) REFERENCES api_info (id)
);

CREATE INDEX ix_api_test_data_key ON api_test_data ("key");
CREATE INDEX ix_api_test_data_id ON api_test_data (id);
```

## 共用断言类
```
class AssertionRule(BaseModel):
    """单条断言规则"""
    jsonpath: str = Field(default="$", description="JSONPath 表达式(支持所有的JSONPath表达式语法)")
    operator: str = Field(default="res_contains_data", description="断言操作符")
    expect_value: Any = Field(..., description="预期值")


class AssertionConfig(BaseModel):
    """完整的断言配置（普通规则列表 + AI 规则）"""
    assertion_rules: list[AssertionRule] = Field(..., description="断言规则列表")
    ai_assertion_rule: Optional[str] = Field(
        default=None,
        description="AI 断言内容，例如：'响应体包含xxx字段'、'响应体包含xxx字段且值为123'、'响应体xxx字段应该与xxx语义相符' 等",
    )
```

**说明**
-   `assertion_rules` 和 `ai_assertion_rule`是相辅相成的,可以同时使用。例如在一些接口失败提示中,使用Ai来判断提示字段内容更好，其他字段使用普通判断。

**AssertionRule.operator 支持的值**

| 操作符 | 含义说明 |
| :--- | :--- |
| **基本比较** | |
| `eq` | 判断实际值是否等于期望值。 |
| `eq_req_body_jsonpath` | 判断实际值是否等于指定测试步骤中某个请求体 JSONPath 路径下的值。参数为 JSONPath 表达式；系统会依次遍历该测试步骤中的每个请求，逐一查找，直到最后一个请求结束。 |
| `ne` | 判断实际值是否不等于期望值。 |
| `gt` | 判断实际值是否大于期望值。 |
| `gte` | 判断实际值是否大于或等于期望值。 |
| `lt` | 判断实际值是否小于期望值。 |
| `lte` | 判断实际值是否小于或等于期望值。 |
| **存在性与类型** | |
| `exists` | 判断指定字段是否存在。 |
| `not_exists` | 判断指定字段是否不存在。 |
| `type` | 判断字段类型是否与期望类型匹配。 |
| **字符串匹配（常用）** | |
| `contains` | 判断字符串是否包含指定子串。 |
| `not_contains` | 判断字符串是否不包含指定子串。 |
| `regex` | 判断字符串是否匹配指定正则表达式。 |
| `startswith` | 判断字符串是否以指定子串开头。 |
| `endswith` | 判断字符串是否以指定子串结尾。 |
| **长度判断** | |
| `length_eq` | 判断长度是否等于期望值。 |
| `length_gt` | 判断长度是否大于期望值。 |
| `length_lt` | 判断长度是否小于期望值。 |
| **集合与范围** | |
| `in` | 判断实际值是否包含于指定集合或列表中。 |
| `not_in` | 判断实际值是否不包含于指定集合或列表中。 |
| `between` | 判断实际值是否处于指定范围内。 |
| **空值判断** | |
| `is_empty` | 判断值是否为空。 |
| `not_empty` | 判断值是否不为空。 |
| **字典判断（常用）** | |
| `res_contains_data` | 判断响应结果是否包含期望的字典数据。`expect_value` 应为 `dict` 类型。 |
| `res_contains_key` | 判断响应结果是否包含期望的字段。`expect_value` 应为 `list[str]` 类型，其中列出期望的键名称。 |
## 表字段内容使用规则

### api_test_data 下的 headers, params , data 字段
headers, data, params 里面的字段值内容可进行`上下文替换`与`方法调用`。

**上下文替换**
规则为`${变量名}`, 变量名称从`api_test_data.extract`字段中的`name`值里面提取。可存储`dict`、`str`、`int` 、`list`等类型的数据。如果是`dict`类型，可使用 `xxx.xxx`来获取字典中的数据，例如`${zhangsan.sex}`
举例:
1. 存储单个数据: 修改用户信息时,需要传递一个用户id。需在获取用户接口测试数据的`extract`添加一个提取字段zhangSanUserId，然后可以可以在修改用户信息接口中使用上下文替换`${zhangSanUserId}`    
2. 存储字典数据: 假如存储了张三的字典`{"username": "张三", "sex": "男"}`, 变量名称叫"zhangsan"，获取数据时可用`${zhangsan.username}` , `{zhangsan.sex}`

**方法调用**
 规则为`__方法名(参数1, 参数2, ...)__`或`__method_name(arga='x', argb='y')__`，适用于测试数据中需要调用系统方法的字段。注意方法前后有两个下划线。
例如A接口的请求体中需要一个随机16进制颜色值,需要调用方法`random_hex_color`,则实际写入到测试数据中的是`__random_hex_color()__`
可用方法列表如下:
```
def login_data_encrypt(username, password, captcha_code=None, captcha_request=None) -> str:
    """
    登陆信息RSA加密
    Args:
        username: 用户名
        password: 密码
        captcha_code: 验证码,可不传,默认1
        captcha_request: 验证码请求参数,可不传,默认1
    Returns:
    """
    # 内容已隐藏,不代表没有数据。
    pass

def des_encrypt(data: str) -> str:
    """
    des加密
    Args:
        data: 数据
    
    Returns:
        des加密后的数据
    """
    pass

```


### api_test_data .extract
请求结果提取,需要满足如下结构

```python
extract: Optional[list[APiTestDataResExtract]] = Field(default=None, description='提取字段')

class JsonPathHandle(BaseModel):
    """
    JSONPath 处理方法
    """
    handle_method: str = Field(default="get_index", description='提取字段处理方法,默认get_index不动')
    handle_param: dict = Field(default_factory=lambda: {"index":0}, description='处理方法参数,按照默认参数不动')

class APiTestDataResExtract(BaseModel):
    """
    API测试数据响应提取字段
    """
    name: str = Field(..., description='提取字段名称')
    jsonpath: str = Field( default="", description='jsonpath提取字段路径')
    handle: JsonPathHandle = Field(default_factory=JsonPathHandle, description='提取字段处理方法')
    description: str = Field(default="", description='提取字段描述')
```
举例
```
[{"name":"xxxname","jsonpath":"$.name","description": "描述信息"}]
```

### api_test_case .pre_requisites、post_steps
内部内容需要满足如下结构
```
pre_requisites: Optional[list[Requisites]] = Field(default=None, description='前置条件')
post_steps: Optional[list[Requisites]] = Field(default=None, description='后置步骤')

class JudgeCriteriaItem(BaseModel):
    """
    前置/后置条件判断标准项
    """
    assertion_config : Optional[AssertionConfig] = Field(default=None, description='校验字段规则配置')
    steps_after_failure: list[str] = Field(default_factory=list,
                                           description='前置/后置条件判断失败后执行的步骤,执行什么测试数据键即api_test_data.key')
    steps_after_success: list[str] = Field(default_factory=list,
                                           description='前置/后置条件判断成功后执行的步骤,执行什么测试数据键即api_test_data.key')

class JudgeCriteria(BaseModel):
    """
    前置/后置条件判断标准
    """
    test_data_key: str = Field(..., description='测试数据键即api_test_data.key')
    judgment_criteria_items: list[JudgeCriteriaItem] = Field(default_factory=list, description='前置/后置条件判断标准项')

class ContextKeyHas(BaseModel):
    """
    上下文键有
    """
    context_key: str = Field(..., description='上下文键')
    steps_after_failure: list[str] = Field(default_factory=list,
                                           description='上下文键失败后执行的步骤,执行什么测试数据键即api_test_data.key')

class Requisites(BaseModel):
    """
    前置/后置条件

    """
    context_key_has: Optional[list[ContextKeyHas]] = Field(default=None, description='上下文键有')
    api_res_exist: Optional[list[JudgeCriteria]] = Field(default=None, description='API响应判断标准')
    api_res_not_exist: Optional[list[JudgeCriteria]] = Field(default=None, description='API响应判断标准（不存在）')


```

### api_test_case.test_steps
内容应该按照如下结构
```
class TestSteps(BaseModel):
    """
    测试步骤
    """
    test_data_key: str = Field(..., description='测试数据键即api_test_data.key')
    description: str = Field(default="", description='测试步骤描述')
    assertion_config: Optional[AssertionConfig] = Field(default=None, description='校验字段')

```

**validate_rules 例子**
```
[{"path":"$","operator":"res_contains_data","expect_value":{"userName":"张三"}}]
```
