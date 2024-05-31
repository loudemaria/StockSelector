from datetime import date
from datetime import datetime

def get_date_difference(date1, date2):
    difference = date2 -date1
    return difference.days

def get_stop_limit_price(arg1):
    input_string = str(arg1)
    input_string_split = input_string.split(", ")
    date_bought = datetime.strptime(input_string_split[1], '%m/%d/%Y').date()

    # *****  CHANGE THIS!! *****
    date_to_sell = date(2024, 6, 3)

    price_paid = float(input_string_split[2])

    number_of_days_held = get_date_difference(date_bought, date_to_sell)

    stop_loss_value = price_paid*(1+((0.262/365)*number_of_days_held))
    stop_loss_activation = stop_loss_value * 1.01

    print (input_string_split[0])
    print ("Stop loss value = " + str(stop_loss_value))
    print ("Stop loss activation = " + str(stop_loss_activation))
    print ()

with open ('Positions.txt') as my_file:
    for my_line in my_file:
        if 'Roth' in my_line:
            print("*****")
            print (my_line)
        elif 'Regular' in my_line:
            print("*****")
            print (my_line)
        else:
            if my_line.strip():
                get_stop_limit_price(my_line)
