from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.fields import DateTimeLocalField
from wtforms.validators import Length, ValidationError, InputRequired
from parking.utilities import blank_space_check, validate_check_from_lst, num_plus_to_compare_lst, latin_letters, \
    cyrillic_letters, str_address_cyrillic_compare_lst, str_address_latin_compare_lst, str_reg_num_latin_compare_lst, \
    srt_reg_num_cyrillic_compare_lst, str_color_latin_dash_compare_lst, str_color_cyrillic_dash_compare_lst, \
    str_model_latin_compare_lst, str_model_cyrillic_compare_lst, first_last_ele_check, dt_format_db, dt_now, \
    calculate_days_diff, validate_datetime_differance
from parking.messages import blank_space_msg, invalid_phone_msg, invalid_code_phone_msg, invalid_first_name_msg, \
    invalid_last_name_msg, first_last_name_differance_msg, invalid_address_msg, address_name_differance_msg, \
    invalid_reg_number_msg, invalid_veh_type_msg, invalid_brand_msg, brand_type_differance_msg, invalid_model_msg, \
    model_type_differance_msg, invalid_color_msg, color_type_differance_msg, invalid_type_msg


class LoginForm(FlaskForm):
    username = StringField(label="Username: *",
                           validators=[InputRequired(), Length(max=20)]
                           )
    password = PasswordField(label="Password: *",
                             validators=[InputRequired(), Length(max=30)]
                             )
    button = SubmitField("Login")


class CustomersRegisterForm(FlaskForm):

    def validate_phone(self, phone_to_check):
        if phone_to_check.data == "":
            pass
        # checks of there is blank space
        elif blank_space_check(phone_to_check):
            raise ValidationError(blank_space_msg("the phone number"))
        # checks if phone number is valid by comparing it to numb list and checks if + is not at first place
        elif (validate_check_from_lst(phone_to_check.data, num_plus_to_compare_lst)) or \
                ([i for i in phone_to_check.data[1:] if i == "+"]):
            raise ValidationError(invalid_phone_msg)
        # checks if phone number begin is valid, must start with +
        elif phone_to_check.data[0] != "+":
            raise ValidationError(invalid_code_phone_msg)

    def validate_first_name(self, first_name_to_check):
        if blank_space_check(first_name_to_check):
            raise ValidationError(blank_space_msg("the first name"))
        # checks if the entry is only letters and if it mixes Latin and Cyrillic
        elif (validate_check_from_lst(first_name_to_check.data, latin_letters)) and \
                (validate_check_from_lst(first_name_to_check.data, cyrillic_letters)):
            raise ValidationError(invalid_first_name_msg)

    def validate_last_name(self, last_name_to_check):
        if blank_space_check(last_name_to_check):
            raise ValidationError(blank_space_msg("the last name"))
        elif (validate_check_from_lst(last_name_to_check.data, latin_letters)) and \
                (validate_check_from_lst(last_name_to_check.data, cyrillic_letters)):
            raise ValidationError(invalid_last_name_msg)
        # checks if the last name is different alphabet than the data
        elif (validate_check_from_lst(self.first_name.data, latin_letters) and
              validate_check_from_lst(last_name_to_check.data, cyrillic_letters)) or \
                (validate_check_from_lst(self.first_name.data, cyrillic_letters) and
                 validate_check_from_lst(last_name_to_check.data, latin_letters)):
            raise ValidationError(first_last_name_differance_msg)

    def validate_address(self, address_to_check):
        if address_to_check.data:
            if (validate_check_from_lst(address_to_check.data, str_address_latin_compare_lst)) and \
                    (validate_check_from_lst(address_to_check.data, str_address_cyrillic_compare_lst)):
                raise ValidationError(invalid_address_msg)
            elif (validate_check_from_lst(self.first_name.data, latin_letters) and
                  validate_check_from_lst(address_to_check.data, str_address_cyrillic_compare_lst)) or \
                    (validate_check_from_lst(self.first_name.data, cyrillic_letters) and
                     validate_check_from_lst(address_to_check.data, str_address_latin_compare_lst)):
                raise ValidationError(address_name_differance_msg)

    first_name = StringField(label="First name: *",
                             validators=[InputRequired(), Length(min=2, max=20)]
                             )
    last_name = StringField(label="Last name: *",
                            validators=[InputRequired(), Length(min=2, max=20)]
                            )
    # according to google the shortest phone number is 7 digits and longest 15. So min and max length are set
    # including + sign
    phone = StringField(label="Phone number: *",
                        validators=[InputRequired(), Length(min=8, max=16)]
                        )
    address = StringField(label="Address: ",
                          validators=[Length(max=100)]
                          )
    button = SubmitField(label="Continue")


# inheritance from customer registration class
class EditCustomerFrom(CustomersRegisterForm):
    pass


class DeleteForm(FlaskForm):

    def validate_deleting(self):
        pass

    button = SubmitField(label="Continue")


