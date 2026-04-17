GLOBAL_A='你好,这是a'
GLOBAL_B='你好,这是b'

name='名字'

def setName(newName):
    global name
    name = newName

def printName():
    print('名字是:', name)