import matplotlib.pyplot as plt
import plotly.express as px


def visualize_cash_flows(cash_flow_df):
    """ stack plot chart for cash flows """

    plt.plot([], [], color='green', label='interest', linewidth=3)
    plt.plot([], [], color='blue', label='principal', linewidth=3)
    plt.plot([], [], color='orange', label='prepayment', linewidth=3)
    plt.plot([], [], color='red', label='recovery', linewidth=3)

    plt.stackplot(
        cash_flow_df.index, cash_flow_df.interest, cash_flow_df.principal, cash_flow_df.prepayment,
        cash_flow_df.recovery, colors=['green', 'blue', 'orange', 'red'])

    plt.xlabel('months')
    plt.ylabel('payment')
    plt.title('Loan Amortisation')
    plt.legend()
    plt.show()


def visualize_cash_flows_2(cash_flow_df):
    """ stack plot chart for cash flows """

    plt.plot([], [], color='green', label='default', linewidth=3)
    plt.plot([], [], color='blue', label='principal', linewidth=3)
    plt.plot([], [], color='orange', label='prepayment', linewidth=3)
    plt.plot([], [], color='red', label='recovery', linewidth=3)

    plt.stackplot(
        cash_flow_df.index, cash_flow_df.default, cash_flow_df.principal,
        cash_flow_df.prepayment, cash_flow_df.recovery, colors=['green', 'blue', 'orange', 'red'])

    plt.xlabel('months')
    plt.ylabel('payment')
    plt.title('Loan Amortisation')
    plt.legend()
    plt.show()


def visualize_cash_flows_3(cash_flow_df):
    """ stack bar chart for cash flows """

    cash_flow_df['period'] = cash_flow_df.index
    fig = px.bar(cash_flow_df, x="period", y=['prepayment', 'principal', 'default', 'interest', 'recovery', ])

    fig.show()
