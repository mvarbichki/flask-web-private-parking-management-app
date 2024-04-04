from flask import flash


# display error messages
def display_error_messages(form):
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(message=f"{err_msg[0]}",
                  category="info"
                  )


# messages
successful_record_msg = "The record was added successfully"
failed_record_msg = "Adding the record failed. Try again"
no_changes_msg = "No changes to the record. You must change at least one field to continue"
update_record_msg = "The record was changed successfully"
failed_update_record_msg = "Changing the record failed. Try again"
successful_del_record_msg = "The record was deleted successfully"
failed_del_record_msg = "Deleting the record failed. Try again"
invalid_phone_msg = "The phone number is invalid. Only numbers and plus symbol are allowed"
invalid_code_phone_msg = "The phone number must begin with country code ex. +359, +90, +30 etc"
invalid_first_name_msg = ("The first name is invalid. Only letters are allowed.A mix between Latin and cyrillic "
                          "letters is not allowed")
invalid_last_name_msg = ("The last name is invalid. Only letters are allowed. A mix between Latin and cyrillic letters "
                         "is not allowed")
first_last_name_differance_msg = ("The first name and the last name are not the same type.Use latin only or cyrillic "
                                  "only for the customer's fields.")
invalid_address_msg = ("The address is invalid. Only letters, numbers, apostrophe, dash, dot, comma are allowed. A mix "
                       "between latin and cyrillic letters is not allowed")
address_first_name_differance_msg = (
    "The address and customer name are not the same type. Use latin only or cyrillic only "
    "for the customer's fields")
invalid_reg_number_msg = ("The vehicle registration number is invalid. Only letters, numbers and dash symbol (must not "
                          "be first or last) are allowed. A mix between latin and cyrillic letters is not allowed")
invalid_veh_type_msg = ("The vehicle type is invalid. Only letters are allowed. A mix between latin and cyrillic "
                        "letters is not allowed")
invalid_brand_msg = ("The vehicle brand is invalid. Only letters are allowed.A mix between latin and cyrillic letters "
                     "is not allowed")
brand_type_differance_msg = ("The vehicle brand and vehicle type are not the same type. Use latin only or cyrillic "
                             "only for the vehicle's fields")
invalid_model_msg = ("The vehicle model is invalid. Only letters are allowed. A mix between latin and cyrillic letters "
                     "is not allowed")
model_type_differance_msg = ("The vehicle model and vehicle type are not the same type. Use latin only or cyrillic "
                             "only for the vehicle's fields")
invalid_color_msg = ("The vehicle color is invalid. Only letters and dash symbol (must not be first or last) are "
                     "allowed. A mix between latin and cyrillic letters is not allowed")
color_type_differance_msg = ("The vehicle color and vehicle type are not the same type. Use latin only or cyrillic "
                             "only for the vehicle's fields")
invalid_type_msg = ("The vehicle type is invalid. Only letters are allowed. A mix between latin and cyrillic letters "
                    "is not allowed")
min_sub_period_msg = "Minimum subscription period is 24 hours"
max_sub_period_msg = "Maximum subscription period is one year"
start_date_system_msg = "start date is taken automatically from the system"
start_date_previous_sub_msg = "start date is the end date of the previous subscription"
wrong_user_credential = "Wrong user or password"
user_logged_out = "Logged out"


def record_exist_msg(record: str):
    return f"The {record} already exists"


def letters_mix_msg(obj_one: str, obj_two: str):
    return f"{obj_one} and {obj_two} are different alphabet. Use only latin or cyrillic {obj_one}"


def alphabet_db_mix_msg(obj: str):
    return f"{obj} is a different alphabet from the DB record. Use the alphabet type which will match"


def fee_refund_msg(obj: float):
    return f"Refund of remaining subscription time: {'{:.2f}'.format(obj)} lv"


def full_fee_msg(obj: str):
    return f"Full subscription fee: {obj} lv"


def overdue_fee_msg(obj: str):
    return f"Overdue subscription fees: {obj} lv"


def login_msg(obj: str):
    return f"{obj} logged in"


def blank_space_msg(obj: str):
    return f"Remove any blank space from {obj}"
