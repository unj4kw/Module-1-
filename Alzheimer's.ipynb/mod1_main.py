import statistics
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression
from mod1_patient import Patient

csv_name = 'Metadata and Protein Data for Module 1.csv'
patients = Patient.pts_from_csv('Metadata and Protein Data for Module 1.csv')
print(f"Loaded {len(patients)} patients\n")

invalid_mmse = [p for p in patients if p.mmse is not None and p.mmse > 30]
# MMSE is scored out of 30, so any score above 30 is not possible.
# Any patients with a score above 30 get their MMSE set to None and are excluded from MMSE analyses.
for p in invalid_mmse:
    p.mmse = None

proteins = [('ptau','pTAU'), ('ttau','tTAU'), ('abeta42','ABeta42'), ('abeta40','ABeta40')]

def paired_values(pts, x_attr, y_attr):
    keep = [p for p in pts if getattr(p, x_attr) is not None and getattr(p, y_attr) is not None]
    return[getattr(p, x_attr) for p in keep], [getattr(p, y_attr) for p in keep]

def iqr_outlier_bounds(values):
    q1, _, q3 = statistics.quantiles(values, n = 4)
    iqr = q3 - q1
    return q1 - 1.5 * iqr, q3 + 1.5 * iqr

def linear_regression(x, y):
    X = np.array(x).reshape(-1,1)
    Y = np.array(y)
    model = LinearRegression()
    model.fit(X, Y)
    slope = model.coef_[0]
    intercept = model.intercept_
    r2 = model.score(X, Y)
    return model, slope, intercept, r2

def scatter_with_regression(ax, x, y, xlabel, ylabel, title):
    model, slope, intercept, r2 = linear_regression(x, y)
    X = np.array(x).reshape(-1, 1)

    ax.scatter(x, y, color = 'blue', alpha = 0.7, edgecolor = 'black')
    ax.plot(X, model.predict(X), color = 'red')

    ax.text(0.03, 0.03, f'y = {slope:.3f}x + {intercept:.2f}\nR² = {r2:.3f}', transform = ax.transAxes, color = 'red', fontsize = 9, va = 'bottom', bbox = dict(facecolor = 'white', alpha = 0.8))
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    return slope, intercept, r2

def significance_stars(p):
    if p < 0.001: return '***'
    if p < 0.01: return '**'
    if p < 0.05: return '*'
    return 'n.s.'

def standardize(values):
    m = statistics.mean(values)
    sd = statistics.stdev(values)
    return[(v - m) / sd for v in values]

def check_assumptions(*groups):
    normal = all(stats.kstest(standardize(g), 'norm').pvalue > 0.05 for g in groups)
    equal_var = stats.levene(*groups).pvalue > 0.05
    print(f"Assumption checks: normal (K-S) = {normal}, equal variances (Levene) = {equal_var}")
    return normal and equal_var

def two_group_test(a, b):
    if check_assumptions(a, b):
        t_stat, p_val = stats.ttest_ind(a, b)
        return "Student's t-test", t_stat, p_val
    u_stat, p_val = stats.mannwhitneyu(a, b, alternative = 'two-sided')
    return "Mann-Whitney", u_stat, p_val

def bar_with_test(ax, groups, labels, ylabel, title, colors):
    means = [statistics.mean(g) for g in groups]
    stds = [statistics.stdev(g) for g in groups]
    ax.bar(labels, means, yerr = stds, capsize = 8, color = colors, edgecolor = 'black')
    test_name, stat, p = two_group_test(groups[0], groups[1])
    top = max(m + s for m, s in zip(means, stds))
    ax.plot([0, 0, 1, 1], [top * 1.05, top * 1.1, top * 1.1, top * 1.05], color = 'black')
    ax.text(0.5, top * 1.12, f'{significance_stars(p)}\n{test_name}, p = {p:.3g}', ha = 'center', fontsize = 8)
    ax.set_ylim(0, top * 1.35)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels([f'{l}\n(n = {len(g)})' for l, g in zip(labels, groups)])
    return test_name, stat, p


# Figure 1: Scatter plots of MMSE vs. each protein, with linear regression.
# A negative slope indicates more of that protein goes with worse cognitive scores.

q1_results = {}

for attr, label in proteins:
    fig, ax = plt.subplots(figsize = (7, 5))
    x, y = paired_values(patients, attr, 'mmse')
    slope, intercept, r2 = scatter_with_regression(ax, x, y, f'{label} (pg/ug)', 'Last MMSE Score', f'MMSE vs. {label} (n = {len(x)})')
    q1_results[label] = (slope, r2)

    plt.tight_layout()
    plt.savefig(f'fig1_mmse_vs_{label}.png', dpi = 100)
    plt.show()

print(f"{'Protein':<9}{'slope':>10}{'R^2':>8}")
for label, (slope, r2) in q1_results.items():
    print(f"{label:<9}{slope:>10.4f}{r2:>8.3f}")


