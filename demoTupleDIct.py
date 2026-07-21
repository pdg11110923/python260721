# demo TupleDict.py

#Tuple practice
#함수 정의
def times(a,b):
    return a+b, a*b

#함수를 호출
result = times(3,4)
print (result)

print("id: %s, name: %s" %("kim", "김유신"))

args = (5,6)
print(times(*args))

#형식변환
a = set((1,2,3))
print(a)
b = list(a)
print(b)
b.append(4)
print(b)

#딕셔너리 구조(사전식 구조)
colors = {"apple":"red", "kiwi":"blue"}
#입력
colors["banana"] = "yellow"
print(colors)
print(len(colors))
#수정
colors["apple"] = "blue"
#삭제
del colors["kiwi"]
print(colors)
print(colors.items())

#반복문
for item in colors.items():
    print(item)

for k,v in colors.items():
    print(k,v)
