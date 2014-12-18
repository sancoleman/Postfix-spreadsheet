#!/usr/bin/env python2.7 -tt

import sys
import csv
import os
import operator
import re
import string
import StringIO
import math
from collections import deque

import argparse
parser = argparse.ArgumentParser(description='Process spreadsheet with CSV input and evaluate postfix by Scott Coleman')
parser.add_argument(nargs=1, dest='csvfilename',
                   help='an input file in comma seprated CSV format')
parser.add_argument('--version', action='version', version='%(prog)s 0.1')
args = parser.parse_args()


class Sheet(object):
    """Simple spreadsheet class with Postfix support
    """
    def __init__(self):
        self.cells = {}
        self.index = {}
        self.cols = None
        self.operators = { '+': operator.add, '-': operator.sub, '*': operator.mul,
                           '/': operator.div, '//': operator.floordiv,
                           '%': operator.mod, '**': operator.pow }

    def int_to_base_26_chr(self, x):
        """ Reference to sourceforge http://bit.ly/10U0IUE """
        from string import lowercase # imports 'a...z'
        if x in self.index:
            return self.index[x]
        else:
            self.index[x] = ''.join(lowercase[i] for i in reversed(list(self.base_26_generator(x))))
            return self.index[x]

    def base_26_generator(self, x):
        if x == 0: yield x
        while x > 0:
            yield x % 26
            x //= 26

    def guess_numeric(self, string):
        return self.guess_int(string) or self.guess_float(string)

    def guess_int(self, string):
        try:
            int(string)
            return True
        except ValueError:
            return False

    def guess_float(self, string):
        try:
            float(string)
            return True
        except ValueError:
            return False

    def update_cell(self, data, row, col):
        """Update cell or create a new one if not exists"""
        key = str(self.int_to_base_26_chr(col)) + str(row)
        self.cells[key] = Cell(data, row, col)

    def eval(self, expression):
        """Update cell or create a new one if not exists"""
        operator = self.operators[expression.operator]
        assert operator
        assert expression.left
        assert expression.right
        return operator(*[float(expression.left), float(expression.right)])

    def is_float(self, val):
        """Returns true if token looks like a float or int, else return nothing
        """
        try:
            float(val)
            return True
        except ValueError:
            return False

    class ConstantNode(object):
        """Inits cell object with raw and computed values"""
        def __init__(self, data):
            self.data = data.strip()
            self.type = None # symbol, value, operator
            self.operators = { '+': operator.add, '-': operator.sub, '*': operator.mul,
                               '/': operator.div, '//': operator.floordiv,
                               '%': operator.mod, '**': operator.pow }

        def is_float(self):
            """Returns true if token looks like a float or int, else return nothing
            """
            try:
                float(self.data)
                return True
            except ValueError:
                return False

    class TokenNode(object):
        """Inits cell object with raw and computed values"""
        def __init__(self, data):
            self.data = data.strip()
            self.type = None # symbol, value, operator
            self.operators = { '+': operator.add, '-': operator.sub, '*': operator.mul,
                               '/': operator.div, '//': operator.floordiv,
                               '%': operator.mod, '**': operator.pow }

        def is_float(self):
            """Returns true if token looks like a float or int, else return nothing
            """
            try:
                float(self.data)
                return True
            except ValueError:
                return False

        def is_operator(self):
            """Returns true if token appears to be an arithmatic operator"""
            if self.data in self.operators:
                return True

    def import_csv(self, fname):
        assert os.path.isfile(fname)
        csv.register_dialect('spreadsheet', delimiter=',', quoting=csv.QUOTE_NONE)
        with open(fname, 'rb') as fname:
            csv_reader = csv.reader(fname, 'spreadsheet')
            try:
                sheet = Sheet()
                for row_key, row in enumerate(csv_reader):
                    for field_key, csv_field in enumerate(row):
                        self.update_cell(csv_field.strip(), row_key + 1, field_key) # TODO: this should create use cell object

            except csv.Error as e:
              sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))

    def import_csv_string(self, csv_string):
        """Imports string as if CSV file. This is used in unit tests"""
        csv.register_dialect('spreadsheet', delimiter=',', quoting=csv.QUOTE_NONE)
        csv_reader = csv.reader(StringIO.StringIO(csv_string), 'spreadsheet')
        for row_key, row in enumerate(csv_reader):
            for field_key, csv_field in enumerate(row):
                self.update_cell(csv_field.strip(),  row_key + 1, field_key) # TODO: this should create use cell object

    def get_cell_value(self, key):
        if key in self.cells:
            if self.cells[key].computed:
                return self.cells[key].computed
            else:
                return self.cells[key].raw

    def evaluate_postfix(self):
        for key in self.cells:
            self.cells[key].computed = self.postfix(str(self.cells[key].raw))

    def show_debug(self):
        for key in self.cells:
            print key + ":" + str(self.cells[key].raw) + " [" + str(self.cells[key].computed) + "]"

    def show(self):
        for key in self.cells:
            print str(self.cells[key].computed)

    def show_csv(self):
        for key in self.cells:
            if (isinstance(self.cells[key].computed, float) and math.isnan(self.cells[key].computed)):
                print "#ERR"
            else:
                print str(self.cells[key].computed)

    def no_decimal(self, i):
        return (str(i)[-2:] == '.0' and str(i)[:-2] or str(i))

    def postfix(self, expression):
        #TODO fails on 3 1 1 -
        #BUG "18 4 --" fails
        #BUG " " fails
        #TODO return int or float
        """Computes the self.postfix expression of a string of numbers.
        >>> sheet = Sheet()
        >>> print sheet.postfix("3 1 -")
        2.0
        >>> print sheet.postfix("5 1 2 + 4 * + 3 -")
        14.0
        >>> print sheet.postfix("4 2 5 * + 1 3 2 * + /")
        2.0
        >>> print sheet.postfix("5 2 %")
        1.0
        >>> print sheet.postfix("5 2 /")
        2.5
        >>> print sheet.postfix("5 2 //")
        2.0
        >>> print sheet.postfix("2 3 **")
        8.0
        >>> print sheet.postfix("18 4 -")
        14.0
        >>> print sheet.postfix(" ")
        #ERR
        >>> print sheet.postfix("18 4")
        #ERR
        >>> print sheet.postfix("18-4")
        #ERR
        >>> print sheet.postfix("18 4 +")
        22
        """
        if not expression or (isinstance(expression, float) and math.isnan(expression)):
            return float('NaN')
        elif (isinstance(expression, float)):
            return expression

        stack = Stack()
        tokens = deque(expression.split())
        visited = set()

        while stack or tokens:

            if tokens:
                token = self.TokenNode(tokens.popleft())

            symbol = re.match(r"^([a-z]+)([\d]+)", str(token.data))

            if not tokens and stack.len() == 1:
                val = stack.pop()
                if self.is_float(val):
                    return val
                else:
                    return float('NaN')

            elif symbol:

                if symbol.group() in visited:
                    # detected circular dependency
                    return float('NaN')

                else:
                    val = self.get_cell_value(symbol.group())
                    token.data = self.postfix(val)
                    visited.add(symbol.group())
                    stack.push(token.data)

            elif token.is_float():

                stack.push(float(token.data))

            elif token.is_operator():

                if stack.len() < 2:

                    return float('NaN')

                else:
                    expression = Expression()
                    expression.operator = token.data
                    try:
                        expression.right = float(stack.pop()) # 1st pop yields second operand
                        expression.left = float(stack.pop())  # 2nd pop yields first operand
                        return float(eval(expression))
                    except:
                        return float('NaN')
            else:
                return float('NaN')

