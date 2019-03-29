n = int(input("enter a number : "))
b = n
c = 0
a = 0
while c < 20:
    s = int(input("enter 19 numbers : "))
    if b<s:
        b=s
    elif b > s:
        a=s

print("biggest number is : ",b)
print("second number is : ",a)