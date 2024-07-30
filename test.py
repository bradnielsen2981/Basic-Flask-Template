'''avariable = 13 #a variable
alist = ['a','b','c','d','e'] #list - a container of variables
print(alist[4]) #4th item  - 0 based index
lengthoflist = len(alist) #length of list
print(alist[lengthoflist-1]) #last item
for item in alist: #iterate through list (shortcut)
    print(item)
for count in range(len(alist)):
    print(count)
    print(alist[count])'''

#Python dictionaries - are also a container of variables
adict = { 'name':'John' , 'age':25 }
print(adict['name'])  #index has a value which is the key
print(adict['age']) 
adict['drug history'] = 'weed'
print(adict)

emptylist = []
for i in range(0,10):
    emptylist.append(adict.copy())

d = emptylist[5] #dictionary
d['name'] = 'Jane'

print(emptylist)
