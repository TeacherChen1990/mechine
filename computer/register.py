from enum import Enum, unique

@unique
class Position(Enum):
    INS = 1  # 指令
    FUN = 2  # 函数
    LAB = 3  # 标签
    VAR = 4  # 变量


@unique
class RegisterType(Enum):
    """ 寄存器 """
    IP = "IP"  # 计数
    BR = "BR"  # 缓存，例如用于存储除法的余数等等
    AC = "AC"  # 结果储存
    PS = "PS"  # nzvc
    SP = "SP"  # 堆栈
    AR = "AR"  # 地址
    IR = "IR"


@unique
class InstructionType(Enum):
    """ 指令集 """
    # math
    ADD = "ADD"
    SUB = "SUB"
    CMP = "CMP"
    DIV = "DIV"
    MUL = "MUL"
    INV = "INV"
    LD = 'LD'
    ST = 'ST'
    PUSH = "PUSH"
    POP = "POP"
    # 跳转
    JMP = "JMP"
    JNZ = "JNZ"
    JZ = "JZ"
    JS = "JS"
    CALL = "CALL"
    RET = "RET"
    # 停止
    HLT = "HLT"


""" 数学操作指令集 """
MATH_INSTRUCTION = (
    InstructionType.ADD, InstructionType.SUB, InstructionType.INV, InstructionType.CMP, InstructionType.DIV,
    InstructionType.MUL)

""" 数据操作指令集 """
DATA_INSTRUCTION = (InstructionType.LD, InstructionType.ST)

""" 栈操作指令集 """
STACK_INSTRUCTION = (InstructionType.POP, InstructionType.PUSH)

""" 跳转指令集 """
JUMP_INSTRUCTION = (
    InstructionType.JZ, InstructionType.JMP, InstructionType.JNZ, InstructionType.CALL, InstructionType.JS,
    InstructionType.RET)

""" 无参数指令集 """
NO_ARGUMENT = (
    InstructionType.PUSH, InstructionType.POP, InstructionType.RET, InstructionType.INV, InstructionType.HLT)


class Instruction:
    def __init__(self, instruction: InstructionType, args: []):
        self.instruction = instruction
        self.args = args

    def to_string(self) -> str:
        result = ""
        result = result + self.instruction.value
        k = 0
        for i in self.args:
            if k == 0:
                result = result + " " + i
                k += 1
            else:
                result = result + " " + i
        return result


def read_code(filename: str) -> {}:
    program = {'Instruction': [], 'Variable': {}, 'Function': {}}
    position = Position.INS
    with open(filename, "r") as f:
        line = f.readline()
        assert line != "", "You open a file, whose format is not property"
        while line:
            line = line.replace("\n", "")
            if line == "FUNCTION":
                position = Position.FUN
            elif line == "LABEL":
                position = Position.LAB
            elif line == "VARIABLE":
                position = Position.VAR
            else:
                ins: Instruction
                if position == Position.INS:
                    term = line.split(" ")
                    ins_type = InstructionType[term[1]]
                    while "" in term:
                        term.remove("")
                    if term[1] == 'HLT':
                        ins = Instruction(ins_type, [])
                    else:
                        ins = Instruction(ins_type, term[2:])
                    program['Instruction'].append(ins)
                elif position == Position.FUN:
                    term = line.split(":")
                    while "" in term:
                        term.remove("")
                    program['Function'][term[0]] = dict()
                    program['Function'][term[0]]['self'] = int(term[1])
                elif position == Position.LAB:
                    term = line.split(":")
                    while "" in term:
                        term.remove("")
                    program['Function'][term[0]][term[1]] = int(term[2])
                elif position == Position.VAR:
                    term = line.split(":", 1)
                    while "" in term:
                        term.remove("")
                    program['Variable'][term[0]] = term[1]
            line = f.readline()
    return program