class Stack:
    """Inits simple stack class with push and pop"""
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def show(self):
        print self.items

    def is_empty(self):
        return (self.items == [])

    def len(self):
        return len(self.items)

class Expression(object):
    def __init__(self):
        self.left = None
        self.operator = None
        self.right = None

"""
class ConstantNode(ExpressionNode):
    def __init__(self):
        self.data = None
        self.left = None
        self.right = None

class OperatorNode(ExpressionNode):
    def __init__(self):
        self.left = None
        self.operator = None
        self.right = None
"""
class Cell(object):
    """Inits cell object with raw and computed values"""
    def __init__(self, raw, col, row):
        self.raw = raw.strip()
        self.computed = None

def main():
    """TODO add this to the doctest
    >>> csv.register_dialect('spreadsheet', delimiter=',', quoting=csv.QUOTE_NONE)
    >>> string_io = StringIO.StringIO('4 2 5 * + 1 3 2 * + /, 5 1 2 + 4 * + 3 -\\n4 2 5 * + 1 3 2 * + /, a1')
    >>> sheet = Sheet()
    >>> sheet.import_csv_string(string_io.getvalue())
    >>> sheet.evaluate_postfix()
    >>> sheet.show_csv()
    2.0
    2.0
    14.0
    2.0
    """
    sheet = Sheet()
    f = args.csvfilename.pop(0)
    sheet.import_csv(f)
    sheet.evaluate_postfix()
    sheet.show_csv()

if __name__ == '__main__':
  main()

import doctest
doctest.testmod()