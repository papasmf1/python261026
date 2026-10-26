# 딕셔너리연습.py

d = {"apple":"red","banana":"yellow"}
print(len(d))
#검색
print(d["apple"])
#입력
d["kiwi"] = "green"
#수정
d["apple"] = "yellow"
print(d)
#삭제
del d["apple"]
print(d)
for item in d.items():
    print(item)

#불린형식
isRight = True 
print(type(isRight))
print(1 < 2)
print(1 > 2)
x = 5 
y = 6 
print(x == y)
print(x != y)
print(not isRight)
print(True and True and True)
print(True and True and False)
print(True or False or False)

#연산자
print( 5 / 2)
print( 5 // 2)
print( 5 % 2)
print( 4 % 2)
print( 2**10 )

