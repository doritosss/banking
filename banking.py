# Write your code here
import random
import sqlite3

conn = sqlite3.connect('card.s3db')
c = conn.cursor()

# Functions to manipulate the database
def check_ids(id_account):
    c.execute('SELECT id FROM card WHERE id=?', (id_account,))
    return c.fetchone()


def create_account_in_db(id_account, card_number, pin):
    c.execute('INSERT INTO card VALUES (?, ?, ?, ?)', (id_account, card_number, pin, 0))
    conn.commit()
    print("Your card has been created")
    print("Your card number:")
    c.execute('SELECT number FROM card WHERE id=?', (id_account,))
    print(c.fetchone()[0])
    print("Your card PIN:")
    c.execute('SELECT pin FROM card WHERE id=?', (id_account,))
    print(c.fetchone()[0])


# Return the account id to make operations in that account if the login is correct, otherwise return false
def check_login_in_db(card_number, pin):
    c.execute('SELECT number, pin, id FROM card WHERE number=?', (card_number,))
    account = c.fetchone()
    if account is None:
        return False
    else:
        if account[1] == pin:
            return account[2]
        else:
            return False


def get_balance(id_account):
    c.execute('SELECT balance FROM card WHERE id=?', (id_account,))
    return c.fetchone()[0]


def get_id(number):
    c.execute('SELECT id FROM card WHERE number=?', (number,))
    return c.fetchone()[0]


# Functions to create the account parameters (id, card number, pin)
def generate_id():
    id_account = ""
    for i in range(9):
        id_account += str(random.randint(0, 9))
    return id_account


# Generate the number for the card in the form 400000 + account id (9 digits) + checksum number = 16 digits
def generate_card_number(id_account):
    number = "400000" + id_account
    checksum_number = luhn_checksum_gen(number)
    number += checksum_number
    return number


# Generate the last digit for the card number using the luhn algorithm
def luhn_checksum_gen(number):
    numbers = split_number(number)
    # Multiply odd digits by 2 (even in python list 0 - 14)
    for i in range(0, 15, 2):
        numbers[i] = numbers[i] * 2
    # Subtract 9 to numbers over 9
    for i in range(15):
        if numbers[i] > 9:
            numbers[i] -= 9
    # Add al numbers
    sum_card_numbers = 0
    for i in range(15):
        sum_card_numbers += numbers[i]
    # Get the checksum number for the card
    n = sum_card_numbers % 10
    if n == 0:
        checksum_number = 0
    else:
        checksum_number = 10 - n
    return str(checksum_number)


# Transform the card number from a string to an array of int
def split_number(number):
    return [int(char) for char in number]


def generate_card_pin():
    pin = ""
    for i in range(4):
        pin += str(random.randint(0, 9))
    return pin


# This function con the functions to generate account parameters and create the registry in the DB
def create_account():
    # loop to generate a unique card number
    while True:
        id_account = generate_id()  # return string
        if check_ids(int(id_account)) is None:
            card_number = generate_card_number(id_account)  # return string
            pin = generate_card_pin()  # return string
            create_account_in_db(id_account, card_number, pin)
            break


# Functions to operate the log in menu
def login():
    x = False
    print("Enter your card number:")
    number = input()
    print("Enter your PIN:")
    pin = input()

    is_logged = check_login_in_db(number, pin)
    if is_logged:
        print("You have successfully logged in!")
        x = is_logged
    else:
        print("Wrong card number or PIN!")
    return x


def update_income(id_account, money):
    with conn:
        c.execute('UPDATE card SET balance=? WHERE id=?', (money, id_account))


def add_income(id_account, income):
    income += get_balance(id_account)
    update_income(id_account, income)


# Check if the user tries to transfer money to himself
def check_accounts(id_card, other_number_card):
    c.execute('SELECT number FROM card WHERE id=?', (id_card,))
    this_number = c.fetchone()
    if this_number[0] == other_number_card:
        print("You can't transfer money to the same account!")
        return False
    else:
        return True


# Check if the card number is consistent with the checksum system
def checksum_number(number):
    numbers = split_number(number)
    # Multiply odd digits by 2 (even in python list 0 - 14)
    for i in range(0, 15, 2):
        numbers[i] = numbers[i] * 2
    # Subtract 9 to numbers over 9
    for i in range(15):
        if numbers[i] > 9:
            numbers[i] -= 9
    # Add al numbers
    sum_card_numbers = 0
    for i in range(16):
        sum_card_numbers += numbers[i]
    if sum_card_numbers % 10 == 0:
        return True
    else:
        print("Probably you made a mistake in the card number. Please try again!")
        return False


# Check if the card number exist in the database to make the transfer
def check_account_exist(number):
    c.execute("SELECT number FROM card WHERE number=?", (number,))
    if c.fetchone() is None:
        print("Such a card does not exist.")
        return False
    else:
        return True


# Function to make the whole verifications to allow transfer money from the user account to other account
def transfer_money(id_account):
    print("Transfer")
    print("Enter card number:")
    card_number = input()
    if check_accounts(id_account, card_number):
        if checksum_number(card_number):
            if check_account_exist(card_number):
                print("Enter how much money you want to transfer:")
                money_to_transfer = int(input())
                if money_to_transfer <= get_balance(id_account):
                    money = get_balance(id_account) - money_to_transfer
                    update_income(id_account, money)
                    id_other_account = get_id(card_number)
                    add_income(id_other_account, money_to_transfer)
                    print("Success!")
                else:
                    print("Not enough money!")


def delete_account(id_account):
    with conn:
        c.execute("DELETE FROM card WHERE id=?", (id_account,))
    print("The account has been closed!")


# Main menu program
option = 6

# First menu
while option != 0:
    print("1. Create an account")
    print("2. Log into account")
    print("0. Exit")
    option = int(input())

    if option == 1:
        create_account()
    elif option == 2:
        log_in = login() # returns id account or false
        # Second menu for users logged in
        if log_in:
            while True:
                print("1. Balance")
                print("2. Add income")
                print("3. Do transfer")
                print("4. Close account")
                print("5. Log out")
                print("0. Exit")
                option_2 = int(input())

                if option_2 == 1:
                    print("Balance: " + str(get_balance(log_in)))
                elif option_2 == 2:
                    print("Enter income:")
                    income = int(input())
                    add_income(log_in, income)
                    print("Income was added!")
                elif option_2 == 3:
                    transfer_money(log_in)
                elif option_2 == 4:
                    delete_account(log_in)
                    break
                elif option_2 == 5:
                    print("You have successfully logged out!")
                    break
                elif option_2 == 0:
                    option = option_2
                    break

    elif option == 0:
        break
