#strings in python

name="Dora"
print("hello"+name)

#print("this is very "unrealistic" situation")  #Error occur
print('this is very "unrealistic" situation')
print("this is very \"unrealistic\"situation")

#multiline string
A='''hey
I am good
what about you'''
print(A)

B="""hey
I am good
what about you"""
print(B)

#string Indexing
c="Nobita"
print(c[0])
print(c[1])
print(c[2])

print("lets use a for loop\n")
for character in name:
    print(character)