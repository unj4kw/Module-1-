import csv
import os

csv_name = 'Metadata and Protein Data for Module 1.csv'

class Patient:
    def __init__(self, donor_id, age_at_death, sex, education, years_education, apoe_genotype, cognitive_status, age_onset, age_diagnosis, thal, braak, abeta40, abeta42, ttau, ptau, mmse = None, mmse_interval = None, ad_change = None):

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


        self.mmse = self._create_float(mmse) 
        self.mmse_interval = self._create_float(mmse_interval) # Finds months between MMSE and death, due to older scores being less reliable.
        self.ad_change = ad_change # Determines the pathologist's overall AD rating.

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
    # This method goes through every character in the "thal" string and only keeps the digits.
        if not patient.thal:
            return None

        # Goes through every character in "thal" column and checks if it is a digit. If it is, it adds it to the "digits" string. If not, it ignores it.    
        digits = "".join(i for i in patient.thal if i.isdigit()) 

        # Returns None if there is no numeric value found in the column. Otherwise, it concerse the digits found into an integer.
        return int(digits) if digits else None        


    def __repr__(self):  
    # Defines what gets shown when you print a patient or a list of patient data.
    # This builds a readable line per patient, showing the attributes separated by vertical bars.
        return f"{self.donor_id}: ({self.age_at_death} | {self.sex} | {self.education} | {self.years_education} | {self.apoe_genotype} | {self.cognitive_status} | {self.age_diagnosis} | {self.thal} | {self.braak} | {self.abeta40} | {self.abeta42} | {self.ttau} | {self.ptau})" 

    @classmethod
    def pts_from_csv(cls, csv_file):
    # Create patient objects from the CSV file and store them in a list. 
    # This method reads the CSV file, creates a Patient object for each row, and returns a list of all Patient objects.
    
        if not os.path.isfile(csv_file):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            csv_file = os.path.join(script_dir, csv_file)
            patients = [] # Empty list to store the patient objects.
    
        with open(csv_file, newline='') as csvfile:
        # Opens the CVS file for reading.
            reader = csv.DictReader(csvfile)
            # DictReader reads each row as a dictionary where the keys are the column headers.
            
            for row in reader:
            # Loops over every row in the CSV, once per patient.
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
                    ptau = row['pTAU pg/ug'],
                    mmse = row['Last MMSE Score'],
                    mmse_interval = row['Interval from last MMSE in months'],
                    ad_change = row['Overall AD neuropathological Change']
                    )
                patients.append(patient) # Adds the new patient to the ongoing list.
        return patients

    # Filters the patients based on the provided criteria and prints the sub-set. 
    # If a criterion is None, it is ignored in the filtering process. 
    # Returns a list of patients that match the criteria that was specified.
    @classmethod
    def filter_patients(cls, patients, sex = None, cognitive_status = None, apoe_genotype = None, thal = None, age_at_death = None, ad_change = None):

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

            if ad_change is not None and patient.ad_change != ad_change: 
                continue
            results.append(patient)
            # This line is reached if the patient passes every filter, so they are appended to the list.
        return results # Only returns the patients that made it through all the checks.