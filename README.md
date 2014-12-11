postfix-spreadsheet
===================
Notes:
- Handle unicode? No, we can assume that it is postfix.
- sniff csv delimeter first?
- specific issues with postfix?
- generate key/value index  (A2, B4, etc - letters refer to columns, numbers to rows).
- Support the basic arithmetic operators +, -, *, / ( use stack )
- write output to stdout or to file?

Handling cell references (A1, A2, B1, B2)
Order of operations: 
- check for circular references
- if cell has reference to 
- recursive function?
- 
Ensure that input is escaped properly
Options for dealing with references
- just search and replace with value.
On the first pass, just do calculations for fields with no references
Take care of maximum file size
Edge cases: file size, no operator, other whitespace, circular reference, too big for memory

# Alternative alphabet keys - any valid size, 
# src: http://stackoverflow.com/questions/9233219/how-to-create-a-list-of-alphabets-to-use-with-grid-coordinates-ie-a-b-z
# alternative - do base26 conversions.
# COLS = reduce(lambda x,y:x+y, 
#              map(lambda N:[''.join(x) for x in itertools.product(string.lowercase, repeat=N)], range(1,4))
#              )

