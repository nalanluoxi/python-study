
class Student:
    name=""
    age=0
    def __init__(self,name ,age):
        self.name = name
        self.age = age

    def printAll(self):
        print('name:'+self.name)
        print('age:'+str(self.age))
        print()


stu1=Student("lisi",18)
stu1.printAll()
#print(Student.__dict__)
#print(stu1.__dict__)
print("输出文件")
path="/Users/nalan/IdeaProjects/python-test/py/PythonTest/doc/textData1.txt"
file = open(path, "a")
#read = file.read()
#read =file.readline()

str="新写入内容2\n"
#print(read)
file.write(str)
file.close()








