#main method where we will run the code
import csv
#step 6- tell python to import everything from the dog_jade.py file
from dog_jade import Dog
import matplotlib.pyplot as plt
from scipy import stats
import numpy as np  
import statistics

import matplotlib.pyplot as plt 
from scipy import stats
import numpy as np
import statistics
import pandas as pd 

Dog.instantiate_from_csv("dog data set.csv")
with open("dog data set.csv", newline="") as f:
        reader = csv.reader(f)
        headers = next(reader) # Get the first row
        for h in headers:
            print(h)
#step 7- dog-type objects. use the constructor to construct each dog according to the attributes we specified in the constructor.            
dog1 = Dog("German Pinscher", 1, 43.0, "Rizzo")  

dog2 = Dog("Golden Retriever", 3, 64.0, "Callypso")

dog3 = Dog("Chihuahua", 2, 15.6, "Cheeto")

dog4 = Dog("Blue Tick Hound", 4, 52.5)

dog5 = Dog("Black Laborator Retriever", 6, 73.0)
#step 9- call the representer in main.py to print the string representation of the dog objects.
print(dog1)
#step 10 and 12- call the get_age method to get the age of dog2
print(dog2.get_age())
#step 13- for loop to sum the ages of all the dogs in the all_dogs list. This is a class variable that will hold all the dog objects we create. This is a list that will hold all the dog objects we create.
total = 0
for dog in Dog.all_dogs:
    total += dog.age
print(total)
print(f"Total age of all dogs is: {total}")
#step 15- call the class method  
print(Dog.sum_ages())

#step 18 
print(Dog.get_dog("Pug"))
#step 19 
Dog.all_dogs.sort(key=Dog.get_age, reverse=False)
for dog in Dog.all_dogs:
    print(dog)
    working_dogs = range(len(Dog.filter(Dog.all_dogs, breedgroup = "Working")))
    print(f'Number of Working Dog breeds = {len(working_dogs)}')
    toy_dogs = range(len(Dog.filter(Dog.all_dogs, breedgroup = "Toy")))
    print(f'Number of Toy Dog breeds = {len(toy_dogs)}')
    age_Working_dogs = []
    age_Toy_dogs = []
    for dog in Dog.filter(Dog.all_dogs, breedgroup = "Working"):
        age_Working_dogs.append(dog.age)
    for dog in Dog.filter(Dog.all_dogs, breedgroup = "Toy"):
        age_Toy_dogs.append(dog.age)
    x_Working_dog_bar = (statistics.mean(age_Working_dogs))
    x_Toy_dog_bar = (statistics.mean(age_Toy_dogs))

    age_Working_dog_stdev = (statistics.stdev(age_Working_dogs))
    age_Toy_dog_stdev = (statistics.stdev(age_Toy_dogs))
    print(f'x_Working_dog_bar = {x_Working_dog_bar}, age_Working_dog_stdev {age_Working_dog_stdev}')
    print(f'x_Toy_dog_bar = {x_Toy_dog_bar}, age_Toy_dog_stdev {age_Toy_dog_stdev}')
    Dog_breedgroup_cols = ['Working Dogs', 'Toy Dogs']
    mean_breedgroup = [x_Working_dog_bar, x_Toy_dog_bar]
    stdev_breedgroup = [age_Working_dog_stdev, age_Toy_dog_stdev]
    yerr = [np.zeros(len(mean_breedgroup)), stdev_breedgroup]
    plt.bar(Dog_breedgroup_cols, mean_breedgroup, yerr=yerr, capsize=10, color=["blue", "orange"])
    plt.title("Average Lifespan of Breedgroups")
    plt.xlabel("Breedgroup")
    plt.ylabel("Average Lifespan (age)")
    plt.show()

    breed_age = []
    breed_weight = []
    for dog in Dog.all_dogs:
        breed_age.append(dog.age)

    for dog in Dog.all_dogs:
        breed_weight.append(dog.weight)
    X = breed_age  # Independent variable
    y = breed_weight  # Dependent variable

    plt.scatter(X, y, color='blue')
    plt.xlabel('Average Lifespan')
    plt.ylabel('Average Weight')
    plt.title('Scatter Plot of Average Lifespan vs Average Weight')
    plt.show()

t_stat, p_val= stats.ttest_ind(age_Working_dogs, age_Toy_dogs)

print(f't_stat = {t_stat}, p_val = {p_val}')
plt.bar(Dog_breedgroup_cols, mean_breedgroup, yerr=yerr, capsize=10, color=["blue", "orange"])
plt.title("Average Lifespan of Breedgroups")
plt.xlabel("Breedgroup")
plt.ylabel("Average Lifespan(age)")
y_max= max(mean_breedgroup)+ max(stdev_breedgroup)*.4
plt.text(
0.5, y_max, 
f"t={t_stat:.2f}\np= {p_val:.3e}",
ha='center', va='bottom')
plt.show()

