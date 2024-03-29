# messages
successful_record_msg = "The record was added successfully"
failed_record_msg = "Adding the record failed. Try again"
no_changes_msg = "No changes to the record. You must change at least one field to continue"
update_record_msg = "The record was changed successfully"
failed_update_record_msg = "Changing the record failed. Try again"
successful_del_record_msg = "The record was deleted successfully"
failed_del_record_msg = "Deleting the record failed. Try again"


def record_exist_msg(record):
    return f"The {record} already exists"


def letters_mix_msg(obj_one, obj_two):
    return f"{obj_one} and {obj_two} are different alphabet. Use only latin or cyrillic {obj_one}"


def alphabet_db_mix_msg(obj):
    return f"{obj} is a different alphabet from the DB record. Use the alphabet type which will match"


def fee_refund(obj):
    return f"Refund of remaining subscription time: {'{:.2f}'.format(obj)} lv"


def full_fee(obj):
    return f"Full subscription fee: {obj} lv"


def overdue_fee(obj):
    return f"Overdue subscription fees: {obj} lv"


def login_msg(obj):
    return f"{obj} logged in"
