from flask import flash
import string
import cyrtranslit
import datetime
from parking.messages import min_sub_period_msg, max_sub_period_msg, start_date_system_msg, start_date_previous_sub_msg

# datetime formats
dt_format_db = "%Y-%m-%dT%H:%M"
dt_format_display = "%d/%m/%Y %H:%M"
dt_now = datetime.datetime.now
today_datetime = datetime.datetime.today()


# tomorrow's dt, 24h ahead
def day_ahead():
    return datetime.datetime.now() + datetime.timedelta(hours=24)


# lists of numbs
num_to_compare = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
num_plus_to_compare_lst = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "+"]
num_dash_to_compare_lst = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "-"]
address_to_compare_lst = ["'", ".", ",", '"']
blank_space = [" "]
# latin letters list. By adding blank space skips case where there blank space and trigger msg for
# difference between fields. Just remove space msg pop up
latin_letters = list(string.ascii_letters) + blank_space
# gets cyrillic dic from cyrtranslit library
cyrillic_letters_dict = cyrtranslit.TRANSLIT_DICT
# gets only cyrillic characters from the dict
cyrillic_letters = list(cyrillic_letters_dict.get("bg").get('tocyrillic').values()) + blank_space
# no blank space used for address check. This way does not allow empty space for address
latin_letters_no_blank = list(string.ascii_letters)
cyrillic_letters_no_blank = list(cyrillic_letters_dict.get("bg").get('tocyrillic').values())
# lists that contain different elements for different purposes
str_reg_num_latin_compare_lst = latin_letters + num_dash_to_compare_lst
srt_reg_num_cyrillic_compare_lst = cyrillic_letters + num_dash_to_compare_lst
str_address_latin_compare_lst = latin_letters_no_blank + num_dash_to_compare_lst + address_to_compare_lst
str_address_cyrillic_compare_lst = cyrillic_letters_no_blank + num_dash_to_compare_lst + address_to_compare_lst
str_model_latin_compare_lst = latin_letters + num_to_compare
str_model_cyrillic_compare_lst = cyrillic_letters + num_to_compare
str_color_latin_dash_compare_lst = latin_letters + ["-"]
str_color_cyrillic_dash_compare_lst = cyrillic_letters + ["-"]


# display error messages
def display_error_messages(form_var):
    if form_var.errors != {}:
        for err_msg in form_var.errors.values():
            flash(f"{err_msg[0]}",
                  category="info"
                  )


# check for blank spaces
def blank_space_check(form_var: str):
    is_white_space = [i for i in form_var.data if i == " "]
    return is_white_space


# compare str to list for allowed symbols
def validate_check_from_lst(var_to_check: str, lst_to_compare: list):
    is_forbidden_symbol = [i for i in var_to_check if i not in lst_to_compare]
    return is_forbidden_symbol


def first_last_ele_check(var_to_check: str, ele: str):
    # gets the first and the last element of the var and adds them to a list
    first_last_lst = [var_to_check.data[i] for i in (0, -1)]
    is_ele_first_last_symbol = [i for i in first_last_lst if i == ele]
    return is_ele_first_last_symbol


# creates a list of not occupied parking spots. It creates 60 parking spots and reverse the order
def free_parking_spots(db_lst: list):
    # creates 60 parking spots. Parking available spots can be reduced or increased by the second argument
    available_parking_spots = range(1, 61)
    # gets all the occupied parking spots from the DB and adds them to a list
    occupied_spots = [str(elem) for elem in db_lst]
    unoccupied_spots = []
    for spot in available_parking_spots:
        # if spot is not in occupied spots adds it to the unoccupied spot list
        if str(spot) not in occupied_spots:
            unoccupied_spots.append(str(spot))
    return unoccupied_spots


# calculate time differance between two dates
def calculate_days_diff(start_date: datetime, end_date: datetime):
    delta = None
    is_negative = False
    if end_date != start_date:
        if start_date > end_date:
            delta = start_date - end_date
            is_negative = True
        else:
            delta = end_date - start_date
            is_negative = False
    elif start_date == end_date:
        delta = end_date - start_date
    # get difference in days
    days_diff = delta.days
    return days_diff, is_negative


def convert_dt_to_str(dt_format, dt=None):
    if dt is None:
        return datetime.datetime.now().strftime(dt_format)
    else:
        return dt.strftime(dt_format)


def manual_str_char_swap_dt(str_dt: str):
    characters_list = list(str_dt)
    # swap list characters
    characters_list[0], characters_list[1], characters_list[2], characters_list[3], characters_list[4], characters_list[
        5], characters_list[6], characters_list[7], characters_list[8], characters_list[9] = \
        characters_list[8], characters_list[9], "/", characters_list[5], characters_list[6], "/", characters_list[0], \
        characters_list[1], characters_list[2], characters_list[3]
    # convert list back to string
    swapped_str = "".join(characters_list)
    return swapped_str


