#!/usr/bin/env python -tt

import sys, csv, operator, argparse, re, logging
from collections import deque
from string import lowercase # imports 'abcdefghijklmnopqrstuvwxyz'

parser = argparse.ArgumentParser(description='Spreadsheet with Postfix RPV Eval by Scott Coleman')

# Allow any number of additional arguments.
parser.add_argument(nargs='*', action='store', dest='inputs',
                    help='input filenames')

args = parser.parse_args()
# print args.__dict__

ARITHMETIC_OPERATORS = {
    '+': operator.add, '-': operator.sub, '*': operator.mul,
    '/': operator.div, '//': operator.floordiv,
    '%': operator.mod, '**': operator.pow,
    '<<': operator.lshift, '>>': operator.rshift
    }

""" Limitation: Note that '__pow__()' should be defined to accept an optional third
argument if the ternary version of the built-in 'pow()' function is to be supported.
"""

def base_26_generator(x):
    """ Base 26 conversion functions borrowed from Stack overflow
            http://bit.ly/10U0IUE
    """
    assert re.search(r"^\d+", str(x)), "(Error) digits only"
    if x == 0: yield x
    while x > 0:
        yield x % 26
        x //= 26

def int_to_base_26_chr(x):
    """ Return lowercase character in base 26 """
    return ''.join(lowercase[i] for i in reversed(list(base_26_generator(x))))

class Sheet(object):
    """ Spreadsheet class """
    def __init__(self):
        self.cells = {}
        self.cols = None

    def update(self, cell, row, col):
        """ Update cell in the spreadsheet using row/col pair """
        key = str(int_to_base_26_chr(col)) + str(row)
        self.cells[key] = Cell(cell, row, col)

    def get_cell(self, cell_row):
        """ Returns raw not yet computed value of the cell if found """
        #        if self.cells[cell_row].computed:
        #            return self.cells[cell_row].computed
        #        else
        #TODO (Scott) test that row/col is in range
        #TODO (Scott) Handle lower and upper
        if cell_row in self.cells:
            return self.cells[cell_row].raw

    def import_csv(self, filename):
        """Read CSV file and update cells"""
        csv.register_dialect('spreadsheet', delimiter=',', quoting=csv.QUOTE_NONE)
        with open(filename, 'rb') as csv_file:
            reader = csv.reader(csv_file, 'spreadsheet')
            try:
                for row_id, csv_row in enumerate(reader):
                    if row_id == 1: # get columns
                        self.cols = len(csv_row)
                    for col_id, csv_cell in enumerate(csv_row):
                        self.update(csv_cell, row_id + 1, col_id + 1)

            except csv.Error as e:
                sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))

    def compute(self):
        """Parse tokens as postfix expressions"""
        for key in self.cells:
            logging.info("Post fix key: " + str(key))
            logging.info("Expression: " + str(self.cells[key].raw))
            logging.info("Postfix output: " + str())
            self.cells[key].computed = postfix(str(self.cells[key].raw), self)

    ##TODO add print for raw/computed, use cell objects instead
    def show(self):
        """Print raw expression list and [computed value]"""
        for key in self.cells:
            print str(self.cells[key].raw) + " [" + str(self.cells[key].computed) + "]"

def is_numeric(token):
    """Returns true if token looks like a float or int, else return nothing
    >>> is_numeric("5")
    True
    >>> is_numeric("5123123123")
    True
    >>> is_numeric("5.0")
    True
    >>> is_numeric("-5.0")
    True
    >>> is_numeric("+5.0")
    True
    >>> is_numeric("-5")
    True
    >>> is_numeric("+")
    False
    >>> is_numeric("-")
    False
    >>> is_numeric(" ")
    False
    """
    if re.search(r"^(\+|-)?([0-9]+\.?[0-9]*|\.[0-9]+)([eE](\+|-)?[0-9]+)?", str(token)):
        return True
    else:
        return False

