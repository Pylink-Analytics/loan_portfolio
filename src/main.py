import numpy as np
import pandas as pd

from src import loans
from src.charts import visualize_cash_flows_3


loan_classes = {
    'fix_instalment': loans.FixInstalmentLoan,
    'bullet': loans.BulletPayment,
    'vector': loans.VectorAmortisationLoan}

portfolio = []
loan_tape = pd.read_csv('src/loan_tape.csv', header=0)
for index, loan_data in loan_tape.iterrows():
    portfolio.append(loan_classes[loan_data['amortisation_type']](**loan_data))


def run_portfolio_cash_flows(cpr, cdr, recovery, recovery_lag):
    total_cf = pd.DataFrame()
    for loan in portfolio:
        df = loan.generate_cash_flow_table(cpr=cpr, cdr=cdr, recovery=recovery, recovery_lag=recovery_lag)
        total_cf = total_cf.add(df, fill_value=0)
    return total_cf


wals = []
for i in range(10):
    total_cf = run_portfolio_cash_flows(cpr=0, cdr=i/100, recovery=0.65, recovery_lag=6)
    wal = np.sum(total_cf['total_princ'] * total_cf.index / 12) / total_cf.loc[1, 'beg_bal']
    wals.append(wal)


import matplotlib.pyplot as plt
plt.plot(wals)
plt.show()

loan_1 = portfolio[11]
print(loan_1.calculate_wal())

visualize_cash_flows_3(total_cf)