class VehiclesRegisterForm(FlaskForm):
    # reg number is not bound to the alphabet because it depends on the country where the vehicle is registered
    def validate_vehicle_registration_number(self, reg_number_to_check):
        if reg_number_to_check.data == "":
            pass
        elif blank_space_check(reg_number_to_check):
            raise ValidationError(blank_space_msg("the registration number"))
        # checks for allowed characters and symbols
        elif validate_check_from_lst(reg_number_to_check.data, str_reg_num_latin_compare_lst) and \
                validate_check_from_lst(reg_number_to_check.data, srt_reg_num_cyrillic_compare_lst) or \
                (first_last_ele_check(reg_number_to_check, "-")):
            raise ValidationError(invalid_reg_number_msg)

    def validate_vehicle_type(self, type_to_check):
        if blank_space_check(type_to_check):
            raise ValidationError(blank_space_msg("the vehicle type"))
        elif (validate_check_from_lst(type_to_check.data, latin_letters)) and \
                (validate_check_from_lst(type_to_check.data, cyrillic_letters)):
            raise ValidationError(invalid_veh_type_msg)

    def validate_brand(self, brand_to_check):
        if blank_space_check(brand_to_check):
            raise ValidationError(blank_space_msg("the vehicle brand"))
        elif (validate_check_from_lst(brand_to_check.data, latin_letters)) and \
                (validate_check_from_lst(brand_to_check.data, cyrillic_letters)):
            raise ValidationError(invalid_brand_msg)
        elif (validate_check_from_lst(self.vehicle_type.data, latin_letters) and
              validate_check_from_lst(brand_to_check.data, cyrillic_letters)) or \
                (validate_check_from_lst(self.vehicle_type.data, cyrillic_letters) and
                 validate_check_from_lst(brand_to_check.data, latin_letters)):
            raise ValidationError(brand_type_differance_msg)

    def validate_model(self, model_to_check):
        if blank_space_check(model_to_check):
            raise ValidationError(blank_space_msg("the vehicle model"))
        elif (validate_check_from_lst(model_to_check.data, str_model_latin_compare_lst)) and \
                (validate_check_from_lst(model_to_check.data, str_model_cyrillic_compare_lst)):
            raise ValidationError(invalid_model_msg)
        elif (validate_check_from_lst(self.vehicle_type.data, str_reg_num_latin_compare_lst) and
              validate_check_from_lst(model_to_check.data, str_model_cyrillic_compare_lst)) or \
                (validate_check_from_lst(self.vehicle_type.data, srt_reg_num_cyrillic_compare_lst) and
                 validate_check_from_lst(model_to_check.data, str_model_latin_compare_lst)):
            raise ValidationError(model_type_differance_msg)

    def validate_color(self, color_to_check):
        if blank_space_check(color_to_check):
            raise ValidationError(blank_space_msg("the vehicle color"))
        elif (validate_check_from_lst(color_to_check.data, str_color_latin_dash_compare_lst)) and \
                (validate_check_from_lst(color_to_check.data, str_color_cyrillic_dash_compare_lst)) or \
                (first_last_ele_check(color_to_check, "-")):
            raise ValidationError(invalid_color_msg)
        elif (validate_check_from_lst(self.vehicle_type.data, str_reg_num_latin_compare_lst) and
              validate_check_from_lst(color_to_check.data, str_color_cyrillic_dash_compare_lst)) or \
                (validate_check_from_lst(self.vehicle_type.data, srt_reg_num_cyrillic_compare_lst) and
                 validate_check_from_lst(color_to_check.data, str_color_latin_dash_compare_lst)):
            raise ValidationError(color_type_differance_msg)

    vehicle_registration_number = StringField(label="Vehicle registration number: *",
                                              validators=[InputRequired(), Length(min=7, max=20)]
                                              )
    vehicle_type = StringField(label="Vehicle type: *",
                               validators=[InputRequired(), Length(min=3, max=15)]
                               )
    brand = StringField(label="Vehicle brand: *",
                        validators=[InputRequired(), Length(min=3, max=20)]
                        )
    model = StringField(label="Vehicle model: *",
                        validators=[InputRequired(), Length(min=1, max=30)]
                        )
    color = StringField(label="Vehicle color: *",
                        validators=[InputRequired(), Length(min=3, max=25)]
                        )
    button = SubmitField(label="Continue")


class EditVehicleFrom(VehiclesRegisterForm):

    def validate_vehicle_type(self, type_to_check):
        if blank_space_check(type_to_check):
            raise ValidationError(blank_space_msg("the vehicle type"))
        elif (validate_check_from_lst(type_to_check.data, latin_letters)) and \
                (validate_check_from_lst(type_to_check.data, cyrillic_letters)):
            raise ValidationError(invalid_type_msg)


class AddSubscriptionForm(FlaskForm):
    days = ""

    def validate_end_date(self, end_date_to_check):
        # takes datetime and make sec/microsecond 0. This is needed because end_date_to_check return sec/microsecond 0
        # it makes comparing between the dates correct
        dt_now_null_sec = dt_now().replace(second=0, microsecond=0)
        # differance in days between start dt and end dt
        self.days = calculate_days_diff(dt_now_null_sec, end_date_to_check.data)[0]
        # dt check for min and max subscription period
        dt_check = validate_datetime_differance(dt_now_null_sec,
                                                end_date_to_check.data,
                                                self.days
                                                )
        if dt_check:
            raise ValidationError(dt_check)

    # returns the days differance
    def get_days(self):
        return int(self.days)

    end_date = DateTimeLocalField(label="Select end date and time: *",
                                  format=dt_format_db,
                                  validators=[InputRequired()]
                                  )
    button = SubmitField(label="Continue")


class SelectEditForm(FlaskForm):

    def validate_editing(self):
        pass

    button = SubmitField(label="Continue")


class EditSubscriptionForm(FlaskForm):
    end_date = DateTimeLocalField(label="Select new end date and time: *",
                                  format=dt_format_db,
                                  validators=[InputRequired()]
                                  )
    button = SubmitField(label="Continue")
