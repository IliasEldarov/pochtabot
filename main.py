import math
#from suds import *

# Section 1. Recursion, call stack
def factorial_rec(x):
    if x == 0:
        return 1
    return x * factorial_rec(x - 1)


print(factorial_rec(30))

from suds import *

# 1.2 - Calculate 3000! Solve the problem you face without rewriting
from suds import *
sys.setrecursionlimit(350)
print('300!', factorial_rec(300))


# 1.3 What about 30000! calculation? Provide a non-recursive function
# #and compare the answer with math.factorial one
import math

def factorial_non_recursion(x):
    if x == 0 or x == 1:
        return 1
    res = 1

    for i1 in range(1, x + 1):
        res = res * i1
    return res


result = factorial_non_recursion(30000)
result2 = math.factorial(30000)
print('Are they identical? ', 'Yes!' if result == result2 else 'no')

age_spans = [
    {'age': '< 5', 'percent': 1.09}, {'age': '5 - 10', 'percent': 14.08},
    {'age': '11 - 17', 'percent': 53.06}, {'age': '18 - 24', 'percent': 24.1},
    {'age': '25 - 34', 'percent': 5.04}, {'age': '35 - 44', 'percent': 1.58},
    {'age': '45 - 54', 'percent': 0.65}, {'age': '55 - 64', 'percent': 0.29},
    {'age': '64 <', 'percent': 0.1}
]

# 2.1 - Section 2 solution
max_percent = 0
max_age = 0
for i in age_spans:
    if max_percent < i['percent']:
        max_percent = i['percent']
        max_age = i['age']
print(max_age)

# Section 3. "operator" module
# 3.1 - Section 3 solution
input_str = '3/2'
print(eval(input_str))

# Section 5. Programming paradigms
# 5.1 - Solve it in declarative style: provide solution based on loops *
rows, cols = 1, 4
array = [[0 for x in range(cols)] for y in range(rows)]
for i_row in range(rows):
    for i_cols in range(cols):
        array[i_row][i_cols] = (i_row + 1) * (i_cols + 1)
print(array)

# 5.2 - Solve it in functional style: one-string
# solution (excluding input reading) *
array2 = [[(i_rows + 1) * (i_cols + 1) for i_cols in range(cols)] for i_rows
          in range(rows)]
print(array2)


#  Decorators
'''4.1 - Create a retry-decorator without arguments 
which calls function 3 times in case the function 
returns None ("@retry_if_none") *
'''
def retry_if_none(f):
    if f(0) == None:
        print('Decorator  without arg started')
        f(1)
        f(2)
        f(3)
        print('Decorator  without arg finished')


'''
4.2 - Create a parameterized retry-decorator which 
calls function N times in case the function returns 
None ("@retry_if_none(10)") *
'''
#  if  the  function returns  0 it  will be called  by  decorator n times
#  this decorator  can be  call with  and  without  args
def retry_if_none_arg(n=1):
    def retry_if_none_decorator(function):
        def wrapper(*args, **kwargs):
            l_result = None
            if function(*args, **kwargs) is None:
                print('Decorator  with  arg started', n)
                for li in range(n):
                    l_result = function(*args, **kwargs)
                print('Decorator  with  arg ended')
            return l_result
        return wrapper
    return retry_if_none_decorator


@retry_if_none_arg(3)
@retry_if_none_arg()
def my_function(cnt: int) -> int:
    print('my_function called with  arg', cnt)
    if cnt == 0:
        return None
    return cnt

my_function(0)
