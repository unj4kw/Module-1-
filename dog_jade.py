#header
#step16- import our dogs from the .csv file 
import csv
with open("dog data set.csv", newline="") as f:
    reader = csv.reader(f)
    headers = next(reader) # Get the first row
    for h in headers:
        print(h)
@classmethod 
def instantiate_from_csv(cls, filename: str):
    with open(filename, encoding="utf8") as f:
        reader = csv.DictReader(f)
        rows_of_dogs = list(reader)
        for row in rows_of_dogs:
                    Dog(
                    breed = row['Name'],
                    age = (int(row['Minimum Life Span']) + int(row['Maximum Life Span'])/2),
                    weight = (int(row['Minimum Weight']) + int(row['Maximum Weight'])/2),
                    breedgroup = row['Breed Group']
                )            
#step 4- define a class of objects 
class Dog:
#step 13- for loop, to make a list of our dogs 
    all_dogs = []
#step 5- special method: a constructor __init__ that lists the different attributrs that a dog can have
    def __init__(self, breed: str, age: float, weight: float, name: str = "n/a", breedgroup: str = "n/a"): 
        self.breed = breed
        self.age = age
        self.weight = weight
        self.name = name
        self.breedgroup = breedgroup
#step13-class variable that will hold all the dog objects we create. This is a list that will hold all the dog objects we create.
        Dog.all_dogs.append(self)
#step 14- class method is inside the class and is a method that is called on the class itself, not on an instance of the class. It is defined with the @classmethod decorator and takes the class as its first argument (cls). This method will sum the ages of all the dogs in the all_dogs list.
    @classmethod
    def sum_ages(cls):
        total = 0
        for dog in Dog.all_dogs:
            total += dog.age
        return total
#step 8- special method: a __repr__ method that will return a string representation of the object when we print it.
    def __repr__(self):  
        return f"{self.name}: ({self.breed} | {self.breedgroup} | {self.age} | {self.weight})" 
#step 11- getter method/instance method which calls on a single object and returns the age of that object.
    def get_age(self): 
        return self.age
    @classmethod 
    def instantiate_from_csv(cls, filename: str):
     
        #the code below will open the .csv file and create a list of all the rows in your spreadsheet
        
        with open(filename, encoding="utf8") as f:
            reader = csv.DictReader(f)
            rows_of_dogs = list(reader)
        
        #the code below will create a dog object for each row, based on the data: 
        
            for row in rows_of_dogs:
                    Dog(
                    breed = row['Name'],
                    age = (int(row['Minimum Life Span']) + int(row['Maximum Life Span'])/2),
                    weight = (int(row['Minimum Weight']) + int(row['Maximum Weight'])/2),
                    breedgroup = row['Breed Group'])
#step 17- 
    @classmethod 
    def get_dog(cls, breed):
        for dog in Dog.all_dogs:
            if dog.breed == breed:
                return dog
#step 20- 

    @classmethod
    def filter(cls, list, breed:str ="any", age:int ="any", weight:int ="any", name:str ="any", breedgroup:str ="any"):
            all_dogs = list
            remove_list = []
            attr_list = (
                        breed,
                        age,
                        weight,
                        name,
                        breedgroup
                        )
            attr_name = (
                        "breed",
                        "age",
                        "weight",
                        "name",
                        "breedgroup"
                        )
            for attr in range(len(attr_list)):
                if attr_list[attr] != "any":
                    for dog in all_dogs:
                        if getattr(dog,attr_name[attr]) != attr_list[attr]:
                            remove_list.append(dog)
                    all_dogs = [dog for dog in all_dogs if dog not in remove_list]
                    remove_list.clear()

            return all_dogs



            

