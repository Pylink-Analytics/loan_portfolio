from src import loans

loan_1 = loans.BulletPayment(loan_id=1, orig_balance=1000000, coupon=0.05, term=120)
df = loan_1.generate_cash_flows()
# loan_1.visualize_cash_flows()

print(df.tail(5))
