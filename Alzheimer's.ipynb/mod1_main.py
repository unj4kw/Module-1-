# Module 1 Final Project - Alzeimer's Disease Data Analysis
# Question 1: Which protein (amyloid-beta or tau) better tracks cognitive decline, measured by MMSE score?
# Question 2: Among donors with high Alzeimer's pathology, do those with more education have better MMSE scores or lower dementia rates?


import statistics # Used for mean(), stdev(), and quantiles() calculations.
import matplotlib.pyplot as plt # Used to build all the graphs.
plt.ion() # Turns on interactive mode so each graph window doesn't pause the rest of the code.
import numpy as np # Used to turn lists into arrays, with sklearn needs for linear regression.
from scipy import stats # Used for statistical tests (K-S, Levene, t-test, Mann-Whitney, ANOVA, Kruskal-Wallis, Tukey).
from sklearn.linear_model import LinearRegression # Used for linear regression, the same method shown in the fourth lecture.
from mod1_patient import Patient # Imports the Patient class located in mod1_patient.py.

# AI Usage: We used Claude to help plan our analysis, write the helper functions and statistical tests, and debug errors (file names, imports, and a scipy version issue with the K-S test.)
# We reviewed and ran each section ourselves and checked that the tests matched the ones taught in lecture.

# Creating patient objects from the CSV file and storing them in a list.
# pts_from_csv() reads every row of the CSV and builds one Patient object per row.
csv_name = 'Metadata and Protein Data for Module 1.csv'
patients = Patient.pts_from_csv('Metadata and Protein Data for Module 1.csv')
print(f"Loaded {len(patients)} patients\n")

# Data validation: the MMSE is scored out of 30, so any score above 30 is not possible.
invalid_mmse = [p for p in patients if p.mmse is not None and p.mmse > 30]
for p in invalid_mmse: # This finds any patients with a score above 30 and sets their MMSE to None, so they are left out of every MMSE analysis.
    p.mmse = None

# List of the 4 proteins we compare in Question 1.
# Each pair holds the attribute name in the Patient class and the label we use on the graphs.
proteins = [('ptau','pTAU'), ('ttau','tTAU'), ('abeta42','ABeta42'), ('abeta40','ABeta40')]

# Helper Functions: These functions were created to be reused for every graph, so each graph uses the same tested steps.

def paired_values(pts, x_attr, y_attr):
    # Builds two matching lists (x and y) for a scatter plot.
    # Only keeps patients who have both values, so a missing value doesn't break the list.
    # getattr(p, x_attr) gets an attribute using its name as a string, e.g. getattr(p,'ptau') is the same as p.ptau.
    keep = [p for p in pts if getattr(p, x_attr) is not None and getattr(p, y_attr) is not None]
    return[getattr(p, x_attr) for p in keep], [getattr(p, y_attr) for p in keep]

def iqr_outlier_bounds(values):
    # Finds the cutoffs for outliers using the IQR rule.
    # quantiles(n = 4) splits the data into 4 equal parts and returns Q1 (25%), the median, and Q3 (75%).
    # The _ skips the median since we don't need it here.
    q1, _, q3 = statistics.quantiles(values, n = 4)
    iqr = q3 - q1 # IQR = the spread of the middle 50% of the data.
    # Anything below Q1 - 1.5*IQR or above Q3 + 1.5*IQR counts as an outlier.
    return q1 - 1.5 * iqr, q3 + 1.5 * iqr

def linear_regression(x, y):
    # Fits a straight line (y = slope * x + intercept) through the data, following the method from lecture.
    X = np.array(x).reshape(-1,1) # sklearn needs a single column, so reshape(-1, 1) turns the list into one.
    Y = np.array(y)
    model = LinearRegression() # Creates an empty linear regression model.
    model.fit(X, Y) # Finds the line that best fits the data.
    slope = model.coef_[0] # How much y changes for every 1 unit increase in x.
    intercept = model.intercept_ #
    r2 = model.score(X, Y) # R^2 represents how much of the variation in y is explained by x (0 = poor fit, 1 = perfect fit).
    return model, slope, intercept, r2

