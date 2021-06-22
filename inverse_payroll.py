import numpy as np
import pandas as pd

#SCRIPT DE PRUEBA MENSUAL

def get_isr_factors(salary):
    data = dict()
    
    lower_limits = [0.01, 644.59, 5470.93, 9614.67, 11176.63, 13381.48, 26988.51, 42537.59, 81211.26, 108281.68, 324845.02]
    upper_limits = [644.58, 5470.92, 9614.66, 11176.62, 13381.47, 26988.50, 42537.58, 81211.25, 108281.67, 324845.01, 999999.00]
    fixed_taxes = [0.00, 12.38, 321.26, 772.10, 1022.01, 1417.12, 4323.58, 7980.73, 19582.83, 28245.36, 101876.90]
    factors = [1.92, 6.40, 10.88, 16.00, 17.92, 21.36, 23.52, 30.00, 32.00, 34.00, 35.00]

    for i, lower in enumerate(lower_limits):
        upper = upper_limits[i]
        if salary >= lower and salary <= upper:
            data['lower_limit'] = lower_limits[i]
            data['upper_limit'] = upper_limits[-1]
            data['fixed_fee'] = fixed_taxes[i]
            data['factor'] = factors[i]/100
            break
        else:
            pass
    return data

def get_subsidy(salary):
    data = dict()
    lower_limits_subsidy = [0.01, 1768.97, 2653.39, 3472.85, 3537.88, 4446.16, 4717.19, 5335.43, 6224.68, 7113.91, 7382.34]
    upper_limits_subsidy = [1768.96, 2653.38, 3472.84, 3537.87, 4446.15, 4717.18, 5335.42, 6224.67, 7113.90, 7382.33, 999999]
    subsidy_values = [407.02, 406.83, 406.62, 392.77, 382.46, 354.23, 324.87, 294.63, 253.54, 217.61, 0]

    for i, lower in enumerate(lower_limits_subsidy):
        upper = upper_limits_subsidy[i]
        if salary >= lower and salary <= upper:
            data['lower_limit'] = lower_limits_subsidy[i]
            data['upper_limit'] = upper_limits_subsidy[-1]
            data['subsidy'] = subsidy_values[i]
            break
        else:
            pass
    return data


def get_J(salary, net_salary, payroll_days, sbc, rate, lower_limit, fixed_fee, subsidy, additional_tax, factors, flag):
    isr = (salary - lower_limit)*rate + fixed_fee - subsidy
    employee_tax = sbc*payroll_days*factors + additional_tax
    #func = -salary + abs(net_salary + isr + employee_tax)
    func = abs(net_salary + isr + employee_tax - salary)
    # print('FO')
    if flag:
        print(salary, net_salary, isr, employee_tax, sbc, func)
    return func

def get_sbc(salary, payroll_days, uma, minimum_salary):
    vacation_days = 6
    christmas_bonus = 15
    vacation_bonus = 0.25
    quoted_days_sbc = 365

    daily_salary = float(salary/payroll_days)

    if daily_salary <= minimum_salary:
        return minimum_salary
    else:
        quote_factor = (1/quoted_days_sbc)*(quoted_days_sbc + (vacation_days*vacation_bonus) + christmas_bonus)
        sbc_value = daily_salary * quote_factor
        if sbc_value > 25*uma:
            return 25*uma
        else:
            return sbc_value

def get_additional_tax(salary, payroll_days, minimum_salary, uma, sbc, additional_tax_factor):
    if salary >= 3*uma*payroll_days:
        return ((sbc - 3*uma)*additional_tax_factor)*payroll_days
    else:
        return 0

#IMSS FACTORS
additional_tax_factor = 0.004
medical_tax_factor = 0.00375
money_tax_factor = 0.0025
disability_and_life_tax_factor = 0.00625
ceav_tax_factor = 0.01125
factors = medical_tax_factor + money_tax_factor + disability_and_life_tax_factor + ceav_tax_factor

uma = 89.62
minimum_salary = 141.70
payroll_days = 30

iter_num = 100
eps = 0.01