def convert_str_to_dt(str_dt: str, dt_format: str):
    return datetime.datetime.strptime(str_dt, dt_format)


def validate_datetime_differance(start_dt: datetime, end_dt: datetime, days: datetime):
    # check if start date is equal or bigger then end date or time differance is less the 1 day
    if (start_dt >= end_dt) or (days < 1):
        return min_sub_period_msg
    # check if subscription period is more than one year
    elif days > 366:
        return max_sub_period_msg


def new_entry_validation(current_record, new_entry, is_address: bool = None):
    # skip changes if field is empty or if the change is same as the db record
    if not is_address:
        if (current_record == new_entry) or (new_entry == ""):
            return current_record, True
        else:
            return new_entry, False
    elif is_address:
        if current_record == new_entry:
            return current_record, True
        elif new_entry == "" and current_record != "--":
            return "--", False
        elif new_entry == "" and current_record == "--":
            return current_record, True
        else:
            return new_entry, False


def str_split_pick(str_to_split: str, index: int, return_int: bool = None):
    # empty str
    if str_to_split == "":
        return ""
    else:
        # return_int is used for ids
        if return_int:
            return int(str_to_split.split()[index])
        else:
            return str(str_to_split.split()[index])


def recalculate_sub_tax(old_tax: float, dt_change: int, is_negative: bool):
    # gets subs days before the change
    sub_days = int(old_tax / 5)
    # reducing sub period
    if is_negative:
        new_sub_tax = (sub_days - dt_change) * 5
        sub_tax_diff = old_tax - new_sub_tax
        sub_action = "return"
    # increasing sub period
    else:
        new_sub_tax = (sub_days + dt_change) * 5
        sub_tax_diff = new_sub_tax - old_tax
        sub_action = "receive"
    return "{:.2f}".format(new_sub_tax), sub_action, "{:.2f}".format(sub_tax_diff)


# checks for existing registration number
def db_reg_uniqueness_check(model, form_data: str):
    return model.query.filter_by(vehicle_registration_number=form_data).first()


# checks for existing phone
def db_phone_uniqueness_check(model, form_data: str):
    return model.query.filter_by(phone=form_data).first()


# remove seconds and colon
def format_time(time):
    return ''.join(time.split())[:-3]


def compose_dt(date: str, time: str, db_format: str):
    date = manual_str_char_swap_dt(date)
    time = format_time(time)
    gather_str_dt = date + " " + time
    return convert_str_to_dt(gather_str_dt, db_format)


def sub_expiry_check(end_dt: datetime, now_dt: datetime):
    # checks for subscription overdue expiration. If so calculate extra fee. Also return different start dt,
    # and different start dt info
    if end_dt < now_dt:
        # if differance is less than 24h the day differance will become 1. Otherwise, will calculate the fee
        time_differance_under_a_day = calculate_days_diff(end_dt, now_dt)[0] == 0
        if time_differance_under_a_day:
            overdue_period = 1
        else:
            overdue_period = calculate_days_diff(end_dt, now_dt)[0]
        overdue_sum = "{:.2f}".format(overdue_period * 5)
        renew_start_dt = convert_dt_to_str(dt_format_display)
        renew_start_dt_db = convert_dt_to_str(dt_format_db)
        return (overdue_sum,
                "YES",
                renew_start_dt,
                start_date_system_msg,
                renew_start_dt_db,
                datetime.datetime.now()
                )
    else:
        renew_start_dt = convert_dt_to_str(dt_format_display, dt=end_dt)
        renew_start_dt_db = convert_dt_to_str(dt_format_db, dt=end_dt)
        return ("--",
                "NO",
                renew_start_dt,
                start_date_previous_sub_msg,
                renew_start_dt_db,
                end_dt
                )


#  converts true/false into yes/no in the customer report for the active subscription column.
#  It's called in the template
def sub_status_msg(status: bool):
    if status is True:
        return "YES"
    else:
        return "NO"


# used for customer report table. Returns -- instead empty record or return formatted dt
def skipped_dt(data):
    if data is not None:
        return convert_dt_to_str(dt_format_display,
                                 data
                                 )
    else:
        return "--"


# used for customer report table. Return -- for empty overdue or return overdue sum with added str 'lv'
def overdue_msg(overdue: str):
    if overdue is not None:
        return f"{overdue} lv"
    else:
        return "--"


def incorrect_plus_place(phone_to_check: str):
    return [i for i in phone_to_check[1:] if i == "+"]


def plus_not_first(phone_to_check: str):
    return phone_to_check[0] != "+"
