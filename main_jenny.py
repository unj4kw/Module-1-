# Jenny Mejia - ccc3dq

# %%
import statistics # Used for mean() and stdev() calculations.
import matplotlib.pyplot as plt # Used to build the bar graph and scatter plot.
from patient import Patient # Import the Patient class located in patient.py.

import os # Used to check/print the current working directory.
# AI Usage: When my graphs weren't showing up anywhere even after successfully running the code, I used Claude to help troubleshoot.
# It suggested printing os.getcwd() and os.listdir("") to check where Python was actually saving my files. I was able to find them in a different folder than the one I was checking.

# Creating patient objects from the CSV file and storing them in a list
# This calls the pts_from_cvs() classmethod.
# Reads every row of the CSV and builds a patient object per row, returning them as list.
patients = Patient.pts_from_csv('Metadata and Protein Data for Module 1.csv')
print(f"Loaded {len(patients)} patients from {'Metadata and Protein Data for Module 1.csv'}\n")

# Sorting patients by age at death and printing them
# sorted() takes the list of patients and uses the key function to sort it by something specific.
# Here, "lambda p: p.age_at_death" means to use the age at death value as the basis for comparison.
# This sorts the patients from youngest to oldest.
sorted_by_age = sorted(patients, key=lambda p: p.age_at_death)
for patient in sorted_by_age:
    print(patient)
print()


# Filtering patients by sex and cognitive status (example of minimum 2 filters). 
# Prints patients that are female and have dementia, both conditions must be true for the patient to be added to this list.
female_dementia = Patient.filter_patients(patients, sex='Female', cognitive_status='Dementia')

print(f"Number of female patients with dementia: {len(female_dementia)}")
for patient in female_dementia:
    print(patient)
print()


# Filtering patients by sex and APOE 4/4 genotype (another example of minimum 2 filters)
male_apoe_44 = Patient.filter_patients(patients, sex='Male', apoe_genotype='4_4')

print(f"Number of male patients with APOE 4/4 genotype: {len(male_apoe_44)}")
for patient in male_apoe_44:
    print(patient)
print()


# Bar graph of mean(+/- standard deviation) ABeta42 levels, comparing male vs. female patients who have dementia.
# First, it narrows down to patients with dementia for both male and female groups using a single filter.
dementia_patients = Patient.filter_patients(patients, cognitive_status='Dementia')

# Builds two separate lists of ABeta42 values for male and female dementia patients.
# The "if ... p.abeta42 is not None" skips over patients missing that value to not break the calculations.
female_abeta42 = [p.abeta42 for p in dementia_patients if p.sex == 'Female' and p.abeta42 is not None]
male_abeta42 = [p.abeta42 for p in dementia_patients if p.sex == 'Male' and p.abeta42 is not None]

# statistics.mean and statistics.stdev calculate the average and standard deviation for each group.
# These values become the bar heights and the error bar sizes in the graphs.
female_mean, female_std = statistics.mean(female_abeta42), statistics.stdev(female_abeta42)
male_mean, male_std = statistics.mean(male_abeta42), statistics.stdev(male_abeta42)

# AI Usage: I asked Claude how to generate a bar graph and scatter plot in Python.
# It suggested using matplotlib's plt.subplots(), ax.bar(), ax.bar()/ax.scatter(), and plt.savefig().
# I used these to build and save each figure as a .png file.

# Creates a new figure (fig) and a single set of axes (ax) to draw on.
fig, ax = plt.subplots(figsize=(6, 5))

groups = ['Female', 'Male'] # X-axis labels.
means = [female_mean, male_mean] # Bar heights.
stds = [female_std, male_std] # Error bar sizes (+/- stdev).

# ax.bar draws the actual bars on the graph.
    # groups/means: the bar positions and heights
    # yerr=stds: adds the +/- stdev error bars
    # capsize=8: adds caps at the ends of the error bars
    # color=[...]: assigns a color per bar
    # edgecolor: outlines each bar in black for contrast
ax.bar(groups, means, yerr=stds, capsize=8, color=['pink', 'lightblue'], edgecolor='black')
ax.set_ylabel('ABeta42 Levels (pg/ug)') # y-axis label
ax.set_xlabel('Sex') # x-axis label
ax.set_title('ABeta42 Levels in Dementia Patients by Sex') # graph title
plt.tight_layout() # Adjusts spacing so labels don't get cut off

# Saves the figure as a .png file.
plt.savefig('bar_graph_abeta42_by_sex.png', dpi = 200)
plt.close(fig) # Closes the figure after saving
print("Saved bar_graph_abeta42_by_sex.png, a bar graph comparing ABeta42 levels between male and female patients with dementia.\n")


# Scatter plot of age at death vs. ABeta42 levels for all patients
# Builds two matching lists, one containing the ages and the other the ABeta42 values.
# Only uses patients who have both values present.
ages = [p.age_at_death for p in patients if p.age_at_death is not None and p.abeta42 is not None]
abeta42_levels = [p.abeta42 for p in patients if p.age_at_death is not None and p.abeta42 is not None]

fig, ax = plt.subplots(figsize=(6, 5))

# ax.scatter plots a dot per patient
# alpha=0.8 makes the dots slightly see through to help visualize points overlapping
ax.scatter(ages, abeta42_levels, alpha=0.8, color='purple', edgecolor='black')
ax.set_xlabel('Age at Death') # x-axis
ax.set_ylabel('ABeta42 Levels (pg/ug)') # y-axis
ax.set_title('Age at Death vs. ABeta42 Levels')
plt.tight_layout()

# Saves the figure as a .png file.
plt.savefig('scatter_plot_age_vs_abeta42.png', dpi = 200)
plt.close(fig)
print("Saved scatter_plot_age_vs_abeta42.png, a scatter plot of age at death vs. ABeta42 levels for all patients.\n")

# AI Usage: My graphs weren't showing up anywhere. This debugging code confirms where the .png files were saved, and they were visible to me after running.
print("Working directory:", os.getcwd())
print("Files here:", os.listdir("."))