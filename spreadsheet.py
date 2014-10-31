#!/usr/bin/env python -tt

import sys, csv, operator, argparse, re, string, math
from collections import deque
from string import lowercase # imports 'abcdefghijklmnopqrstuvwxyz'

parser = argparse.ArgumentParser(description='Spreadsheet by Scott Coleman')

# Allow any number of additional arguments.
parser.add_argument(nargs='*', action='store', dest='inputs',
                    help='input filenames')

args = parser.parse_args()
# print args.__dict__

ARITHMETIC_OPERATORS = {
    '+': operator.add, '-': operator.sub, '*': operator.mul, 
    '/': operator.div, '//': operator.floordiv,     
    '%': operator.mod, '**': operator.pow, '<<': operator.lshift, 
    '>>': operator.rshift
    }

""" Limitation: Note that '__pow__()' should be defined to accept an optional third
argument if the ternary version of the built-in 'pow()' function is to be supported.
"""

"""
Base 26 conversion functions from 
http://stackoverflow.com/questions/9233219/how-to-create-a-list-of-alphabets-to-use-with-grid-coordinates-ie-a-b-z
"""
def base_26_generator(x):
    if x == 0: yield x
    while x > 0:
        yield x % 26
        x //= 26    

def int_to_base_26_chr(x):
    return ''.join(lowercase[i] for i in reversed(list(base_26_generator(x))))

class Sheet:
    """Spreadsheet class
    """
    def __init__(self):
        self.cells = {}
        self.cols = None
#        self.col_idx = base_26_generator(cols)
#        self.col_idx = [base_26_chr(x) for x in range(len(row))]
#        self.cols = [base_26_chr(x) for x in range(len(row))]

    def push(self, cell, row, col):
        key = str(int_to_base_26_chr(col)) + str(row)
        self.cells[key] = Cell(cell, row, col)

    def update(self, cell):
        self.cells.update(cell)

    def get_cell(self, cell_row):
#        if self.cells[cell_row].computed:
#            return self.cells[cell_row].computed
#        else
        if cell_row in self.cells:
            return self.cells[cell_row].raw

    def import_csv(self, filename): 
        csv.register_dialect('spreadsheet', delimiter=',', quoting=csv.QUOTE_NONE)
        row_id = 1
        col_id = 0
        with open(filename, 'rb') as csv_file:
            reader = csv.reader(csv_file, 'spreadsheet')
            try:
                for csv_line in reader:
                    if row_id == 1: # get columns
                        self.cols = len(csv_line)
                    for csv_value in csv_line:
                        self.push(csv_value, row_id, col_id)
                        col_id += 1
                    col_id = 0
                    row_id += 1

            except csv.Error as e:
                sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))        

    def compute(self):
        for key in self.cells:
            print "Post fix key: " + str(key)
            print "Expression: " + str(self.cells[key].raw)
            print "Postfix output: " + str()
            self.cells[key].computed = self.postfix(str(self.cells[key].raw))

    ##TODO add print for raw/computed, use cell objects instead
    def show(self):
        for key in self.cells:                
            print str(self.cells[key].raw) + " [" + str(self.cells[key].computed) + "]"

    def postfix(self, expression, operators=ARITHMETIC_OPERATORS):

        if not expression:
            return "#ERR"

        print "Evaluate postfix: " + str(expression)
        stack = Stack()


        tokens = deque(expression.split())
        while tokens or stack.items:
            print "Tokens:" + str(tokens)
            print "Postfix stack: " + str(stack.items)

            if not tokens and stack.len() == 1:
                return stack.pop()

            if tokens:
                token = tokens.popleft()
                print "Token from expression queue: " + token

                # if it is a number then push onto stack
                if re.match("[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?", token):

                    stack.push(float(token))

                elif re.match("^([a-z])+([\d])+", token):

                    cellref = re.match("^([a-z])+([\d])+", token)
                    print cellref.group()
                    print "Lookup value: " + str(self.get_cell(cellref.group()))
                    val = self.get_cell(cellref.group())

                    stack.push(self.postfix(val))

                elif token in operators:

                    print "Perform operation... "

                    assert stack.len() >= 2, "(Error) The user has not input sufficient values in the expression"
                    print token
                    print stack.items

#                    result = self.calculate(operators[token], one, two)
                    operator = operators[token]
                    one = stack.pop()
                    two = stack.pop()

                    print "self: " + str(one)
                    print "other: " + str(two)

                    assert not math.isnan(one), "(Error) Must be a valid number"
                    assert not math.isnan(two), "(Error) Must be a valid number"                    

                    print ("Evaluate: operator(self: %s, other: %s)") % (str(one), str(two))

                    # Evaluate the operator, with the values as arguments.
                    result = operator(*[float(two), float(one)])

                    # Push the returned results, if any, back onto the stack.
                    stack.push(float(result))

                else:
                    assert "(Error) The user has not input sufficient vfalues in the expression"

            elif (stack.len() == 1):
                return stack.pop()

"""Computes the self.postfix expression of a string of numbers.

>>> print postfix("5 1 2 + 4 * + 3 -")
14.0
>>> print postfix("4 2 5 * + 1 3 2 * + /")
2.0
>>> print postfix("5 2 %")
1.0
>>> print postfix("5 2 /")
2.5
>>> print postfix("5 2 //")
2.5        
>>> print postfix("2 3 **")
8.0
>>> print postfix("18 4 -")
14.0
""" 

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