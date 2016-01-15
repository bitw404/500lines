# 判断开闭括号是否完全匹配。

from pyds.basic import Stack

def matches(open, close):
    opens = '([{'
    closers = ')]}'
    return opens.index(open) == closers.index(close)

def pair_check(pair_str):
    s = Stack()
    flag = True

    for pair in pair_str:
        if pair in '([{':
            s.push(pair)
        elif s.is_empty():
            flag = False
            break
        elif not matches(s.peek(), pair):
            flag = False
            break
        else:
            s.pop()

    if flag and s.is_empty():
        print('ok')
    else:
        print('fuck')

pair_check('(())')
pair_check('((())')
pair_check('(()))(')

pair_check('(()]')
pair_check('{{([])}}')