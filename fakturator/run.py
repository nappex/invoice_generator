from collections import defaultdict

from fakturator.drainerInfo import (
    get_customer,
    get_supplier,
    get_payment_info,
    get_dates,
    get_invoice_number,
    overwrite_last_data,
)
from fakturator.input_validator import input_discount_percentage, input_y_N
from fakturator.pdf_render import compile_pdf_from_template


def run():
    # set values in dictionary, which will be used for rendering template
    input_data = get_supplier()                                       # supplier
    input_data.update(get_customer())                                 # customer

    customer_name = input_data['customer_name']

    input_data.update(get_payment_info(customer_name=customer_name))  # payment
    input_data.update(get_dates())                                    # dates

    brutto_price = 0
    tax_table = defaultdict(float)
    temp_data = []

    for item in input_data['invoice_subjects']:
        discount = {}
        tax_rate = item["tax_rate"]

        item['sum_netto_price'] = item["netto_price"] * item["quantity"] # sum netto price
        item["tax"] = item["tax_rate"] * item["sum_netto_price"] / 100   # tax
        item['brutto_price'] = item['sum_netto_price'] + item['tax']
        temp_data.extend([item])

        if input_y_N(f"Discount for '{item['subject']}'"):
            text = "Insert discount [%]: "
            discount_percentage = input_discount_percentage(text)
            discount_coef = discount_percentage / 100
            disc_sum_netto_price = (-item['sum_netto_price'] * discount_coef)
            disc_tax = disc_sum_netto_price * tax_rate / 100

            discount['subject'] = f"• SLEVA ( {discount_percentage} % )"
            discount['sum_netto_price'] = disc_sum_netto_price
            discount['brutto_price'] = disc_sum_netto_price + disc_tax
            temp_data.extend([discount])

        brutto_price += item['brutto_price'] + discount.get('brutto_price', 0)
        tax_table[tax_rate] += item['sum_netto_price'] + discount.get('sum_netto_price', 0)


    input_data['invoice_subjects'] = temp_data
    input_data["brutto_price"] = brutto_price - input_data["deposit"]

    tax_table = sorted(tax_table.items(), key=lambda kv: kv[0])
    input_data['tax_table'] = [{  'tax_rate': tax_rate,
                            'sum_netto_price': sum_netto_price,
                            'sum_tax': sum_netto_price * tax_rate / 100} \
                        for tax_rate, sum_netto_price in tax_table
                        ]


    input_data['invoice_number'] = get_invoice_number()

    compile_pdf_from_template('invoice_temp.html', input_data)

    overwrite_last_data(input_data['invoice_number'], customer_name)
