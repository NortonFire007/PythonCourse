import create_api_module
from money_transfer import perform_money_transfer
from part4 import randomly_choose_users_for_discount, get_debtors_names, get_bank_with_the_biggest_capital, \
    get_the_oldest_client_bank, delete_accounts_and_users_without_full_info, get_user_last_three_months_transactions, \
    get_bank_with_highest_unique_outbound_users


def main():
    users = [
        {'id': 5385, 'user_full_name': 'John O', 'birth_day': '1992-03-17', 'accounts': 'ID--r5-gry-70325-g'},
        {'id': 9064, 'user_full_name': 'Jane Babel', 'birth_day': '1984-07-10', 'accounts': 'ID--a1-b-123456-x7'}
    ]

    banks_data = [
        {'name': 'Bank Ad', 'id': 31},
        {'name': 'Bank B', 'id': 73}
    ]

    accounts_data = [
        {'user_id': 5777, 'type': 'debit', 'account_number': 'ID--h5-i-567890-q2', 'bank_id': 1, 'currency': 'USD',
         'amount': 5000, 'status': 'silver'},
        {'user_id': 503, 'type': 'credit', 'account_number': 'ID--j3-q-432547-u9', 'bank_id': 2, 'currency': 'EUR',
         'amount': 10000, 'status': 'gold'}
    ]

    create_api_module.add_user(users)
    create_api_module.add_bank(banks_data)
    create_api_module.add_account(accounts_data)

    create_api_module.add_data_from_csv('banks.csv', create_api_module.add_bank)
    create_api_module.add_data_from_csv('accounts.csv', create_api_module.add_account)
    create_api_module.add_data_from_csv('users.csv', create_api_module.add_user)

    create_api_module.modify_row('Account', 7, {'Amount': 8750})
    create_api_module.modify_row('Bank', 57, {'Id': 56, 'Name': 'New Bank Name'})
    create_api_module.delete_row('User', 'Id = 6')

    perform_money_transfer('ID--r5-gry-70325-g', 'ID--u0-vuv-6819-u1', 150)
    perform_money_transfer('ID--j3-q-432547-u9', 'ID--f4-ggg-90123-g', 3200, '2022-08-19 11:42:24')
    perform_money_transfer('ID--j3-q-432547-u9', 'ID--u0-vuv-6819-u1', 1500)
    perform_money_transfer('ID--f4-ggg-90123-g', 'ID--u0-vuv-6819-u1', 15000)

    print(f'Randomly select users from  to receive discounts: {randomly_choose_users_for_discount()}')
    print(f'Names of users who have debts based on account balances: {get_debtors_names()}')
    print(f'The bank with the highest capital in USD: {get_bank_with_the_biggest_capital()}')
    print(f'Get the oldest client bank: {get_the_oldest_client_bank()}')
    print(f'User last three months transactions: {get_user_last_three_months_transactions(503)}')
    print(f'bank with highest unique outbound users: {get_bank_with_highest_unique_outbound_users()}')
    delete_accounts_and_users_without_full_info()


if __name__ == "__main__":
    main()