# Figure 2: Bar graphs comparing protein levels in donors with verusus without dementia.
# Null hypothesis: donors with and without dementia have similar levels of the protein.
# Alternative (two-tailed): the levels differ.

for attr, label in [('ptau', 'pTAU'), ('abeta42', 'ABeta42')]:
    fig, ax = plt.subplots(figsize = (6, 5))
    dem = [getattr(p, attr) for p in patients if p.cognitive_status == 'Dementia' and getattr(p, attr) is not None]
    no_dem = [getattr(p, attr) for p in patients if p.cognitive_status == 'No dementia' and getattr(p, attr) is not None]
    print(f"{label}:")
    test_name, stat, p = bar_with_test(ax, [no_dem, dem], ['No dementia', 'Dementia'], f'{label} (pg/ug)', f'{label} by Cognitive Status', ['lightgreen', 'salmon'])
    print(f"{label}: {test_name}, statistic = {stat:.3f}, p = {p:.3g}")

    plt.tight_layout()
    plt.savefig(f'fig2_{label}_by_dementia.png', dpi = 100)
    plt.show()


# Figure 3: One-way ANOVA to visualize if pTAU differs across the 4 levels of AD pathology.
# Null hypothesis: pTAU is the same across all 4 pathology levels.

levels = ['Not AD', 'Low', 'Intermediate', 'High']
ptau_groups = [[p.ptau for p in Patient.filter_patients(patients, ad_change = lvl) if p.ptau is not None] for lvl in levels]

if check_assumptions(*ptau_groups):
    anova_name = 'One-way ANOVA'
    stat, anova_p = stats.f_oneway(*ptau_groups)
else:
    anova_name = 'Kruskal-Wallis ANOVA on ranks'
    stat, anova_p = stats.kruskal(*ptau_groups)
print(f"{anova_name}: statistic = {stat:.3f}, p = {anova_p:.3g}\n")

if anova_p <= 0.05:
    tukey = stats.tukey_hsd(*ptau_groups)
    print("Tukey HSD post hoc test (pairs with p < 0.05 differ significantly): ")

    for i in range(len(levels)):
        for j in range(i + 1, len(levels)):
            print(f" {levels[i]:>12} vs {levels[j]:<12} p = {tukey.pvalue[i,j]:.3g}")
else:
    print("ANOVA failed (p > 0.05), so no post hoc test: none of the groups differ significantly.")

fig, ax = plt.subplots(figsize = (7, 5))
means = [statistics.mean(g) for g in ptau_groups]
stds = [statistics.stdev(g) for g in ptau_groups]
ax.bar(range(4), means, yerr = stds, capsize = 8, color = ['#d0e1f2', '#9ecae1', '#4292c6', '#08519c'], edgecolor = 'black')
ax.set_xticks(range(4))
ax.set_xticklabels([f'{l}\n(n = {len(g)})' for l, g in zip(levels, ptau_groups)])
ax.set_xlabel('Overall AD Neuropathological Change')
ax.set_ylabel('pTAU (pg/ug)')
ax.set_title(f"pTAU by Alzheimer's Pathology Level\n{anova_name}: p = {anova_p:.3g}")
plt.tight_layout()
plt.savefig('fig3_ptau_anova.png', dpi = 100)
plt.show()

# 

high = Patient.filter_patients(patients, ad_change = 'High')
high_dem = [p for p in high if p.cognitive_status == 'Dementia']
high_no_dem = [p for p in high if p.cognitive_status == 'No dementia']
print(f"High pathology donors: {len(high)} ({len(high_dem)} dementia, {len(high_no_dem)} no dementia)\n")

# Figure 4:

fig, ax = plt.subplots(figsize = (7,5))
x, y = paired_values(high, 'years_education', 'mmse')
slope_edu, int_edu, r2_edu = scatter_with_regression(ax, x, y, 'Years of Education', 'Last MMSE Score', f'Education vs. MMSE in High-Pathology Donors (n = {len(x)})')
plt.tight_layout()
plt.savefig('fig4_education_vs_mmse_high.png', dpi = 100)
plt.show()
print(f"slope = {slope_edu:.3f} MMSE points per year of education, R^2 = {r2_edu:.3f}")

# Figure 5

fig, ax = plt.subplots(figsize = (6, 5))
edu_no_dem = [p.years_education for p in high_no_dem if p.years_education is not None]
edu_dem = [p.years_education for p in high_dem if p.years_education is not None]
test_name, stat, p = bar_with_test(ax, [edu_no_dem, edu_dem], ['No dementia', 'Dementia'], 'Years of Education', 'Education in High-Pathology Donors', ['lightgreen', 'salmon'])

plt.tight_layout()
plt.savefig('fig5_education_vs_demenentia.png', dpi = 100)
plt.show()
print(f"{test_name}: statistic = {stat:.3f}, p = {p:.3g}")
print(f"Mean education - no dementia: {statistics.mean(edu_no_dem):.1f} yrs, dementia: {statistics.mean(edu_dem):.1f} yrs")