def is_cell_reference(token):
    """Returns true if token appears to be a cell reference / identifer"""
    return re.search("^[a-z]+[\d]+", token)

def is_operator(token, operators=ARITHMETIC_OPERATORS):
    """Returns true if token appears to be an arithmatic operator"""
    if token in operators:
        return True

def postfix(expression, sheet = Sheet(), operators=ARITHMETIC_OPERATORS):
    """Computes the self.postfix expression of a string of numbers.
    >>> print postfix("+")
    #ERR
    >>> print postfix("-")
    #ERR
    >>> print postfix("5")
    5
    >>> print postfix("c1")
    #ERR
    >>> print postfix("5 1 2 + 4 * + 3 -")
    14.0
    >>> print postfix("4 2 5 * + 1 3 2 * + /")
    2.0
    >>> print postfix("2 3 8 * + 4 48 4 2 + / 6 * + -")
    -26.0
    >>> print postfix("5 2 %")
    1.0
    >>> print postfix("5 2 /")
    2.5
    >>> print postfix("5 2 //")
    2.0
    >>> print postfix("2 3 **")
    8.0
    >>> print postfix("18 4 -")
    14.0
    >>> print postfix("15 5 +")
    20.0
    """
    #TODO check for "random chars, --, invalid postfix, etc. this will be"
    if not expression:
        return "#ERR"

    logging.info("Evaluate postfix: " + str(expression))
    stack = Stack()
    tokens = deque(expression.split())

#    print len(tokens)
#    print is_numeric(tokens)
#    print tokens[-1]
    if len(tokens) == 1 and is_numeric(tokens[-1]):
        stack.push(tokens.popleft())

    if len(tokens) == 1 and (not is_numeric(tokens[-1])):
        return "#ERR"

    while tokens or stack.items:
        logging.info("Tokens:" + str(tokens))
        logging.info("Postfix stack: " + str(stack.items))

        if not tokens and stack.len() == 1:
            return stack.pop()

        if tokens:
            token = tokens.popleft()
            logging.info("Token from expression queue: " + token)

            # if it is a number then push onto stack
            if is_numeric(token):

                stack.push(float(token))

            elif is_cell_reference(token):

                cellref = re.match(r"^([a-z]+)([\d]+)", token)
                val = sheet.get_cell(cellref.group())
                stack.push(postfix(val, sheet))

            elif is_operator(token):

                logging.info("Perform operation... ")
                logging.info(token)
                logging.info(stack.items)

#                    result = self.calculate(operators[token], one, two)
                assert stack.len() >= 2, \
                    "(Error) The user has not input sufficient values in the expression"
                operator = operators[token]
                right = stack.pop() # 1st pop yields second operand
                left = stack.pop() # 2nd pop yields first operand

                assert re.search(r"[-+]?[0-9]*\.?[0-9]+", str(left)), str(left) \
                                + "(Error) Must be a valid number"
                assert re.search(r"[-+]?[0-9]*\.?[0-9]+", str(right)), str(right) \
                                + "(Error) Must be a valid float or "

                logging.info("Evaluate: operator(left operand: %s, right operand: %s)"
                            % (str(left), str(right)))

                # Evaluate the operator, with the values as arguments.
                result = operator(*[float(left), float(right)])

                # Push the returned results, if any, back onto the stack.
                stack.push(float(result))

            else:
                assert "(Error) The user has not input sufficient vfalues in the expression"

        elif (stack.len() == 1):
            return stack.pop()

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

class Cell(object):
    """Inits cell object with raw and computed values"""
    def __init__(self, raw, col, row):
        self.raw = raw.strip()
        self.computed = None
        self.col = col
        self.row = row

def main():
    filename = args.inputs[0]
    sheet = Sheet()
    sheet.import_csv(filename)
    sheet.compute()
    sheet.show()

if __name__ == '__main__':
  main()

import doctest
doctest.testmod()