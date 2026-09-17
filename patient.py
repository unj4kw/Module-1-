# Jenny Mejia - ccc3dq

import csv
import os
# AI Usage: To solve an error relating to not being able to locate the CSV file, Claude suggested to add "import os" at the top.
# This allowed pts_from_csv() in the code below to locate the CSV file relative to this file.

class Patient: 
    # Defines objects that represent patients in the dataset. 
    # Each patient has attributes corresponding to the columns in the CSV file.
    
    def __init__(self, donor_id, age_at_death, sex, education, years_education, apoe_genotype, cognitive_status, age_onset, age_diagnosis, thal, braak, abeta40, abeta42, ttau, ptau):
        # The constructor runs every time a new patient object is created. It initializes the attributes of the patient object with the values provided as arguments.
        # This makes it possible to access an attribute of a patient object using dot notation. For example, patient.age_at_death or patient.sex.
        
        # The following lines convert certain attributes to float if they are numbers, by running them through the _create_float method.
        self.donor_id = donor_id
        self.age_at_death = self._create_float(age_at_death)
        self.sex = sex
        self.education = education
        self.years_education = self._create_float(years_education)
        self.apoe_genotype = apoe_genotype
        self.cognitive_status = cognitive_status
        self.age_onset = self._create_float(age_onset)
        self.age_diagnosis = self._create_float(age_diagnosis)
        self.thal = thal # Thal and braak are categorical variables, so they are stored as strings.
        self.braak = braak
        self.abeta40 = self._create_float(abeta40)
        self.abeta42 = self._create_float(abeta42)
        self.ttau = self._create_float(ttau)
        self.ptau = self._create_float(ptau)

    @staticmethod
    def _create_float(value): 
        # Turns the value into a float if it is a number, otherwise returns None. 
        # This is used to handle missing or invalid values in the dataset.
        # @staticmethod means that this method does not depend on the class (self), it can take any value as input and return a float or None.
        if value is None or value == "": 
            return None
        try:
            # Attempts to convert the value to a float.
            return float(value)
        except ValueError:
            # If the value cannot be converted to a float, it returns None to avoid the error. 
            return None

    @classmethod
    def thal_score(cls, patient):
        if not patient.thal:
            return None

        # This method goes through every character in the "thal" string and only keeps the digits.
        digits = "".join(i for i in patient.thal if i.isdigit()) # Goes through every character in "thal" column and checks if it is a digit. If it is, it adds it to the "digits" string. If not, it ignores it.

        # Returns None if there is no numeric value found in the column. Otherwise, it concerse the digits found into an integer.
        return int(digits) if digits else None 


    def __repr__(self):  
        # Defines what gets shown when you print a patient or a list of patient data.
        # This builds a readable line per patient, showing the attributes separated by vertical bars.
        return f"{self.donor_id}: ({self.age_at_death} | {self.sex} | {self.education} | {self.years_education} | {self.apoe_genotype} | {self.cognitive_status} | {self.age_diagnosis} | {self.thal} | {self.braak} | {self.abeta40} | {self.abeta42} | {self.ttau} | {self.ptau})" 

    # Create patient objects from the CSV file and store them in a list. 
    # This method reads the CSV file, creates a Patient object for each row, and returns a list of all Patient objects.
    @classmethod
    def pts_from_csv(cls, csv_file):
        # If the given filename can't be found in the current working directory, it tries to find it in the same directory as this script. This is what fixed the "file not found" error.
        
        # AI Usage: I got a "file not found" error even though the CSV file was visibly in the same folder as my code.
        # I asked Claude to help debug it, and it explained that open() uses a path relative to Python's current working directory, not the actual file location.
        # It suggested resolving the path relative to this file's location instead so it works regardless of where the script is run.
        if not os.path.isfile(csv_file):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            csv_file = os.path.join(script_dir, csv_file)

        patients = [] # Empty list to store the patient objects.

        # Opens the CVS file for reading. 
        with open(csv_file, newline='') as csvfile:
            # DictReader reads each row as a dictionary where the keys are the column headers.
            reader = csv.DictReader(csvfile)

            # Loops over every row in the CSV, once per patient.
            for row in reader:
                # Builds a new patient object using the row's values, calling __init__ with each column.
                patient = cls(
                    donor_id = row['Donor ID'],
                    age_at_death = row['Age at Death'],
                    sex = row['Sex'],
                    education = row['Highest level of education'],
                    years_education = row['Years of education'],
                    apoe_genotype = row['APOE Genotype'],
                    cognitive_status = row['Cognitive Status'],
                    age_onset = row['Age of onset cognitive symptoms'],
                    age_diagnosis = row['Age of Dementia diagnosis'],
                    thal = row['Thal'],
                    braak = row['Braak'],
                    abeta40 = row['ABeta40 pg/ug'],
                    abeta42 = row['ABeta42 pg/ug'],
                    ttau = row['tTAU pg/ug'],
                    ptau = row['pTAU pg/ug']
                )
                patients.append(patient) # Adds the new patient to the ongoing list.
        return patients

    # Filters the patients based on the provided criteria and prints the sub-set. 
    # If a criterion is None, it is ignored in the filtering process. 
    # Returns a list of patients that match the criteria that was specified.
    @classmethod
    def filter_patients(cls, patients, sex = None, cognitive_status = None, apoe_genotype = None, thal = None, age_at_death = None):

        results = [] # Holds the patients that meet every criteria.
        for patient in patients:
            # For each filter argument, if there was a value given that isn't None but the patient doesn't match it, it skips to the next patient using "continue". That patient will not be added.
            if sex is not None and patient.sex != sex:
                continue
            if cognitive_status is not None and patient.cognitive_status != cognitive_status:
                continue
            if apoe_genotype is not None and patient.apoe_genotype != apoe_genotype:
                continue
            if thal is not None:
                # thal_score is called here to convert the values to a number that can be compared using the following filter argument.
                score = cls.thal_score(patient)
                if score is None or score < thal:
                    continue
            if age_at_death is not None:
                if patient.age_at_death is None or patient.age_at_death != age_at_death:
                    continue

            # This line is reached if the patient passes every filter, so they are appended to the list.
            results.append(patient)
        return results # Only returns the patients that made it through all the checks.