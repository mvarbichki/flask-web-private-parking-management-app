from flask import flash
import string
import cyrtranslit
import datetime

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
def blank_space_check(var):
    white_space_lst = [i for i in var.data if i == " "]
    return white_space_lst


# compare str to list for allowed symbols
def validate_check_from_lst(var_to_check, lst_to_compare):
    res_lst = [i for i in var_to_check if i not in lst_to_compare]
    return res_lst


def first_last_ele_check(var_to_check, ele):
    first_last_lst = [var_to_check.data[i] for i in (0, -1)]
    res = [i for i in first_last_lst if i == ele]
    return res


# creates a list of not occupied parking spots. It creates 60 parking spots and reverse the order
def free_parking_spots(db_lst: list):
    str_lst = [str(elem) for elem in db_lst]
    res_lst = []
    for i in range(1, 61):
        if str(i) not in str_lst:
            res_lst.append(str(i))
    return [x for x in res_lst[::-1]]


# calculate time differance between two dates
def calculate_days_diff(start_date, end_date):
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


def manual_str_char_swap_dt(str_dt):
    c_lst = list(str_dt)
    # swap list characters
    c_lst[0], c_lst[1], c_lst[2], c_lst[3], c_lst[4], c_lst[5], c_lst[6], c_lst[7], c_lst[8], c_lst[9] = \
        c_lst[8], c_lst[9], "/", c_lst[5], c_lst[6], "/", c_lst[0], c_lst[1], c_lst[2], c_lst[3]
    # convert list back to string
    res = "".join(c_lst)
    return res


def convert_str_to_dt(str_dt, dt_format):
    return datetime.datetime.strptime(str_dt, dt_format)


def validate_datetime_differance(start_dt, end_dt, days):
    # check if start date is equal or bigger then end date or time differance is less the 1 day
    if (start_dt >= end_dt) or (days < 1):
        return "Minimum subscription period is 24 hours"
    # check if subscription period is more than one year
    elif days > 366:
        return "Maximum subscription period is one year"


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
    if str_to_split == "":
        return ""
    else:
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


# checks for existing registration number or phone
def db_uniqueness_check(model, form_data: str, option: str):
    if option == "phone":
        return model.query.filter_by(phone=form_data).first()
    elif option == "reg_number":
        return model.query.filter_by(vehicle_registration_number=form_data).first()


# remove seconds and colon
def format_time(time):
    return ''.join(time.split())[:-3]


def formation_dt(date: str, time: str, db_format: str):
    date = manual_str_char_swap_dt(date)
    time = format_time(time)
    gather_str_dt = date + " " + time
    return convert_str_to_dt(gather_str_dt, db_format)


def sub_expiry_check(end_dt, now_dt):
    # checks for subscription overdue expiration. If so calculate extra fee. Also return different start dt,
    # and different start dt info
    if end_dt < now_dt:
        # if differance is less than 24h the day differance will become 1. Otherwise, will calculate the fee
        if calculate_days_diff(end_dt, now_dt)[0] == 0:
            overdue_period = 1
        else:
            overdue_period = calculate_days_diff(end_dt, now_dt)[0]
        return ("{:.2f}".format(overdue_period * 5), "YES", convert_dt_to_str(dt_format_display),
                "start date is taken automatically from the system", convert_dt_to_str(dt_format_db),
                datetime.datetime.now())
    else:
        return ("--", "NO", convert_dt_to_str(dt_format_display, dt=end_dt),
                "start date is the end date of the previous subscription", convert_dt_to_str(dt_format_db, dt=end_dt),
                end_dt)


# instead true/false return yes/no in the customer report for the active subscription column
def sub_status_msg(status):
    if status is True:
        return "YES"
    else:
        return "NO"


# used for customer report table. Returns -- instead empty record for skipped dt or return formatted dt
def skipped_dt(data):
    if data is not None:
        return convert_dt_to_str(dt_format_display,
                                 data
                                 )
    else:
        return "--"


# used for customer report table. Return -- for empty overdue or return overdue sum with added str 'lv'
def overdue_msg(overdue):
    if overdue is not None:
        return f"{overdue} lv"
    else:
        return "--"
