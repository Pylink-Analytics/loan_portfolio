import copy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class Loan:

    def __init__(self, loan_id, orig_balance, coupon, term):
        """

        Args:
            loan_id (int):
            orig_balance (float):
            coupon (float):
            term (int): number of months
        """
        self.loan_id = loan_id
        self.orig_balance = orig_balance
        self.coupon = coupon
        self.term = term
        self.cash_flow_df = pd.DataFrame()

    def generate_cash_flows(self):
        """ overridden in the sub-classes

        Returns:
            cash_flow_df (pd.DataFrame): cash flow table (no default, no prepayment)
        """
        return pd.DataFrame()

    def visualize_cash_flows(self):
        """ stack plot chart for cash flows """

        plt.plot([], [], color='green', label='interest', linewidth=3)
        plt.plot([], [], color='blue', label='principal', linewidth=3)

        plt.stackplot(
            self.cash_flow_df.index, self.cash_flow_df.interest, self.cash_flow_df.principal, colors=['green', 'blue'])

        plt.xlabel('months')
        plt.ylabel('payment')
        plt.title('Loan Amortisation')
        plt.legend()
        plt.show()


class FixInstalmentLoan(Loan):

    def generate_cash_flows(self):
        """

        Returns:
            cash_flow_df (pd.DataFrame): cash flow table (no default, no prepayment)
        """

        cash_flows = []
        curr_bal = copy.deepcopy(self.orig_balance)
        installment = np.pmt(rate=self.coupon / 12, nper=self.term, pv=-self.orig_balance)

        p = 0
        while p <= self.term:
            p += 1
            interest = curr_bal * self.coupon / 12
            principal = installment - interest
            cash_flows.append({
                'beg_bal': curr_bal,
                'interest': interest,
                'principal': principal,
                'payment': installment,
                'end_bal': curr_bal - principal,
            })
            curr_bal -= principal

        self.cash_flow_df = pd.DataFrame(cash_flows)
        return self.cash_flow_df


class VectorAmortisationLoan(Loan):

    def __init__(self, loan_id, orig_balance, coupon, term, vector):
        super(VectorAmortisationLoan, self).__init__(loan_id, orig_balance, coupon, term)
        self.vector = vector

    def generate_cash_flows(self):
        """

        Returns:
            cash_flow_df (pd.DataFrame): cash flow table (no default, no prepayment)
        """

        self.cash_flow_df = pd.DataFrame()
        return self.cash_flow_df


class BulletPayment(Loan):

    def generate_cash_flows(self):
        """

        Returns:
            cash_flow_df (pd.DataFrame): cash flow table (no default, no prepayment)
        """

        interest = self.orig_balance * self.coupon / 12
        cash_flows = {
            'beg_bal': [self.orig_balance] * self.term,
            'interest': [interest] * self.term,
            'principal': [0] * self.term,
            'payment': [interest] * self.term,
            'end_bal': [self.orig_balance] * self.term}

        cash_flows['end_bal'][-1] = 0
        cash_flows['principal'][-1] = self.orig_balance
        cash_flows['payment'][-1] += self.orig_balance

        self.cash_flow_df = pd.DataFrame(cash_flows)
        return self.cash_flow_df
