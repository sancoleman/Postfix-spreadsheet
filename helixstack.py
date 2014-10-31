#!/usr/bin/env python

import operator
import doctest


class Stack:
    def __init__(self):
        """Initialize a new empty stack."""
        self.items = []       

    def push(self, item):
        """Add a new item to the stack."""
        self.items.append(item)

    def pop(self):
        """Remove and return an item from the stack. The item 
        that is returned is always the last one that was added.
        """
        return self.items.pop()

    def is_empty(self):
        """Check whether the stack is empty."""
        return (self.items == [])


# Map supported arithmetic operators to their functions
ARITHMETIC_OPERATORS = {"+":"add", "-":"sub", "*":"mul", "/":"div", "%":"mod", "**":"pow", "//":"floordiv"}

def postfix(expression, stack=Stack(), operators=ARITHMETIC_OPERATORS):
    """Postfix is a mathematical notation wherein every operator follows all 
    of its operands. This function accepts a string as a postfix mathematical 
    notation and evaluates the expressions. 

    1. Starting at the beginning of the expression, get one term 
       (operator or operand) at a time.
       * If the term is an operand, push it on the stack.
       * If the term is an operator, pop two operands off the stack, 
         perform the operation on them, and push the result back on 
         the stack.

    2. When you get to the end of the expression, there should be exactly 
       one operand left on the stack. That operand is the result.

    See http://en.wikipedia.org/wiki/Reverse_Polish_notation

    >>> expression = "1 2 +"
    >>> postfix(expression)
    3
    >>> expression = "5 4 3 + *"
    >>> postfix(expression)
    35
    >>> expression = "3 4 5 * -"
    >>> postfix(expression)
    -17
    >>> expression = "5 1 2 + 4 * + 3 -"
    >>> postfix(expression, Stack(), ARITHMETIC_OPERATORS)
    14

    """
    if not isinstance(expression, str):
        return
    for val in expression.split(" "):
        if operators.has_key(val):
            method = getattr(operator, operators.get(val))
            # The user has not input sufficient values in the expression
            if len(stack.items) < 2:
                return
            first_out_one = stack.pop()
            first_out_two = stack.pop()
            operand = method(first_out_two, first_out_one)
            stack.push(operand)
        else:
            # Type check and force int
            try:
                operand = int(val)
                stack.push(operand)
            except ValueError:
                continue
    return stack.pop()


if __name__ == '__main__':
    doctest.testmod()