def scatter_with_regression(ax, x, y, xlabel, ylabel, title):
    # Draws a scatter plot with its regression line, and writes the equation and R^2 value on the graph.
    model, slope, intercept, r2 = linear_regression(x, y)
    X = np.array(x).reshape(-1, 1)

    # ax.scatter plots a dot per patient.
    # alpha = 0.7 makes the dots slightly see-through to help show overlapping dots.
    ax.scatter(x, y, color = 'blue', alpha = 0.7, edgecolor = 'black')

    # model.predict(X) calculates the y-value on the line for each x, and ax.plot draws the red regression line.
    ax.plot(X, model.predict(X), color = 'red')

    # Writes the equation and R^2 in a white box in the bottom-left corner.
    # transform = ax.transAxes means (0.03, 0.03) is a position on the graph (3% from the left and bottom), not a data value.
    ax.text(0.03, 0.03, f'y = {slope:.3f}x + {intercept:.2f}\nR² = {r2:.3f}', transform = ax.transAxes, color = 'red', fontsize = 9, va = 'bottom', bbox = dict(facecolor = 'white', alpha = 0.8))
    ax.set_xlabel(xlabel) # x-axis label
    ax.set_ylabel(ylabel) # y-axis label
    ax.set_title(title) # graph title
    return slope, intercept, r2

def significance_stars(p):
    # Turns a p-value into the standard star shorthand shown above the bars.
    # We use alpha = 0.05, so any p-value below 0.05 is significant. More stars indicates stronger evidence.
    if p < 0.001: return '***'
    if p < 0.01: return '**'
    if p < 0.05: return '*'
    return 'not significant'

def standardize(values):
    # Converts values into z-scores: (value - mean) / standard deviation.
    # This lets the K-S test compare the data to a standard normal curve (mean 0, stdev 1).
    m = statistics.mean(values)
    sd = statistics.stdev(values)
    return[(v - m) / sd for v in values]

def check_assumptions(*groups):
# Before comparing groups, we run two checks to decide which kind of test is appropriate.
# *groups means this function can take any number of groups (2 for a t-test, 4 for the ANOVA).
    
    # Check 1: Normality (Kolmogorov-Smirnov test):
    # Each group is converted to z-scores and compared to a standard normal curve.
    # If p > 0.05, the data is not significantly different from normal, so we treat it as normal.
    normal = all(stats.kstest(standardize(g), 'norm').pvalue > 0.05 for g in groups)     # all(...) only makes it True if every group passes.

    # CHECK 2 - Equal variances (Levene's test):
    # If p > 0.05, the spreads are not significantly different, so we treat the variances as equal.
    equal_var = stats.levene(*groups).pvalue > 0.05

    # Prints the result of both checks so we can report which test was chosen and why.
    print(f"Assumption checks: normal (K-S) = {normal}, equal variances (Levene) = {equal_var}")
    
    # Returns True only if both checks pass.
    # True  -> use a parametric test, which compares means (Student's t-test or one-way ANOVA).
    # False -> use a non-parametric test, which compares ranks (Mann-Whitney or Kruskal-Wallis).
    return normal and equal_var

def two_group_test(a, b):
# Compares exactly two unpaired groups. There are different patients in each group and each one is measured once.
# This is two-tailed because we are testing whether the groups differ, not whether one is specifically higher.
# If both assumptions pass, it proceeds to the student's t-test, to compare means.
    if check_assumptions(a, b):
        t_stat, p_val = stats.ttest_ind(a, b)
        return "Student's t-test", t_stat, p_val
        # If either assumption fails, it proceeds to the Mann-Whitney rank sum test, to compare ranks instead of means.
    u_stat, p_val = stats.mannwhitneyu(a, b, alternative = 'two-sided')
    return "Mann-Whitney", u_stat, p_val

