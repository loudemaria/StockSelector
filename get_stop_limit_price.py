from datetime import date

def get_date_difference(date1, date2):
    difference = date2 -date1
    return difference.days

date_bought = date(2023, 11, 10)
date_to_sell = date(2024, 2, 5)
price_paid = 115.88

number_of_days_held = get_date_difference(date_bought, date_to_sell)

stop_loss_value = price_paid*(1+((0.262/365)*number_of_days_held))
stop_loss_activation = stop_loss_value * 1.01

print ("Stop loss value = " + str(stop_loss_value))
print ("Stop loss activation = " + str(stop_loss_activation))
