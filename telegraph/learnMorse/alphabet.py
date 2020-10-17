from collections import OrderedDict

from telegraph.common.symbols import Symbol as s


letters = OrderedDict()
letters['A'] = [s.DIT, s.DAH]
letters['B'] = [s.DAH, s.DIT, s.DIT, s.DIT]
letters['C'] = [s.DAH, s.DIT, s.DAH, s.DIT]
letters['D'] = [s.DAH, s.DIT, s.DIT]
letters['E'] = [s.DIT]
letters['F'] = [s.DIT, s.DIT, s.DAH, s.DIT]
letters['G'] = [s.DAH, s.DAH, s.DIT]
letters['H'] = [s.DIT, s.DIT, s.DIT, s.DIT]
letters['I'] = [s.DIT, s.DIT]
letters['J'] = [s.DIT, s.DAH, s.DAH, s.DAH]
letters['K'] = [s.DAH, s.DIT, s.DAH]
letters['L'] = [s.DIT, s.DAH, s.DIT, s.DIT]
letters['M'] = [s.DAH, s.DAH]
letters['N'] = [s.DAH, s.DIT]
letters['O'] = [s.DAH, s.DAH, s.DAH]
letters['P'] = [s.DIT, s.DAH, s.DAH, s.DIT]
letters['Q'] = [s.DAH, s.DAH, s.DIT, s.DAH]
letters['R'] = [s.DIT, s.DAH, s.DIT]
letters['S'] = [s.DIT, s.DIT, s.DIT]
letters['T'] = [s.DAH]
letters['U'] = [s.DIT, s.DIT, s.DAH]
letters['V'] = [s.DIT, s.DIT, s.DIT, s.DAH]
letters['W'] = [s.DIT, s.DAH, s.DAH]
letters['X'] = [s.DAH, s.DIT, s.DIT, s.DAH]
letters['Y'] = [s.DAH, s.DIT, s.DAH, s.DAH]
letters['Z'] = [s.DAH, s.DAH, s.DIT, s.DIT]

numbers = OrderedDict()
numbers['0'] = [s.DAH, s.DAH, s.DAH, s.DAH, s.DAH]
numbers['1'] = [s.DIT, s.DAH, s.DAH, s.DAH, s.DAH]
numbers['2'] = [s.DIT, s.DIT, s.DAH, s.DAH, s.DAH]
numbers['3'] = [s.DIT, s.DIT, s.DIT, s.DAH, s.DAH]
numbers['4'] = [s.DIT, s.DIT, s.DIT, s.DIT, s.DAH]
numbers['5'] = [s.DIT, s.DIT, s.DIT, s.DIT, s.DIT]
numbers['6'] = [s.DAH, s.DIT, s.DIT, s.DIT, s.DIT]
numbers['7'] = [s.DAH, s.DAH, s.DIT, s.DIT, s.DIT]
numbers['8'] = [s.DAH, s.DAH, s.DAH, s.DIT, s.DIT]
numbers['9'] = [s.DAH, s.DAH, s.DAH, s.DAH, s.DIT]

morse = OrderedDict()
morse.update(letters)
morse.update(numbers)
