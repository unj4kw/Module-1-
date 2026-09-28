#Jade Campoverde unj4kw

# %%
import statistics #used for mean and stdev 
import matplotlib.pyplot as plt #used to create the bar graph and scatter plot
from patient_jade import Patient 
import os 
from scipy import stats 
from sklearn.linear_model import LinearRegression
import numpy as np 

#os.path builds the script's own location. instead of a normal filename string. this code still finds the CSV
#i used claude to figure out why my code kept giving me a FileNotFoundError. Python was not looking for the script's location.
CVS_PATH= os.path.join(os.path.dirname(__file__), 'Metadata and Protein Data for Module 1 (1).csv')
patients = Patient.pts_from_csv(CVS_PATH)
print(set(p.cognitive_status for p in patients))
#sorted() takes the list of patients and uses the key function to sort by something specific.
#age at death is a simple numeric field
sorted_by_age = sorted(patients, key=lambda p: p.age_at_death)
for patient in sorted_by_age:
    print(patient)
print()

#filtering patients by sex and cognitive status (my first example of filtering on 2+ attributes).both conditions (Female AND Dementia) must be true for a patient to make it into this list.

female_dementia = Patient.filter_patients(patients, sex='Female', cognitive_status='Dementia')

print(f"Number of female patients with dementia: {len(female_dementia)}")
for patient in female_dementia:
    print(patient)
print()


male_apoe_44 = Patient.filter_patients(patients, sex='Male', apoe_genotype='4_4')

print(f"Number of male patients with APOE 4/4 genotype: {len(male_apoe_44)}")
for patient in male_apoe_44:
    print(patient)
print()
#AI usage- i added float() conversion based on the fact that i needed to convert to float() before any math. 
dementia_patients = Patient.filter_patients(patients, cognitive_status='Dementia')
female_abeta42 = [float(p.abeta42) for p in dementia_patients if p.sex == 'Female' and p.abeta42 is not None]
male_abeta42 = [float(p.abeta42) for p in dementia_patients if p.sex == 'Male' and p.abeta42 is not None]
print(f"dementia_patients count: {len(dementia_patients)}")
print(f"female_abeta42: {female_abeta42}")
print(f"male_abeta42: {male_abeta42}")
female_mean, female_std = statistics.mean(female_abeta42), statistics.stdev(female_abeta42)
male_mean, male_std = statistics.mean(male_abeta42), statistics.stdev(male_abeta42)
#AI Usage: I asked Claude how to generate a bar graph and scatter plot in Python. it suggested using matplotlib's plt.subplots(), ax.bar()/ax.scatter(), and plt.savefig().
#helpful- I used these to build and save each figure as a .png file instead of using plt.show(),
fig, ax = plt.subplots(figsize=(6, 5))

groups = ['Female', 'Male'] 
means = [female_mean, male_mean] 
stds = [female_std, male_std] 

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
plt.tight_layout() 

# Saves the figure as a .png file.
plt.savefig('bar_graph_abeta42_by_sex.png', dpi = 200)
plt.close(fig) 
print("Saved bar_graph_abeta42_by_sex.png, a bar graph comparing ABeta42 levels between male and female patients with dementia.\n")


# ages = [float(p.age_at_death) for p in patients if p.age_at_death not in (None, '') and p.abeta42 not in (None, '')]
# abeta42_levels = [float(p.abeta42) for p in patients if p.age_at_death not in (None, '') and p.abeta42 not in (None, '')]
ages = [float(p.age_at_death) for p in patients if p.age_at_death not in (None, '') and p.abeta42 not in (None, '')]
abeta42_levels = [float(p.abeta42) for p in patients if p.age_at_death not in (None, '') and p.abeta42 not in (None, '')]

# reshape into the (n_samples, 1) format sklearn expects for X
X = np.array(ages).reshape(-1, 1)   # independent variable
y = np.array(abeta42_levels)         # dependent variable

# fit the linear regression
model = LinearRegression()
model.fit(X, y)

slope = model.coef_[0]
intercept = model.intercept_
r2 = model.score(X, y)

fig, ax = plt.subplots(figsize=(6, 5))

ax.scatter(ages, abeta42_levels, alpha=0.8, color='purple', edgecolor='black')
ax.plot(X, model.predict(X), color='red')  # regression line

