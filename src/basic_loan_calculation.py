import numpy_financial as npf
import pandas as pd
import matplotlib.pyplot as plt

# reading loan_tape.csv into a pandas dataframe
loan_tape = pd.read_csv('src/loan_tape.csv', header=0)

# setting up the assumptions from the dataframe
orig_bal = loan_tape['orig_balance'][0]
start_bal = orig_bal
coupon = loan_tape['coupon'][0]/12
term = loan_tape['term'][0]

# intialising lists
interest_payment = []
principle_payment = []
amortisation_profile = []
periods = range(1, term + 1)

# creating payment vectors
interest_payment = -npf.ipmt(rate=coupon, per=periods, nper=term, pv=orig_bal)
principle_payment = -npf.ppmt(rate=coupon, per=periods, nper=term, pv=orig_bal)

# loop to create scheduled principle
for period in periods:
    prin_paid = principle_payment[period - 1]
    end_bal = start_bal - prin_paid
    amortisation_profile.append(round(end_bal, 4) + 0)
    start_bal = end_bal

# appending period 0 to the periods and the scheduled principle lists
payment_periods = [0] + list(periods)
amortisation_profile = [orig_bal] + amortisation_profile

# storing results in a dictionary and then converting to pandas dataframe
results = {'Period': payment_periods, 'Scheduled Principle': amortisation_profile}
results_df = pd.DataFrame(results)

# stacked area plot with relationship between interest and principle over loan life
plt.stackplot(periods, interest_payment, principle_payment, labels=['Interest', 'Principle'])
plt.legend(loc='upper left')
plt.xlabel("Period")
plt.ylabel("Payment")
plt.margins(0, 0)
plt.show()

# barchart showing scheduled principle
plt.bar(results_df['Period'], results_df['Scheduled Principle'], 0.5)
plt.xlabel("Period")
plt.ylabel("Remaining Principle")
plt.margins(0, 0)
plt.show()

