import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from assembler import parse_source, to_ir, encode


class AssemblerTests(unittest.TestCase):
    def setUp(self):
        source = os.path.join(os.path.dirname(__file__), 'data', 'test.csv')
        self.ir = to_ir(parse_source(source))

    def test_ir_fields(self):
        self.assertEqual([item['command'] for item in self.ir],
            ['LOAD_CONST', 'READ_MEM', 'WRITE_MEM', 'SHR'])
        self.assertEqual(self.ir[0]['fields']['B']['value'], 42)
        self.assertEqual(self.ir[0]['fields']['C']['value'], 90)
        self.assertEqual(self.ir[1]['fields']['B']['value'], 914)
        self.assertEqual(self.ir[1]['fields']['C']['value'], 224)
        self.assertEqual(self.ir[2]['fields']['B']['value'], 873)
        self.assertEqual(self.ir[2]['fields']['C']['value'], 350)
        self.assertEqual(self.ir[3]['fields']['D']['value'], 267)

    def test_expected_encoding(self):
        expected = bytes.fromhex(
            '50 01 A0 05 00 00 91 1C 00 0E 00 '
            '4E 1B E0 15 00 7D 02 70 0B 60 21 00')
        self.assertEqual(encode(self.ir), expected)

    def test_out_of_range_operand(self):
        with self.assertRaises(ValueError):
            to_ir([{'name': 'LOAD_CONST', 'A': 0, 'B': 42, 'C': 1 << 22}])

if __name__ == '__main__':
    unittest.main()