# annotate the equation and R^2 in the corner
equation = f"y = {slope:.2f}x + {intercept:.2f}\nR² = {r2:.2f}"
ax.text(0.95, 0.95, equation, transform=ax.transAxes, ha='right', va='top',
         color='red', fontsize=12)

ax.set_xlabel('Age at Death')
ax.set_ylabel('ABeta42 Levels (pg/ug)')
ax.set_title('Age at Death vs. ABeta42 Levels')
plt.tight_layout()
plt.savefig('scatter_plot_age_vs_abeta42.png', dpi=200)
plt.close(fig)
print("Saved scatter_plot_age_vs_abeta42.png, a scatter plot of Age at Death vs. ABeta42 levels with regression line.\n")
print("Working directory:", os.getcwd())
print("Files here:", os.listdir("."))

#AI Usage: asked Claude how to run a one-way ANOVA across 4 groups and add it to the bar graph.
#scipy.stats.f_oneway compares means across groups; a small p-value means at least one
#group's mean differs significantly from the others.

#split into healthy vs. dementia groups, then by sex
#NOTE: replace 'No Dementia' below with whatever string your CSV actually uses
healthy_patients = Patient.filter_patients(patients, cognitive_status='<exact string from the printout>')

healthy_patients = Patient.filter_patients(patients, cognitive_status='No dementia')
dementia_patients = Patient.filter_patients(patients, cognitive_status='Dementia')

def get_abeta42(patient_list, sex):
    return [float(p.abeta42) for p in patient_list
            if p.sex == sex and p.abeta42 not in (None, '')]

health_fem_vals = get_abeta42(healthy_patients, 'Female')
health_male_vals = get_abeta42(healthy_patients, 'Male')
diseased_fem_vals = get_abeta42(dementia_patients, 'Female')
diseased_male_vals = get_abeta42(dementia_patients, 'Male')

x_health_fem_bar = statistics.mean(health_fem_vals)
x_health_male_bar = statistics.mean(health_male_vals)
x_diseased_fem_bar = statistics.mean(diseased_fem_vals)
x_diseased_male_bar = statistics.mean(diseased_male_vals)

ABeta_health_fem_stdev = statistics.stdev(health_fem_vals)
ABeta_health_male_stdev = statistics.stdev(health_male_vals)
ABeta_diseased_fem_stdev = statistics.stdev(diseased_fem_vals)
ABeta_diseased_male_stdev = statistics.stdev(diseased_male_vals)

print(f"x_bar = {x_health_fem_bar}, ABeta_stdev {ABeta_health_fem_stdev}")
print(f"x_bar = {x_health_male_bar}, ABeta_stdev {ABeta_health_male_stdev}")
print(f"x_bar = {x_diseased_fem_bar}, ABeta_stdev {ABeta_diseased_fem_stdev}")
print(f"x_bar = {x_diseased_male_bar}, ABeta_stdev {ABeta_diseased_male_stdev}")

sex_cols = ['Healthy Female', 'Healthy Male', 'Diseased Female', 'Diseased Male']
mean_sex_ABeta42 = [x_health_fem_bar, x_health_male_bar, x_diseased_fem_bar, x_diseased_male_bar]
stdev_sex_ABeta42 = [ABeta_health_fem_stdev, ABeta_health_male_stdev,
                      ABeta_diseased_fem_stdev, ABeta_diseased_male_stdev]
colors = ["red", "blue", "pink", "skyblue"]

# run one-way ANOVA across all four groups at once
f_stat, p_value = stats.f_oneway(health_fem_vals, health_male_vals,
                                  diseased_fem_vals, diseased_male_vals)
print("F-statistic:", f_stat)
print("p-value:", p_value)

fig, ax = plt.subplots(figsize=(6, 5))
ax.bar(sex_cols, mean_sex_ABeta42, yerr=stdev_sex_ABeta42, capsize=10,
       color=colors, edgecolor='black')
ax.set_title("ABeta42 Levels")
ax.set_xlabel("Sex and Health Status")
ax.set_ylabel("ABeta42 (pg/ug)")
ax.text(1.5, max(mean_sex_ABeta42) + max(stdev_sex_ABeta42) + 20,
        f"One-Way ANOVA: p = {p_value:.3f}", ha='center', va='top', fontsize=12)
plt.tight_layout()
plt.savefig('bar_graph_abeta42_four_groups.png', dpi=200)
plt.close(fig)
print("Saved bar_graph_abeta42_four_groups.png\n")

print("Working directory:", os.getcwd())
print("Files here:", os.listdir("."))