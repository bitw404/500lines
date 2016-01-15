# 字符串反序输出。

from pyds.basic import Stack

def revstring(mystr):
    s = Stack()
    newstr = ''
    for ch in mystr:
        s.push(ch)
    while not s.is_empty():
        newstr += s.pop()
    return newstr

print(revstring('hello'))