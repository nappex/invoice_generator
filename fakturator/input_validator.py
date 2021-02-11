from datetime import date


def positive_int(question=""):
    while True:
        num = input(question)
        try:
            num = int(num)
            if num < 1:
                print("\nNumber has to be higher than 1")
                continue
            return num

        except ValueError as err:
            print(f"{err}: You don't type a number (integer).")


def input_y_N(question=""):
    ask = question.strip()
    while True:
        answer = input(f"\n{ask} (y/N): ")
        if not answer or answer == "n":
            return False
        elif answer == "y":
            return True
        else:
            print("Wrong answer. Try again !")


def validate_date(year, month, day):
    try:
        date(year=year, month=month, day=day)
        return True
    except ValueError as fail:
        print(f"{fail}: wrong date !")
        return False


def input_discount_percentage(question=""):
    discount = positive_int(question)
    while discount > 100:
        print("Max. percentage discount is 100 %.")
        discount = positive_int(question)

    return discount # in %
