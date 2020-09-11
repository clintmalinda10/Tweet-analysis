import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

def extract_data():
    conn = sqlite3.connect("tweets.db")
    c = conn.cursor()
    insert_query = "SELECT misspelt FROM corona"
    c.execute(insert_query)
    misspelt = c.fetchall()
    for i in range(len(misspelt)):
        misspelt[i] = int(misspelt[i][0])

    return misspelt

def extract_off():
    conn = sqlite3.connect("tweets.db")
    c = conn.cursor()
    insert_query = "SELECT profanity FROM corona"
    c.execute(insert_query)
    data = c.fetchall()
    off = []
    for i in range(len(data)):
        off.append(data[i][0])
    return off

def str_to_int(array):
    for i in range(len(array)):
        array[i] = int(array[i])

    return array

def count_off(array):
    off = []
    non_off = []
    for i in range(len(array)):
        if array[i] == 'offensive':
             off.append(array[i])
        else:
            non_off.append(array[i])
    return off, non_off

def offandmis():
    sum_non = 0
    sum_off = 0
    for i in range(len(off)):
        if off[i] == 'offensive':
            sum_off = sum_off + misspelt[i]
        else:
            sum_non = sum_non + misspelt[i]
    return sum_non, sum_off

#Offensive words
a = extract_off()
count = count_off(a)
non_off = count[1]
off = count[0]
off = np.array(off)
non_off = np.array(non_off)
names = ['offensive', 'non_offensive']
values = [len(off), len(non_off)]
fig = plt.figure(figsize=(9,3))
ax = fig.add_axes([0,0,1,1])
ax.axis('equal')
ax.pie(values, labels = names, autopct='%1.2f%%')
plt.title('Non and offensive tweets')
plt.show()

#Misspelt words
a = extract_data()
#print(type(a))
sum = 0
misspelt = np.array(a)
std_dvt = np.std(misspelt)
avg = np.average(misspelt)
for i in misspelt:
    sum = sum + i
print('*-------------------------------Misspelt and Corrected words-------------------------------------*')
print('My data set had a total number of ',sum,' misspelt words which were corrected.' )
print('The standard deviation of the number of misspelt words ',std_dvt)
print('The average of misspelt words per tweet were',avg)
print('*------------------------------------------------------------------------------------------------*')

print('*---------------------misspelt words in offensive and non-offensive tweets-----------------------*')
a = offandmis()
values = [a[1], a[0]]
plt.figure(figsize=(9,3))
plt.ylabel('Misspelt words')
plt.bar(names,values)
plt.title('misspelt words in offensive and non-offensive tweets')
plt.show()
print('*------------------------------------------------------------------------------------------------*')
