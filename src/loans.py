import datetime
from copy import copy
import numpy as np
import pandas as pd
from collections import OrderedDict

amortisation_vectors = pd.read_csv('src/amortisation_profiles.csv', header=0, index_col=0)

class Loan:

    def __init__(self, loan_id, orig_balance, coupon, term, amortisation_type, vector):
        """

        Args:
            loan_id (int):
            orig_balance (float):
            coupon (float):
            term (int): number of months
            amortisation_type (str): 'fix_instalment', 'vector', 'bullet'
            vector (list):
        """
        self.loan_id = loan_id
        self.orig_balance = orig_balance
        self.coupon = coupon
        self.term = term
        self.amortisation_type = amortisation_type
        self.vector = vector
        self.cash_flow_df = pd.DataFrame()

    def generate_scheduled_amortisation_profile(self):
        """ overridden in the sub-classes

        Returns:
            scheduled_bal (list): beginning balance for each period (It also contains a zero in the period after
            maturity. Therefore the length of the vector is self.term + 1).
        """
        scheduled_bal = []
        return scheduled_bal

    def generate_cash_flows(self, cpr, cdr):
        """

        Constant Default Rate (CDR):
        It refers to the percentage of mortgages within a pool of loans for which the mortgagors have fallen more than 90
        days behind. It is a measure used to analyze losses within mortgage-backed securities.

        Conditional Prepayment Rate (CPR):
        It is a loan prepayment rate equivalent to the proportion of a loan pool's principal that is assumed to be paid
        off ahead of time in each period. The calculation of this estimate is based on a number of factors, such as
        historical prepayment rates for previous loans similar to ones in the pool and future economic outlooks.

        Single Monthly Mortality (SMM):
        It is a measure of the prepayment rate of a mortgage-backed security (MBS). As the term suggests, the single
        monthly mortality measures prepayment in a given month and is expressed as a percentage.

            SMM = 1 – (1 – CPR) ^ (1 / 12)

        Returns:
            cash_flow_df (pd.DataFrame): cash flow table
        """

        scheduled_bal = self.generate_scheduled_amortisation_profile()
        end_bal = copy(self.orig_balance)

        smm_cpr = 1 - (1 - cpr) ** (1 / 12)
        smm_cdr = 1 - (1 - cdr) ** (1 / 12)

        p = 0
        while p <= self.term and round(end_bal, 0) > 0:
            p += 1

            beg_bal = end_bal
            default = beg_bal * smm_cdr
            prepayment = (beg_bal - default) * smm_cpr * (scheduled_bal[p] / scheduled_bal[p - 1])
            principal = (beg_bal - default) * (1 - scheduled_bal[p] / scheduled_bal[p - 1])
            end_bal = beg_bal - default - principal - prepayment

            yield OrderedDict([
                ('period', p),
                ('beg_bal', beg_bal),
                ('principal', principal),
                ('default', default),
                ('prepayment', prepayment),
                ('end_bal', end_bal)])

    def create_cf_dict(self, cpr, cdr):

        end_bal = []
        scheduled_bal = self.generate_scheduled_amortisation_profile()
        orig_bal = copy(self.orig_balance)
        end_bal.append(orig_bal)

        smm_cpr = 1 - (1 - cpr) ** (1 / 12)
        smm_cdr = 1 - (1 - cdr) ** (1 / 12)

        p = 0
        period = []
        beg_bal = []
        default = []
        prepayment = []
        principal = []

        while p <= self.term and round(end_bal[-1], 0) > 0:
            p += 1
            period.append(p)
            beg_bal.append(end_bal[-1])
            default.append(beg_bal[-1] * smm_cdr)
            prepayment.append((beg_bal[-1] - default[-1]) * smm_cpr * (scheduled_bal[p] / scheduled_bal[p - 1]))
            principal.append((beg_bal[-1] - default[-1]) * (1 - scheduled_bal[p] / scheduled_bal[p - 1]))
            end_bal.append(beg_bal[-1] - default[-1] - principal[-1] - prepayment[-1])

        end_bal.pop(0)
        return OrderedDict([
                ('period', period),
                ('beg_bal', beg_bal),
                ('principal', principal),
                ('default', default),
                ('prepayment', prepayment),
                ('end_bal', end_bal)])

    def generate_cash_flow_table(self, cpr, cdr, recovery, recovery_lag, type):
        """ create full cash flow table including interest, principal, default, prepayment, recovery, etc.

        Args:
            cpr (float): conditional prepayment rate -- annual
            cdr (float): constant default rate -- annual
            recovery (float): 1 - loss severity
            recovery_lag (int): no of month between default and liquidation

        Returns:
            cash_flow_df (pd.DataFrame): cash flow table
        """
        if type == "Generator":
            cash_flow_df = pd.DataFrame(self.generate_cash_flows(cpr, cdr))
        elif type == "Dictionary":
            cash_flow_df = pd.DataFrame(self.create_cf_dict(cpr, cdr))
        else:
            cash_flow_df = pd.DataFrame(self.generate_cash_flows(cpr, cdr))
        cash_flow_df.set_index('period', inplace=True, drop=True)

        # adding new columns
        cash_flow_df['interest'] = cash_flow_df['beg_bal'] * self.coupon / 12
        cash_flow_df['liquidation'] = cash_flow_df['default']
        cash_flow_df['loss'] = cash_flow_df['default'] * (1 - recovery)
        cash_flow_df['recovery'] = cash_flow_df['default'] * recovery

        # shifting by recovery lag
        cash_flow_df['liquidation'] = cash_flow_df['liquidation'].shift(recovery_lag).fillna(0)
        cash_flow_df['loss'] = cash_flow_df['loss'].shift(recovery_lag).fillna(0)
        cash_flow_df['recovery'] = cash_flow_df['recovery'].shift(recovery_lag).fillna(0)

        cash_flow_df['total_princ'] = cash_flow_df['principal'] + cash_flow_df['recovery'] + cash_flow_df['prepayment']
        cash_flow_df['payment'] = cash_flow_df['interest'] + cash_flow_df['total_princ']

        self.cash_flow_df = cash_flow_df
        return self.cash_flow_df

    def calculate_wal(self):
        """
        calculate the tranche's waited average life

        multiply the time (in years) since the closing date and the principal payment. Then divide it by the total prin
        paid.

        Returns:
            wal (float): weighted average life
        """
        wal = np.sum(self.cash_flow_df['total_princ'] * self.cash_flow_df.index / 12) / self.orig_balance
        return wal

    def check_pandas_speeds(self, cpr, cdr):
        """ perform three methods of filling a pandas DF to show speed differences"""

        beg_time = datetime.datetime.now()
        df_1 = pd.DataFrame(self.generate_cash_flows(cpr, cdr))
        runtime = ((datetime.datetime.now() - beg_time).total_seconds()) * 1e09
        print("Generator: " + str(runtime) + "ns")

        beg_time = datetime.datetime.now()
        # dict_2 = self.create_cf_dict(cpr, cdr)
        df_2 = pd.DataFrame(self.create_cf_dict(cpr, cdr))
        runtime = ((datetime.datetime.now() - beg_time).total_seconds()) * 1E09
        print("Generator: " + str(runtime) + "ns")




