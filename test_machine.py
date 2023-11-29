from translator import translator
from machine import machine
from math import gcd
import unittest


class MachineTest(unittest.TestCase):
    """ 处理器测试 """

    def setUp(self) -> None:
        print("Test beginning:")

    def tearDown(self) -> None:
        print("Test finished.")

    def test_cat(self):
        print("Testing cat")
        translator.translate('./asm/cat.asm', './asm/target')
        result = machine.start('./asm/target', './asm/cat_test.txt')
        text = ''
        with open('asm/cat_test.txt') as f:
            text = f.read()
        self.assertEqual(result, text)

    def test_hello(self):
        print("Testing hello")
        translator.translate("./asm/hello.asm", "./asm/target")
        result = machine.start("./asm/target", '')
        self.assertEqual(result, "Hello,world")

    def test_prob5(self):
        print("Testing problem5")
        translator.translate("./asm/problem5.asm", "./asm/target")
        result = machine.start("./asm/target", '')
        result1 = 1
        for i in range(1, 21):
            result1 = result1 * i // gcd(result1, i)
        print("问题5答案:" + result)
        self.assertEqual(int(result), result1)


if __name__ == '__main__':
    unittest.main()
