# 반복구문 
value = 5 
while value > 0:
    print(value)
    value -= 1

print("---for in---")
for i in range(5):
    print(i)

print("---날짜, 연도를 생성---")
print(list(range(2000, 2027)))
print(list(range(1,32)))

lst = list(range(1,11))
for item in lst:
    print(item)

print("---리스트 컴프리헨션---")
lst = list(range(1,11))
print([i**2 for i in lst if i>5])
words = ["apple", "banana", "cherry"]
print([word.upper() for word in words])

