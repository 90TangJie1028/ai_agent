"""计算器工具：安全四则运算 + 注册到 ToolRegistry。

模型只声明要调 calculator；真正算数在本地（类似 Cursor 调 Shell，
IDE 执行命令，模型不自己「跑」终端）。
"""

from __future__ import annotations
 # ast = Abstract Syntax Tree；Python 标准库模块，用于把表达式字符串解析成语法树节点，
 # 可安全遍历、检查代码结构，防止直接 eval 执行带来的任意代码风险
import ast 
# operator 是 Python 标准库，提供了函数式操作符（如加减乘除）的实现，
# 允许用函数方式调用本来用 +, -, *, / 等操作符实现的操作，比如 operator.add(1, 2)。
import operator

# 这句是 type hint：Any 表示任意类型。
# 这里只 import，用于类型注解（见 _BIN_OPS/_UNARY_OPS 用到）。
# typing 是 Python 的标准库模块，提供类型注解支持（如 Any、List、Dict 等）。
from typing import Any

# pydantic 是一个用于数据校验和设置数据模型的第三方库，这里用于定义工具参数的 schema（如 expression 字符串），
# 并自动做类型校验、生成 JSON schema，方便与 LLM tool 参数校验对接
from pydantic import BaseModel, Field


# 从当前目录的 registry.py 文件中导入 ToolRegistry 类
from model_gateway.tools.registry import ToolRegistry

# 工具名称，固定为 "calculator"
TOOL_NAME = "calculator"
# 工具描述，用于在模型中显示，描述工具的功能和使用方法
TOOL_DESCRIPTION = (
    "Evaluate a basic arithmetic expression. "
    "Supports +, -, *, /, //, %, **, and parentheses. "
    "Input example: expression=\"123 * 456\"."
)

# 只允许这些二元/一元运算；禁止调用、属性、名字等（防任意代码执行）
# type[ast.operator] 表示 ast.operator 的类型，比如 ast.Add 表示加法运算。
# dict[type[ast.operator], Any] 表示一个字典，键是 ast.operator 的类型，值是任意类型。
# 这里用于定义二元/一元运算的实现
# 比如 operator.add(1, 2) 相当于 1 + 2。
_BIN_OPS: dict[type[ast.operator], Any] = {
    ast.Add: operator.add,  # 加法（x + y），等价于 x + y
    ast.Sub: operator.sub,  # 减法（x - y），等价于 x - y
    ast.Mult: operator.mul,  # 乘法（x * y），等价于 x * y
    ast.Div: operator.truediv,  # 除法（x / y），等价于 x / y
    ast.FloorDiv: operator.floordiv,  # 地板除法（x // y），“地板”即向下取整除法。例如 7 // 2 = 3（不是3.5），即结果永远向下取整到最接近的整数
    ast.Mod: operator.mod,  # 模运算（x % y），等价于 x % y
    ast.Pow: operator.pow,  # 幂运算（x ** y），等价于 x ** y
}
# type[ast.unaryop] 表示 ast.unaryop 的类型，比如 ast.UAdd 表示正数运算，ast.USub 表示负数运算。
# dict[type[ast.unaryop], Any] 表示一个字典，键是 ast.unaryop 的类型，值是任意类型。
# 这里用于定义一元运算的实现
# 比如 operator.pos(1) 相当于 +1，operator.neg(1) 相当于 -1。
_UNARY_OPS: dict[type[ast.unaryop], Any] = {
    # Python 标准 AST 不支持自增（++）和自减（--）运算符，它们不是合法表达式，
    # 只允许一元正负运算 (+x, -x)
    ast.UAdd: operator.pos,  # +x
    ast.USub: operator.neg,  # -x
}

# 继承 BaseModel 之后，CalcArgs 具备了：
# - 参数校验能力：会自动验证传入的参数类型和约束（如 expression 必须为非空字符串）。
# - 自动生成 JSON-schema：可用于 OpenAI 的工具参数 schema。
# - 易于序列化/反序列化：支持 dict/JSON 转换，便于与 LLM 工具对接。
# - 直观的错误提示：参数不符合时会抛出明确的 ValidationError 异常，方便调试和捕获。
class CalcArgs(BaseModel):
    # 这里定义了工具的参数 schema，expression 字段必须是非空字符串，且描述为 "arithmetic expression"。
    # 这个 schema 会被 pydantic 自动校验，确保传入的参数符合要求。
    # min_length=1 表示 expression 字段必须是非空字符串。
    # description="arithmetic expression" 表示 expression 字段的描述为 "arithmetic expression"。
    # 比如 expression="123 * 456" 是合法的，expression="123 * 456" 是非法的。
    expression: str = Field(
        min_length=1,
        description="arithmetic expression, e.g. 123 * 456",
    )  

class UnsafeExpressionError(ValueError):
    """表达式含不允许的语法（名字、函数调用、属性等）。"""


