import sys
import re
from computer.register import InstructionType, NO_ARGUMENT


def read_asm_file(source_name):
    """ 读取asm程序源码 """
    result, last_fun = "", ""
    variable, function_point, label_in_fun = dict(), dict(), dict()
    index, instruction_index = 0, 0

    with open(source_name, "r") as f:
        line = f.readline()
        index += 1
        line = pre_translation(line)
        read_all_data = True
        if line == "SECTION .DATA":
            read_all_data = False
        while line and not read_all_data:
            line = f.readline()
            index += 1
            line = line.split(";")[0]
            line = re.sub(r"\t+", "", line)
            line = re.sub(r"\n", "", line)
            section = pre_translation(line)
            if section == "SECTION .TEXT":
                break
            key, value = read_variable(line)
            key = key.upper()
            assert key != 'INPUT' and key != 'OUTPUT', "Line {}:You can't declare a variable name as INPUT or OUTPUT".format(
                index)
            assert key not in variable.keys(), "Line {}:You can't declare a variable two or more times".format(index)
            variable[key] = value
        line = f.readline()
        index += 1
        line = pre_translation(line)
        is_first_fun = True
        while line:
            if line != "" and line != "\n":
                if check_string("^\S*:$", line):  ## a function or label
                    line = pre_translation(line)
                    if check_string("^\.\S*:$", line):
                        line = line.replace(":", "")
                        label_in_fun[last_fun][line] = instruction_index
                    else:
                        line = line.replace(":", "")
                        function_point[line] = instruction_index
                        label_in_fun[line] = dict()
                        last_fun = line
                        if is_first_fun:
                            assert last_fun == '_START', 'Your first function should be _start'
                            is_first_fun = False
                else:  ## normal instructions
                    line = line.split(";")[0]
                    line = re.sub(r"\t+", "", line)
                    line = re.sub(r"\n", "", line)
                    line = re.sub(r" +", " ", line)
                    split = line.split(" ")
                    split[0] = split[0].upper()
                    assert split[0] in InstructionType.__members__, "Line {}, no such instrument".format(index)
                    if InstructionType[split[0]] in NO_ARGUMENT:
                        assert len(split) == 1, "Line {}, this instrument have no argument".format(index)
                    else:
                        assert len(split) == 2, "Line {}, only one argument allowed".format(index)
                    if line != "":
                        if len(split) == 2:
                            if not check_string("^\'[A-Za-z]{1}\'$", split[1]):
                                split[1] = split[1].upper()
                            result = result + str(instruction_index) + " " + InstructionType[split[0]].value + " " + \
                                     split[1] + " " + "\n"
                        else:
                            result = result + str(instruction_index) + " " + InstructionType[
                                split[0]].value + " " + "\n"
                        instruction_index += 1
            line = f.readline()
            index += 1
    return result, function_point, label_in_fun, variable, instruction_index


def check_string(re_exp: str, target: str) -> bool:
    """
    判断字符串和正则表达式是否匹配
    :param re_exp: 正则表达式
    :param target: 需要判断的字符串
    :return: bool
    """
    return bool(re.search(re_exp, target))


def read_variable(line: str) -> tuple[str, str]:
    """  读取变量  """
    # assert any(check_string(pattern, line) for pattern in [
    #     "^.*: *0 *$",
    #     "^.*: *[1-9]+[0-9]* *$",
    #     "^.*: *\".*\" *, *[1-9]+[0-9]* *$",
    #     "^.*: *\".*\" *$"
    # ]), f"Illegal variable {line}"

    key, value = map(str.strip, line.split(":", 1))
    key = re.findall("\S*", key)[0]

    if check_string("^.*: *-?[1-9]+[0-9]* *$", line):  # Numeric
        value = re.findall("-?[1-9]+[0-9]*", value)[0]
    elif check_string("^.*: *0 *$", line):
        value = '0'
    elif check_string("^.*: *\".*\" *$", line):  # String
        value = re.findall("\".*\"", value)[0] + f",{len(value) - 2}"
    else:
        left, right = map(str.strip, value.rsplit(',', 1))
        left = left.rsplit("\"", 1)[0] + "\""
        value = f"{left},{re.sub(r' ', '', right)}"

    return key, value


def pre_translation(line: str) -> str:
    """
    翻译内容预处理
    1、将每行内容转换为大写
    2、去掉";"之后的内容(仅作为注释使用)
    3、去掉制表符(\t)和换行符(\n)
    """
    line = line.upper()
    line = line.split(";")[0]
    line = re.sub(r"\t+", "", line)
    line = re.sub(r"\n", "", line)
    return line


def translate(source_name: str, target_name: str):
    """
    翻译：
    1、获取asm文件内容
    2、翻译内容后写入指定文件
    @param source_name 源文件
    @param target_name 数据写入文件
    """
    result, function_point, label_in_fun, variable, instruction_index = read_asm_file(source_name)
    write_translate(target_name, result, function_point, label_in_fun, variable, instruction_index)


def write_translate(target_name: str, result, function_point, label_in_fun, variable, instruction_index):
    """ 将asm文件翻译内容写入文件 """
    with open(target_name, "w") as f:
        f.write(result)
        f.write("FUNCTION\n")
        for i in function_point:
            line = i + ":" + str(function_point[i]) + "\n"
            f.write(line)
        f.write("LABEL\n")
        for i in label_in_fun:
            for k in label_in_fun[i]:
                line = i + ":" + k + ":" + str(label_in_fun[i][k]) + "\n"
                f.write(line)
        f.write("VARIABLE\n")
        for i in variable:
            line = i + ":" + variable[i] + "\n"
            f.write(line)
    with open(target_name, "r") as f:
        index = 0
        while index < instruction_index:
            index += 1
            line = f.readline()
            line = pre_translation(line)
            term = line.split(" ")[1:]
            while "" in term:
                term.remove("")
            print(term)


if __name__ == "__main__":
    assert len(sys.argv) == 3, '参数错误'
    translate(sys.argv[0], sys.argv[1])
