#Jade Campoverde unj4kw
import csv 

#step 1- define a patient class
class Patient:
    def __init__(self, donor_id, age_at_death, sex, education, years_education, apoe_genotype, cognitive_status, age_onset, age_diagnosis, thal, braak, abeta40, abeta42, ttau, ptau):
#step 2- constructor: contains all the data
        self.donor_id = donor_id
        self.age_at_death = age_at_death
        self.sex = sex
        self.education = education
        self.years_education = years_education
        self.apoe_genotype = apoe_genotype
        self.cognitive_status = cognitive_status
        self.age_onset = age_onset
        self.age_diagnosis = age_diagnosis
        self.thal = thal
        self.braak = braak
        self.abeta40 = abeta40
        self.abeta42 = abeta42
        self.ttau = ttau
        self.ptau = ptau
#def- converts a CSV string value to a float and prevents the code from crashing
    def _create_float(value):
        if value is None or value == '':
            return None
        try:
            return float(value)
        except ValueError:
            return None
#class method- numeric score out of the thal field
    @classmethod
    def thal_score(cls, patient):
        if not patient.thal:
            return None
        digits="".join(y for y in patient.thal if y.isdigit())
        return int(digits) if digits else None
#repr- defines what prints when we call print() on our patient object     
    def __repr__(self):
        return f"{self.donor_id}: ({self.age_at_death} | {self.sex} | {self.education} | {self.years_education} | {self.apoe_genotype} | {self.cognitive_status} | {self.age_onset} | {self.age_diagnosis} | {self.thal} | {self.braak} | {self.abeta40} | {self.abeta42} | {self.ttau} | {self.ptau})"
#another class method- the CSV file is read and makes a patient object for all rows
    @classmethod
    def pts_from_csv(cls, csv_file):
        patients = []
        with open(csv_file, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                patient = cls(
                    donor_id=row['Donor ID'],
                    age_at_death=row['Age at Death'],
                    sex=row['Sex'],
                    education=row['Highest level of education'],
                    years_education=row['Years of education'],
                    apoe_genotype=row['APOE Genotype'],
                    cognitive_status=row['Cognitive Status'],
                    age_onset=row['Age of onset cognitive symptoms'],
                    age_diagnosis=row['Age of Dementia diagnosis'],
                    thal=row['Thal'],
                    braak=row['Braak'],
                    abeta40=row['ABeta40 pg/ug'],
                    abeta42=row['ABeta42 pg/ug'],
                    ttau=row['tTAU pg/ug'],
                    ptau=row['pTAU pg/ug']
                )
                patients.append(patient)
        return patients
#class method- filters the patient list to only match every condition passed and each parameter results in None
    @classmethod 
    def filter_patients(cls, patients, sex=None, cognitive_status=None,
                        apoe_genotype=None, thal=None, age_at_death=None):
        
        results=[]
        for patient in patients:
            if sex is not None and patient.sex != sex:
                continue
            if cognitive_status is not None and patient.cognitive_status != cognitive_status:
                continue
            if apoe_genotype is not None and patient.apoe_genotype != apoe_genotype:
                continue
            if thal is not None:
                score = cls.thal_score(patient)
                if score is None or score < thal:
                    continue
            if age_at_death is not None:
                if patient.age_at_death is None or patient.age_at_death != age_at_death:
                    continue

            results.append(patient)
        return results 