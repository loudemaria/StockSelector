from datetime import date

def get_date_difference(date1, date2):
    difference = date2 -date1
    return difference.days

date_bought = date(2023, 7, 31)
date_to_sell = date(2023, 8, 14)
price_paid = 52.31

number_of_days_held = get_date_difference(date_bought, date_to_sell)

stop_loss_value = price_paid*(1+((0.262/365)*number_of_days_held))
stop_loss_activation = stop_loss_value * 1.01

print ("Stop loss value = " + str(stop_loss_value))
print ("Stop loss activation = " + str(stop_loss_activation))
