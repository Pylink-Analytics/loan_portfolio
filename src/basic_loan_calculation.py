import pandas as pd
import numpy_financial as npf
import matplotlib.pyplot as plt
from collections import namedtuple

""" Basic Calculation -- fix coupon, no default, no prepayment """

# loan characteristics
orig_bal = 5e05
coupon = 0.08
term = 120

# payments
periods = range(1, term+1)
int_payment = npf.ipmt(rate=coupon / 12, per=periods, nper=term, pv=-orig_bal)
prin_payment = npf.ppmt(rate=coupon / 12, per=periods, nper=term, pv=-orig_bal)

# stacked area plot with relationship between interest and principle over loan life
# plt.stackplot(periods, int_payment, prin_payment, labels=['Interest', 'Principle'])
# plt.legend(loc='upper left')
# plt.xlabel("Period")
# plt.ylabel("Payment")
# plt.margins(0, 0)
# plt.show()

# cash flow table
cf_table = pd.DataFrame({'Interest': int_payment, 'Principle': prin_payment}, index=periods)
cf_table['Payment'] = cf_table['Interest'] + cf_table['Principle']
cf_table['End Bal'] = orig_bal - cf_table['Principle'].cumsum()
cf_table['Beg Bal'] = [orig_bal] + list(cf_table['End Bal'])[:-1]
cf_table = cf_table[['Beg Bal', 'Payment', 'Interest', 'Principle', 'End Bal']]

# barchart showing scheduled principle
# plt.bar(cf_table.index, cf_table['Beg Bal'], 0.5)
# plt.xlabel("Period")
# plt.ylabel("Remaining Principle")
# plt.margins(0, 0)
# plt.show()

""" Advance Calculation -- floater coupon, default and prepayment assumptions """

Period_CF = namedtuple('Period_CF', 'period, beg_bal, default, interest, scheduled_prin, prepay, end_bal')

# loan characteristics
orig_bal = 5e05
spread = 0.04
term = 120

# assumptions
default_curves = pd.read_csv('./default_curves.csv', header=0, index_col=0)
sonia = pd.read_csv('./sonia.csv', header=0, index_col=0)


def calculate_amortisation(interest_rate_curve, cpr, default_rate, default_curve, lgd, recovery_lag):
    """

    Args:
        interest_rate_curve (str): name of the interest rate curve assumption (e.g., 3m_forward, up_stress)
        cpr (float): CPR -- value between 0 and 1
        default_rate (float) cumulative default rate -- value between 0 and 1
        default_curve (str): name of the default timing curve (e.g., Front_10yr')
        lgd (float): loss given default
        recovery_lag (int): number of months between default and recovery

    Returns:
        cf_df (pd.DataFrame): cash flow table - each row represents a period.
            The columns are: beg_bal, default, interest, scheduled_prin, prepay, end_bal
    """

    period = 1
    result = []
    end_bal = orig_bal
    smm = 1 - (1 - cpr) ** (1 / 12)
    while round(end_bal, 0) > 0 and period <= term:

        beg_bal = end_bal
        flt_coupon = (spread + sonia.loc[period, interest_rate_curve]) / 12
        default = orig_bal * default_rate * default_curves.loc[period, default_curve]
        pmt_i = npf.pmt(rate=flt_coupon, nper=term - period + 1, pv=-(beg_bal - default))
        interest = (beg_bal - default) * flt_coupon
        scheduled_prin = pmt_i - interest
        prepayment = max(0, (min(beg_bal - default - scheduled_prin, smm * (beg_bal - scheduled_prin))))
        end_bal = beg_bal - default - scheduled_prin - prepayment

        result.append(Period_CF(period, beg_bal, default, interest, scheduled_prin, prepayment, end_bal))
        period += 1

    cf_df = pd.DataFrame(result)
    cf_df.set_index('period')
    cf_df['loss'] = cf_df['default'] * lgd
    cf_df['recovery'] = cf_df['default'] * (1 - lgd)
    cf_df['loss'] = cf_df['loss'].shift(recovery_lag).fillna(0)
    cf_df['recovery'] = cf_df['recovery'].shift(recovery_lag).fillna(0)
    return cf_df


plt.figure()
cf_table = calculate_amortisation(
    interest_rate_curve='down_stress', cpr=0.0, default_rate=0.2, default_curve='Back_10yr', lgd=0.5, recovery_lag=3)
cf_table[['interest', 'scheduled_prin', 'prepay', 'recovery']].plot.area()
plt.show()

cf_table = calculate_amortisation(
    interest_rate_curve='down_stress', cpr=0.00, default_rate=0.2, default_curve='Front_10yr', lgd=0.5, recovery_lag=3)
cf_table[['interest', 'scheduled_prin', 'prepay', 'recovery']].plot.area()
plt.show()