def bar_with_test(ax, groups, labels, ylabel, title, colors):
# Draws a bar graph of the mean (+/- standard deviation) for two groups and adds the test result on top.
    means = [statistics.mean(g) for g in groups] # bar heights
    stds = [statistics.stdev(g) for g in groups] # error bar sizes (+/- stdev)

    # ax.bar draws the bars 
    # yerr adds the error bars
    # capsize adds caps to their ends
    # edgecolor outlines each bar
    ax.bar(labels, means, yerr = stds, capsize = 8, color = colors, edgecolor = 'black')
    
    # Runs the statistical test that fits the data (t-test or Mann-Whitney).
    test_name, stat, p = two_group_test(groups[0], groups[1])
    # Finds the top of the tallest error bar so the bracket and p-value can go right above it.
    top = max(m + s for m, s in zip(means, stds))
    
    # Draws the bracket connecting the two bars. The x-values are the bar positions and the y-values set its height.
    ax.plot([0, 0, 1, 1], [top * 1.05, top * 1.1, top * 1.1, top * 1.05], color = 'black')

    # Writes the stars, the test name, and the p-value centered above the bracket.
    ax.text(0.5, top * 1.12, f'{significance_stars(p)}\n{test_name}, p = {p:.3g}', ha = 'center', fontsize = 8)
    
    # Makes the y-axis tall enough so the bracket and text aren't cut off.
    ax.set_ylim(0, top * 1.35)
    ax.set_ylabel(ylabel)
    ax.set_title(title)

    # Places the tick marks under each bar and labels them with the group name and its number of patients (n).
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels([f'{l}\n(n = {len(g)})' for l, g in zip(labels, groups)])
    return test_name, stat, p


# Question 1 Figures

# Figure 1: Scatter plots of MMSE vs. each protein, with linear regression.
# A negative slope indicates more of that protein goes with worse cognitive scores.

q1_results = {} # Stores each protein's slope and R^2 so we can compare them and use them in the outlier analysis.

# One figure with a 2x2 grid of scatter plots so all 4 proteins can be compared side by side.
# figsize is large and constrained_layout spaces the panels so titles and labels don't overlap.
fig, axes = plt.subplots(2, 2, figsize = (13, 10), constrained_layout = True)

# Loops through the 4 proteins
# axes.flat turns the 2x2 grid into a list, so each protein gets its own panel.
for ax, (attr, label) in zip(axes.flat, proteins):
    x, y = paired_values(patients, attr, 'mmse') # x = protein level, y = MMSE score
    slope, intercept, r2 = scatter_with_regression(ax, x, y, f'{label} (pg/ug)', 'Last MMSE Score', f'MMSE vs. {label} (n = {len(x)})')
    q1_results[label] = (slope, r2) # Saves the results for this protein.

fig.suptitle('Figure 1: Cognitive Score (MMSE) vs. Protein Level', fontsize = 15) # Main title over the whole figure.
plt.savefig(f'fig1_mmse_vs_proteins.png', dpi = 100) # Saves the figure as a .png file.
plt.show()

# Prints a summary table of the slope and R^2 for each protein.
# The protein with the highest R^2 explains the most variation in MMSE, meaning it tracks cognition best.
# :<9 and :>10 line up the columns, and :.4f / :.3f round to 4 or 3 decimal places.
print(f"{'Protein':<9}{'slope':>10}{'R^2':>8}")
for label, (slope, r2) in q1_results.items():
    print(f"{label:<9}{slope:>10.4f}{r2:>8.3f}")


# Figure 2: Bar graphs comparing protein levels in donors with verusus without dementia.
# Null hypothesis: donors with and without dementia have similar levels of the protein.
# Alternative (two-tailed): the levels differ.

# One figure with 2 bar graphs side by side (pTAU and ABeta42).
fig, axes = plt.subplots(1, 2, figsize = (13, 6), constrained_layout = True)

for ax, (attr, label) in zip(axes, [('ptau', 'pTAU'), ('abeta42', 'ABeta42')]):
# Builds two lists of protein values: one for patients with dementia and one for patients without.
# getattr(p, attr) gets the protein value, and patients missing it are skipped.
    dem = [getattr(p, attr) for p in patients if p.cognitive_status == 'Dementia' and getattr(p, attr) is not None]
    no_dem = [getattr(p, attr) for p in patients if p.cognitive_status == 'No dementia' and getattr(p, attr) is not None]
    print(f"{label}:")

    # Draws the bar graph and runs the statistical test on the two groups.
    test_name, stat, p = bar_with_test(ax, [no_dem, dem], ['No dementia', 'Dementia'], f'{label} (pg/ug)', f'{label} by Cognitive Status', ['lightgreen', 'salmon'])
    print(f"{label}: {test_name}, statistic = {stat:.3f}, p = {p:.3g}")

fig.suptitle('Figure 2: Protein Levels in Donors With vs. Without Dementia', fontsize = 15)
plt.savefig(f'fig2_{label}_by_dementia.png', dpi = 100)
plt.show()


