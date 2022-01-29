import math
from suds import *

age_spans = {
    '< 5': 1.09,
    '5 - 10': 14.08,
    '11 - 17': 53.06,
    '18 - 24': 24.1,
    '25 - 34': 5.04,
    '35 - 44': 1.58,
    '45 - 54': 0.65,
    '55 - 64': 0.29,
    '64 <': 0.1
}

#print(list(filter(lambda x: age_spans[x] == max(age_spans.values()), age_spans.keys())))

input_str = '3 - 2'
print(eval(input_str))