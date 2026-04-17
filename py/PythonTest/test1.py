a = 4
b = 3

print(a/b)
print(a//b)

c='你叫什么名字 ,'
print(c[0:3:2])

d=[1,2,3,4]
print(d[0])
print(d[0:])
#print(type(d[0])+" "+type(d[0:]))
print(str(type(d[0])) + " " + str(type(d[0:])))

print(c*4)

e='Admain'
print(e.upper())
print(e.replace('a','c'))
print(e.find('a'))

t=('你好',2)
print(type(t))

map={}
map['book1']=123
map['book2']='你好'
map['book3']=12.4
map['book4']=('你好',2)
map[('book5')]=('你好',3)


print(map['book1'])
print(map['book2'])
print(map['book3'])
print(map['book4'])
print(map[('book5')])


print(map.keys())

del (map['book1'])

print(map.keys())
print(map.values())

#set=set()
#set.add(1)
#set.add('nihao')
#for i in set:
#    print(i)

set1=set()
set2=set()

set1.add(1)
set1.add(2)
set1.add(3)

set2.add(2)
set2.add(4)
#set2.add(3)

print(set1&set2)
print(set2.issubset(set1))
print(4 in set1)
print(4 in set2)

r = range(1, 10)
print(r)

for i in range(10):
    print(str(i)+" ;")

def max(a, b):
    if a > b:
        return a
    else:
        return b

print(max(1, 2))

def fun1(par1,par2):
    print('方法1')
    print('par1:'+par1)
    print('par2:'+par2)
    print("end1")

def fun2(par1, *par2):
    print('方法2')
    print('par1:' + par1)
    print('par2:' + str(par2))
    print(type(par2))
    print(par2[1])
    print("end2")

def fun3(par1,**par2):
    print('方法3')
    print('par1:'+par1)
    print('par2:'+str(par2))
    print(type(par2))
    print(par2['a'])
    print("end3")

fun1('1','2')
print()
fun2('1','2','3')
print()
fun3('1',a='2',b='3')