# Figure 3: One-way ANOVA to visualize if pTAU differs across the 4 levels of AD pathology.
# Null hypothesis: pTAU is the same across all 4 pathology levels.

# The 4 pathology levels, from least to most damage.
levels = ['Not AD', 'Low', 'Intermediate', 'High']

# Builds one list of pTAU values per pathology level using the ad_change filter.
# This creates a list of 4 lists, one for each level.
ptau_groups = [[p.ptau for p in Patient.filter_patients(patients, ad_change = lvl) if p.ptau is not None] for lvl in levels]

# Checks the assumptions first. The * unpacks the 4 lists so each one is passed in as its own group.
if check_assumptions(*ptau_groups):
    # If both checks pass, it runs a one-way ANOVA to compare means.
    anova_name = 'One-way ANOVA'
    stat, anova_p = stats.f_oneway(*ptau_groups)
else:
    # If either check fails, it runs a Kruskal-Wallis ANOVA on ranks.
    anova_name = 'Kruskal-Wallis ANOVA on ranks'
    stat, anova_p = stats.kruskal(*ptau_groups)
print(f"{anova_name}: statistic = {stat:.3f}, p = {anova_p:.3g}\n")

# ANOVA only tells us that at least one group is different, not which one.
# So if it passes (p <= 0.05), Tukey's HSD post hoc test compares every pair of groups to find which ones differ.
if anova_p <= 0.05:
    tukey = stats.tukey_hsd(*ptau_groups)
    print("Tukey HSD post hoc test (pairs with p < 0.05 differ significantly): ")

    # The two loops go through every pair of levels once
    # tukey.pvalue[i, j] is the p-value for the pair of level i and level j
    for i in range(len(levels)):
        for j in range(i + 1, len(levels)):
            print(f" {levels[i]:>12} vs {levels[j]:<12} p = {tukey.pvalue[i,j]:.3g}")
else:
    print("ANOVA failed (p > 0.05), so no post hoc test: none of the groups differ significantly.")

# Bar graph of the mean (+/- stdev) pTAU for each pathology level.
fig, ax = plt.subplots(figsize = (7, 5))
means = [statistics.mean(g) for g in ptau_groups] # bar heights
stds = [statistics.stdev(g) for g in ptau_groups] # error bar sizes

# The 4 colors go from light to dark blue to show increasing pathology.
ax.bar(range(4), means, yerr = stds, capsize = 8, color = ['#d0e1f2', '#9ecae1', '#4292c6', '#08519c'], edgecolor = 'black')
ax.set_xticks(range(4))
ax.set_xticklabels([f'{l}\n(n = {len(g)})' for l, g in zip(levels, ptau_groups)]) # Level name and number of patients under each bar.
ax.set_xlabel('Overall AD Neuropathological Change')
ax.set_ylabel('pTAU (pg/ug)')
ax.set_title(f"pTAU by Alzheimer's Pathology Level\n{anova_name}: p = {anova_p:.3g}") # Shows which test was used and its p-value.
plt.tight_layout() # Adjusts spacing so labels don't get cut off.
plt.savefig('fig3_ptau_anova.png', dpi = 100)
plt.show()

# Question 2
# 

high = Patient.filter_patients(patients, ad_change = 'High') # Only keeps high-pathology donors.

# Splits the high-pathology donors into those with dementia and those without.
high_dem = [p for p in high if p.cognitive_status == 'Dementia']
high_no_dem = [p for p in high if p.cognitive_status == 'No dementia']
print(f"High pathology donors: {len(high)} ({len(high_dem)} dementia, {len(high_no_dem)} no dementia)\n")

# Figure 4: Scatter plot of years of education vs. MMSE in high-pathology donors, with linear regression.
# Null hypothesis: years of education has no relationship with MMSE score (the slope is 0).
# Alternative: education is related to MMSE. A positive slope would support cognitive reserve (more education goes with better cognition despite the same brain damage).
# We judge the strength of the relationship using R^2 (closer to 0 = no relationship).
fig, ax = plt.subplots(figsize = (7,5))
x, y = paired_values(high, 'years_education', 'mmse') # x = years of education, y = MMSE score
slope_edu, int_edu, r2_edu = scatter_with_regression(ax, x, y, 'Years of Education', 'Last MMSE Score', f'Education vs. MMSE in High-Pathology Donors (n = {len(x)})')
plt.tight_layout()
plt.savefig('fig4_education_vs_mmse_high.png', dpi = 100)
plt.show()
print(f"slope = {slope_edu:.3f} MMSE points per year of education, R^2 = {r2_edu:.3f}")