test_salaries = [
    4390,
    7000,
    8500,
    9500,
    12500,
    16500,
    20000,
    80000,
]

for net_salary in test_salaries:

    #Vector initialization
    a = []
    b = []
    L = []
    fb = []
    fa = []
    alp = []

    lam = []
    mu = []
    f_alp = []
    f_lam = []
    f_mu = []

    #Initial values
    isr_data = get_isr_factors(net_salary)
    subsidy_data = get_subsidy(net_salary)
    sbc = get_sbc(net_salary, payroll_days, uma, minimum_salary)
    additional_tax = get_additional_tax(net_salary, payroll_days, minimum_salary, uma, sbc, additional_tax_factor)

    #Setting initial values
    a.append(isr_data['lower_limit'])
    b.append(isr_data['upper_limit'])
    L.append(b[-1] - a[-1])
    # fa.append(get_J(a[-1], net_salary, payroll_days, sbc, isr_data['factor'], isr_data['lower_limit'], isr_data['fixed_fee'], subsidy_data['subsidy'], additional_tax, factors, False))
    # fb.append(get_J(b[-1], net_salary, payroll_days, sbc, isr_data['factor'], isr_data['lower_limit'], isr_data['fixed_fee'], subsidy_data['subsidy'], additional_tax, factors, False))
    alp.append((a[-1] + b[-1])/2)

    lam.append(0)
    mu.append(0)
    f_alp.append(0)
    f_lam.append(0)
    f_mu.append(0)
    k=0

    f_alp[k] = get_J(alp[k], net_salary, payroll_days, sbc, isr_data['factor'], isr_data['lower_limit'], isr_data['fixed_fee'], subsidy_data['subsidy'], additional_tax, factors, False)

    #for k in range(iter_num):
    while k <= iter_num:
        lam[k] = a[k] + L[k]/4
        mu[k] = b[k] - L[k]/4
        f_alp[k] = get_J(alp[k], net_salary, payroll_days, sbc, isr_data['factor'], isr_data['lower_limit'], isr_data['fixed_fee'], subsidy_data['subsidy'], additional_tax, factors, False)
        f_lam[k] = get_J(lam[k], net_salary, payroll_days, sbc, isr_data['factor'], isr_data['lower_limit'], isr_data['fixed_fee'], subsidy_data['subsidy'], additional_tax, factors, False)
        f_mu[k] = get_J(mu[k], net_salary, payroll_days, sbc, isr_data['factor'], isr_data['lower_limit'], isr_data['fixed_fee'], subsidy_data['subsidy'], additional_tax, factors, False)
        
        if f_lam[k] < f_alp[k]:
            b.append(alp[k])
            alp.append(lam[k])
            a.append(a[k])

        elif f_mu[k] < f_alp[k]:
            a.append(alp[k])
            alp.append(mu[k])
            b.append(b[k])
        else:
            a.append(lam[k])
            b.append(mu[k])
            alp.append(alp[k])
        
        lam.append(0)
        mu.append(0)
        f_alp.append(0)
        f_lam.append(0)
        f_mu.append(0)
        
        L.append(b[k+1] - a[k+1])
        isr_data = get_isr_factors(alp[k+1])
        subsidy_data = get_subsidy(alp[k+1])
        sbc = get_sbc(alp[k+1], payroll_days, uma, minimum_salary)
        additional_tax = get_additional_tax(alp[k+1], payroll_days, minimum_salary, uma, sbc, additional_tax_factor)
        if f_alp[k] < eps:
            print(f_alp[k], k)
            break
        k = k + 1

    # data = np.array([a, b, L, alp, f_alp]).T
    # columns = ["ak", "bk", "xk", "Lk", "f_alp"]
    # results = pd.DataFrame(data=data, columns=columns)
    # print(results)
    get_J(alp[-1], net_salary, payroll_days, sbc, isr_data['factor'], isr_data['lower_limit'], isr_data['fixed_fee'], subsidy_data['subsidy'], additional_tax, factors, True)
    print(f"Optimum: {alp[-1]} k: {k} f_alp: {f_alp[-1]}")
    
