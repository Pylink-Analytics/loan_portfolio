import numpy_financial as npf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# reading loan_tape.csv into a pandas dataframe
loan_tape = pd.read_csv('src/loan_tape.csv', header=0)

# setting up the assumptions from the dataframe
orig_bal = 5e05
coupon = 0.08 / 12
term = 120

# intialising lists
periods = range(1, term + 1)
payment_periods = [0] + list(periods)

# creating payment vectors
interest_payment = list(npf.ipmt(rate=coupon, per=periods, nper=term, pv=-orig_bal))
principle_payment = list(npf.ppmt(rate=coupon, per=periods, nper=term, pv=-orig_bal))
scheduled_principle = [orig_bal] * (term + 1)

results = {
            'Period': payment_periods,
            'Interest': [0] + interest_payment,
            'Principle': [0] + principle_payment,
            'Scheduled Principle': scheduled_principle,
           }

result_df = pd.DataFrame(results)
result_df['Scheduled Principle'] = np.maximum((result_df['Scheduled Principle'] - result_df['Principle'].cumsum()), 0)

# stacked area plot with relationship between interest and principle over loan life
plt.stackplot(list(periods), interest_payment, principle_payment, labels=['Interest', 'Principle'])
plt.legend(loc='upper left')
plt.xlabel("Period")
plt.ylabel("Payment")
plt.margins(0, 0)
plt.show()

# barchart showing scheduled principle
plt.bar(result_df['Period'], result_df['Scheduled Principle'], 0.5)
plt.xlabel("Period")
plt.ylabel("Remaining Principle")
plt.margins(0, 0)
plt.show()