def eval_safe(expression: str) -> int | float:
    """解析并求值算术表达式；拒绝非算术 AST 节点。"""
    # expression.strip() 用于去除表达式两端的空白字符（如空格、换行符等），
    # 确保后续解析时不会因为前后空白字符导致语法错误。
    text = expression.strip()
    # 如果去除空白字符后的表达式为空，则抛出 ValueError 异常，表示表达式不能为空。
    if not text:
        # 抛出 ValueError 异常，表示表达式不能为空。
        raise ValueError("expression must be non-empty")
    try:
        tree = ast.parse(text, mode="eval")
        # ast.parse(text, mode="eval") 用于将表达式字符串解析为抽象语法树（AST），
        # 这个树结构包含了表达式的所有语法信息，包括操作符、操作数、括号等。
        # mode="eval" 表示解析模式为 eval，即允许在表达式中使用内置函数和变量。
        # 比如 expression="123 * 456" 会被解析为 ast.BinOp(ast.Constant(123), ast.Mult(), ast.Constant(456))。
    except SyntaxError as exc:
        raise ValueError(f"invalid expression: {expression!r}") from exc
    return _eval_node(tree.body)


def _eval_node(node: ast.AST) -> int | float:
    # 如果节点是 ast.Constant（常量），且值是 int 或 float
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        # 返回节点的值
        return node.value

    # 如果节点是一元运算（如正负号），且操作类型在 _UNARY_OPS 支持列表里
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        # 递归计算操作数，再根据操作类型调用对应的函数（如 operator.neg/pos）
        return _UNARY_OPS[type(node.op)](_eval_node(node.operand))

    # 如果节点是二元运算（如加减乘除），且操作类型在 _BIN_OPS 支持列表里
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
        # 递归分别计算左右两个子节点
        # 先递归计算左子节点，通常就是取出常量（如 123 * 456，node.left 就是常量 123）。
        left = _eval_node(node.left)
        # 再递归计算右子节点，通常就是取出常量（如 123 * 456，node.right 就是常量 456）。
        right = _eval_node(node.right)
        try:
            # 根据操作类型调用对应的函数（如 operator.add/sub/mul/truediv），
            # 比如 node.op 是 ast.Add，则调用 operator.add(left, right)。
            return _BIN_OPS[type(node.op)](left, right)
        except ZeroDivisionError as exc:
            # 如果除数为零，抛出更友好的异常信息
            raise ValueError("division by zero") from exc

    # 如果节点是 ast.Expression，递归处理其 body
    if isinstance(node, ast.Expression):
        # 递归处理其 body，通常就是取出常量（如 123 * 456，node.body 就是常量 123 * 456）。
        # 比如 node.body 是 ast.BinOp(ast.Constant(123), ast.Mult(), ast.Constant(456))，
        # 则调用 _eval_node(ast.BinOp(ast.Constant(123), ast.Mult(), ast.Constant(456)))。
        return _eval_node(node.body)

    # 其他类型的节点都视为不安全，抛出异常
    raise UnsafeExpressionError(
        f"disallowed expression node: {type(node).__name__}"
    )


def run_calculator(args: CalcArgs) -> str:
    """Registry handler：入参已是校验后的 CalcArgs，返回给 role=tool 的字符串。"""
    value = eval_safe(args.expression)   # 计算表达式的值
    # int 结果保持整数字符串，避免 56088.0 干扰模型
    if isinstance(value, float) and value.is_integer():
        # 如果结果是浮点数且为整数，则转换为整数字符串，避免 56088.0 干扰模型
        return str(int(value))
    # 如果结果是浮点数且不为整数，则转换为浮点数字符串
    return str(value)


def register_calculator(registry: ToolRegistry, *, replace: bool = False) -> None:
    """把 calculator 挂进工具目录（对外 name 固定为 calculator）。"""
    # registry.register(name=TOOL_NAME, description=TOOL_DESCRIPTION, args_model=CalcArgs, handler=run_calculator, replace=replace)
    # 注册工具到工具目录，name 为 TOOL_NAME，description 为 TOOL_DESCRIPTION，
    # args_model 为 CalcArgs，handler 为 run_calculator，replace 为 False。
    # 如果 replace 为 True，则替换已有的工具。
    # 比如 registry.register(name="calculator", description="Evaluate a basic arithmetic expression. Supports +, -, *, /, //, %, **, and parentheses. Input example: expression=\"123 * 456\".", args_model=CalcArgs, handler=run_calculator, replace=False)
    registry.register(
        name=TOOL_NAME,
        description=TOOL_DESCRIPTION,
        args_model=CalcArgs,
        handler=run_calculator,
        replace=replace,
    )


def build_default_registry() -> ToolRegistry:
    """D11 默认：仅含 calculator 的工具集。"""
    reg = ToolRegistry()
    register_calculator(reg)
    return reg