class FixInstalmentLoan(Loan):

    def generate_scheduled_amortisation_profile(self):
        """ calculate the beginning balance for each periods based on no default, no prepayment (scheduled amortisation)

        The total payment is the same for each periods but the interest vs principal proportion is changing overtime.
        (The principal portion is increasing.)

        Formula:
            - numpy.pmt (to calculate the fix instalment)
            - numpy.ppmt (to calculate the principal portion for a given period or periods)
            - numpy.ipmt (to calculate the interest portion for a given period or periods)

        Returns:
            scheduled_bal (list): beginning balance for each period (It also contains a zero in the period after
            maturity. Therefore the length of the vector is self.term + 1).
        """
        periods = range(1, self.term + 1)
        principal_vector = np.ppmt(rate=self.coupon / 12, per=periods, nper=self.term, pv=-self.orig_balance)
        scheduled_bal = [self.orig_balance] + list(self.orig_balance - principal_vector.cumsum())
        return scheduled_bal


class VectorAmortisationLoan(Loan):

    def generate_scheduled_amortisation_profile(self):
        """ calculate the beginning balance for each periods based on no default, no prepayment (scheduled amortisation)

        In this case the amortisation of the loan defined by a vector (input variable) which represents the actual
        principal payment for each period.

        Returns:
            scheduled_bal (list): beginning balance for each period (It also contains a zero in the period after
            maturity. Therefore the length of the vector is self.term + 1).
        """

        vector = amortisation_vectors[self.vector]
        scheduled_bal = [self.orig_balance] + list(self.orig_balance - vector.cumsum())
        return scheduled_bal


class BulletPayment(Loan):

    def generate_scheduled_amortisation_profile(self):
        """ calculate the beginning balance for each periods based on no default, no prepayment (scheduled amortisation)

        Interest Only (IO):
        There is no principal payment during the life of the loan but there is a big bullet payment at maturity that is
        the full notional (original balance) of the loan.

        Returns:
            scheduled_bal (list): beginning balance for each period (It also contains a zero in the period after
            maturity. Therefore the length of the vector is self.term + 1).
        """

        scheduled_bal = [self.orig_balance] * self.term + [0]
        return scheduled_bal
