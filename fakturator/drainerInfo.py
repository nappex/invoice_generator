import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable, Optional

from config.settings import DEFAULT_CONFIG
from fakturator.fileHandler import get_config, read_yaml, write_to_yaml
from fakturator.input_validator import positive_int, input_y_N, validate_date


DATABASES_DIR = Path(DEFAULT_CONFIG['DATABASE_DIR'])
CUSTOMERS_DB = DATABASES_DIR / DEFAULT_CONFIG['CUSTOMERS_DB_FILE']
INVOICES_DB = DATABASES_DIR / DEFAULT_CONFIG['INVOICES_DB_FILE']

CONFIG_DIR = Path(DEFAULT_CONFIG['CONFIG_DIR'])
INPUT_DATA = CONFIG_DIR / DEFAULT_CONFIG['INPUT_DATA']
SUPPLIER = CONFIG_DIR / DEFAULT_CONFIG['SUPPLIER']
LAST_DATA = CONFIG_DIR / DEFAULT_CONFIG['LAST_DATA']

def get_customer():
    def from_database():
        customers_db = get_config(CUSTOMERS_DB)
        customers_names = customers_db.sections()
        print_menu(customers_names,"CUSTOMERS DATABASE", "back")

        customer = get_value_from_list(customers_names)
        if customer is not None:
            return {**customers_db[customer]}

    def from_yaml():
        data = read_yaml(INPUT_DATA)
        key = 'customer'
        try:
            return data[key]
        except KeyError:
            print(f"Key error {key} is not in {INPUT_DATA}")


    customer_menu = {
        "Get customer from database": from_database,
        f"Get customer from {INPUT_DATA}": from_yaml,
    }

    customer_data = None
    while customer_data is None:
        print_menu(customer_menu, title="CUSTOMER MENU")
        program_key = get_value_from_list(customer_menu)

        if program_key is None:
            sys.exit("Application is stopped: no customer data")

        else:
            run_program = customer_menu[program_key]
            customer_data = run_program()

            if customer_data is not None:
                return customer_data


def get_supplier():
    return read_yaml(SUPPLIER)


def get_payment_info(customer_name):
    def from_database():
        invoices_db = read_yaml(INVOICES_DB)
        try:
            invoices_db = invoices_db[customer_name]
        except KeyError:
            print(f"Invoices not found for {customer_name} in database")
            print(f"Update DB {INVOICES_DB}")
            return None

        print_menu(invoices_db, "DATABASE OF INVOICES", "back")

        invoice_name = get_value_from_list(invoices_db)

        if invoice_name is not None:
            invoice = {**invoices_db[invoice_name]}

            if customer_name == 'new_customer':
                text = invoice['invoice_subjects'][0]['subject']
                d = date.today()

                if invoice_name == "Dodavka oleje":
                    quarter = positive_int("Kvartál: ")
                    text = text.replace("{{quarter}}", str(quarter))
                    text = text.replace("{{year}}", d.year)

                elif invoice_name == "Udrzba auta":
                    d = d.replace(month=d.month - 1).strftime('%m/%Y')
                    text = text.replace("{{date}}", d)

                elif invoice_name == "Pronajem auta":
                    text = text.replace("{{date}}", d.strftime('%m/%Y'))

                invoice['invoice_subjects'][0]['subject'] = text

            return {**invoice}

    def from_yaml():
        delete_key = 'customer'
        data = read_yaml(INPUT_DATA)
        data.pop(delete_key, None)

        return data


    payment_menu = {
        "Get payment info from database": from_database,
        f"Get payment from {INPUT_DATA}": from_yaml,
    }

    payment_data = None
    while payment_data is None:
        print_menu(payment_menu, title="PAYMENT MENU")

        program_key = get_value_from_list(payment_menu)

        if program_key is None:
            sys.exit("Application is stopped: no payment data")

        else:
            run_program = payment_menu[program_key]
            payment_data = run_program()

            if payment_data is not None:
                return payment_data


def get_dates():
    date_issue = date.today()
    date_due = date_issue + timedelta(days=14)

    if input_y_N("Change length of date due (default 14 days)"):
        num_days = positive_int("Write the number of days to date due: ")
        date_due = date_issue + timedelta(days=num_days)

    while True:
        print("Insert info about filling date:")
        day = positive_int("Day: ")
        month = positive_int("Month: ")
        year = get_year()

        if validate_date(year, month, day):
            date_fill = date(year=year, month=month, day=day)

            return {
                "date_issue": date_issue.strftime("%d.%m.%Y"),
                "date_due": date_due.strftime("%d.%m.%Y"),
                "date_fill": date_fill.strftime("%d.%m.%Y"),
            }


def get_year():
    next_year = date.today().year + 1
    last_year = date.today().year - 1

    while True:
        year = positive_int("Year: ")

        if last_year <= year <= next_year:
            return year

        print(f"Wrong year must be {last_year} .. {next_year}.")


def get_invoice_number():
    """
    Created number invoice from file last_invoice_data.ini
    and actual year. This two values are joined together and
    return as string.
    """
    data = read_yaml(LAST_DATA)
    last_year = data["year"]
    today_date = date.today()
    today_year = today_date.year

    if last_year == today_year:
        num = data['number'] + 1
    else:
        num = 1

    return str(today_year) + str(num).rjust(3, "0")


def overwrite_last_data(invoice_number, customer, yamlfile=LAST_DATA):
    data = {}
    number = int(invoice_number[4:])

    today = date.today()
    data['year'] = today.year
    data['number'] = number
    data['to_company'] = customer
    data['date'] = today

    write_to_yaml(data, yamlfile)


def print_menu(
            iterable: Iterable[str],
            title: str ="MENU",
            exit_text: str ="exit program") -> None:

    iterable = list(iterable)
    divide_line = (max(map(len, iterable + [title]))+6)*"-" + "\n"
    menu = "\n" + title + "\n"
    menu += divide_line

    for num, menu_option in enumerate(iterable):
        menu += f"{num:<2} - {menu_option} \n"

    menu += f"{'x':<2} - {exit_text}\n"
    menu += divide_line

    print(menu)


def get_value_from_list(
        iterable: Iterable[str]) -> Optional[str]:
    """
    Function check if your choice for choices in list are available.
    If your input is correct, than function return element from list you were
    choosing. So function have one necessary parametr - list.
    """
    sequence = list(iterable)
    while True:
        user_input = input("Your choice: ")
        if user_input.lower() == "x":
            return None
        try:
            i = int(user_input)
            return sequence[i]
        except ValueError as err:
            print(f"{err}: You don't type a number.")
        except IndexError:
            print("Number is not available in choices.")