# Figure 5: Bar graph of years of education in high-pathology donors with vs. without dementia.
# Null hypothesis: donors with and without dementia have the same average years of education.
# Alternative (two-tailed): the average years of education differ between the two groups.
# If cognitive reserve is real, we would expect the no-dementia group to have more education.
fig, ax = plt.subplots(figsize = (6, 5))

# Builds two lists of years of education, skipping anyone missing that value.
edu_no_dem = [p.years_education for p in high_no_dem if p.years_education is not None]
edu_dem = [p.years_education for p in high_dem if p.years_education is not None]

# Draws the bar graph and runs the statistical test on the two groups.
test_name, stat, p = bar_with_test(ax, [edu_no_dem, edu_dem], ['No dementia', 'Dementia'], 'Years of Education', 'Education in High-Pathology Donors', ['lightgreen', 'salmon'])

plt.tight_layout()
plt.savefig('fig5_education_vs_demenentia.png', dpi = 100)
plt.show()
print(f"{test_name}: statistic = {stat:.3f}, p = {p:.3g}")
print(f"Mean education - no dementia: {statistics.mean(edu_no_dem):.1f} yrs, dementia: {statistics.mean(edu_dem):.1f} yrs")


# Figure 6: The protein data is very skewed: a few donors have extremely high values.
# In linear regression, a single extreme point can pull the line and inflate or shrink R^2.
# Our code finds outliers using the IQR rule, shows them with box plots, and re-runs Figure 1 regressions without the outliers and compare R^2.
# If R^2 stays similar, the result is not driven by a few patients.

print(f"{'Protein':<9}{'# outliers':>11}{'R^2 (all)':>11}{'R^2 (no outliers)':>19}")
for attr, label in proteins:
# All of the values for this protein, skipping missing ones.
    values = [getattr(p, attr) for p in patients if getattr(p, attr) is not None]

    # Gets the outlier cutoffs, then finds every patient whose value falls outside of them.
    low, high_bound = iqr_outlier_bounds(values)
    outliers = [p for p in patients if getattr(p, attr) is not None and not (low <= getattr(p, attr) <= high_bound)]

    # Box plot: the box is the middle 50% of the data, the line inside is the median, and dots past the whiskers are outliers.
    fig, ax = plt.subplots(figsize = (5,5))
    ax.boxplot(values)
    ax.set_title(f'{label} Distribution ({len(outliers)} outliers)')
    ax.set_ylabel(f'{label} (pg/ug)')
    ax.set_xticks([]) # Removes the x-axis tick since there is only one box
    plt.tight_layout()
    plt.savefig(f'fig6_{label}_outliers.png', dpi = 100)

    # Re-runs the regression without the outliers and compares it to the original R^2 from Figure 1.
    kept = [p for p in patients if p not in outliers] # Everyone except the outliers.
    x, y = paired_values(kept, attr, 'mmse')
    _, _, _, r2_clean = linear_regression(x, y) # The _ skips the values we don't need (model, slope, intercept).
    print(f"{label:<9}{len(outliers):>11}{q1_results[label][1]:>11.3f}{r2_clean:>19.3f}")
    print(f"        outlier IDs: {[p.donor_id for p in outliers]}") # Lists which donors were outliers.


# Some MMSE scores were taken years before death, but proteins were measured after death.
# Cognition can decline a lot in that gap. This code check re-runs the regressions using only MMSE scores taken within 24 months (2 years) of death to see if the pTAU result still holds.
recent = [p for p in patients if p.mmse_interval is not None and p.mmse_interval <= 24]
print(f"\nDonors with MMSE within 24 months of death: {len(recent)}")
for attr, label in [('ptau', 'pTAU'), ('abeta42', 'ABeta42')]:
    x, y = paired_values(recent, attr, 'mmse')
    _, slope, _, r2 = linear_regression(x, y)
    print(f"    {label}: slope = {slope:.4f}, R^2 = {r2:.3f}")

# Keeps all graph windows open at the end of the script.
plt.ioff()
plt.show()
