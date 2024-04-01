from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.fields import DateTimeLocalField
from wtforms.validators import Length, ValidationError, InputRequired
from parking.utilities import blank_space_check, validate_check_from_lst, num_plus_to_compare_lst, latin_letters, \
    cyrillic_letters, str_address_cyrillic_compare_lst, str_address_latin_compare_lst, str_reg_num_latin_compare_lst, \
    srt_reg_num_cyrillic_compare_lst, str_color_latin_dash_compare_lst, str_color_cyrillic_dash_compare_lst, \
    str_model_latin_compare_lst, str_model_cyrillic_compare_lst, first_last_ele_check, dt_format_db, dt_now, \
    calculate_days_diff, validate_datetime_differance, incorrect_plus_place, plus_not_first
from parking.messages import blank_space_msg, invalid_phone_msg, invalid_code_phone_msg, invalid_first_name_msg, \
    invalid_last_name_msg, first_last_name_differance_msg, invalid_address_msg, address_first_name_differance_msg, \
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
        phone_is_empty_str = phone_to_check.data == ""
        blank_space_in_phone = blank_space_check(phone_to_check)
        invalid_phone = validate_check_from_lst(phone_to_check.data, num_plus_to_compare_lst)
        invalid_plus_symbol_place = incorrect_plus_place(phone_to_check.data)
        invalid_phone_first_symbol = plus_not_first(phone_to_check.data)
        if phone_is_empty_str:
            pass
        # checks of there is blank space
        elif blank_space_in_phone:
            raise ValidationError(blank_space_msg("the phone number"))
        # checks if phone number is valid by comparing it to numb list and checks if + is not at first place
        elif invalid_phone or invalid_plus_symbol_place:
            raise ValidationError(invalid_phone_msg)
        # checks if phone number begin is valid, must start with +
        elif invalid_phone_first_symbol:
            raise ValidationError(invalid_code_phone_msg)

    def validate_first_name(self, first_name_to_check):
        blank_space_in_first_name = blank_space_check(first_name_to_check)
        invalid_first_name_latin = validate_check_from_lst(first_name_to_check.data, latin_letters)
        invalid_first_name_cyrillic = validate_check_from_lst(first_name_to_check.data, cyrillic_letters)
        if blank_space_in_first_name:
            raise ValidationError(blank_space_msg("the first name"))
        # checks if the entry is only letters and if it mixes Latin and Cyrillic
        elif invalid_first_name_latin and invalid_first_name_cyrillic:
            raise ValidationError(invalid_first_name_msg)

    def validate_last_name(self, last_name_to_check):
        blank_space_in_last_name = blank_space_check(last_name_to_check)
        invalid_last_name_latin = validate_check_from_lst(last_name_to_check.data, latin_letters)
        invalid_last_name_cyrillic = validate_check_from_lst(last_name_to_check.data, cyrillic_letters)
        invalid_first_name_latin = validate_check_from_lst(self.first_name.data, latin_letters)
        invalid_first_name_cyrillic = validate_check_from_lst(self.first_name.data, cyrillic_letters)
        if blank_space_in_last_name:
            raise ValidationError(blank_space_msg("the last name"))
        elif invalid_last_name_latin and invalid_last_name_cyrillic:
            raise ValidationError(invalid_last_name_msg)
        # checks if the last name is different alphabet than the data
        elif (invalid_first_name_latin and invalid_last_name_cyrillic) or \
                (invalid_first_name_cyrillic and invalid_last_name_latin):
            raise ValidationError(first_last_name_differance_msg)

    def validate_address(self, address_to_check):
        address = address_to_check.data
        invalid_address_latin = validate_check_from_lst(address, str_address_latin_compare_lst)
        invalid_address_cyrillic = validate_check_from_lst(address, str_address_cyrillic_compare_lst)
        invalid_first_name_latin = validate_check_from_lst(self.first_name.data, latin_letters)
        invalid_first_name_cyrillic = validate_check_from_lst(self.first_name.data, cyrillic_letters)
        if address:
            if invalid_address_latin and invalid_address_cyrillic:
                raise ValidationError(invalid_address_msg)
            elif (invalid_first_name_latin and invalid_address_cyrillic) or \
                    (invalid_first_name_cyrillic and invalid_address_latin):
                raise ValidationError(address_first_name_differance_msg)

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
        reg_number_is_empty_str = reg_number_to_check.data == ""
        blank_space_in_reg_num = blank_space_check(reg_number_to_check)
        invalid_reg_num_cyrillic = validate_check_from_lst(reg_number_to_check.data, srt_reg_num_cyrillic_compare_lst)
        invalid_reg_num_latin = validate_check_from_lst(reg_number_to_check.data, str_reg_num_latin_compare_lst)
        reg_first_or_last_element_is_dash = first_last_ele_check(reg_number_to_check, "-")
        if reg_number_is_empty_str:
            pass
        elif blank_space_in_reg_num:
            raise ValidationError(blank_space_msg("the registration number"))
        # checks for allowed characters and symbols
        elif (invalid_reg_num_latin and invalid_reg_num_cyrillic) or reg_first_or_last_element_is_dash:
            raise ValidationError(invalid_reg_number_msg)

    def validate_vehicle_type(self, type_to_check):
        blank_space_in_type = blank_space_check(type_to_check)
        invalid_type_cyrillic = validate_check_from_lst(type_to_check.data, cyrillic_letters)
        invalid_type_latin = validate_check_from_lst(type_to_check.data, latin_letters)
        if blank_space_in_type:
            raise ValidationError(blank_space_msg("the vehicle type"))
        elif invalid_type_latin and invalid_type_cyrillic:
            raise ValidationError(invalid_veh_type_msg)

    def validate_brand(self, brand_to_check):
        blank_space_in_brand = blank_space_check(brand_to_check)
        invalid_brand_cyrillic = validate_check_from_lst(brand_to_check.data, cyrillic_letters)
        invalid_brand_latin = validate_check_from_lst(brand_to_check.data, latin_letters)
        invalid_type_latin = validate_check_from_lst(self.vehicle_type.data, latin_letters)
        invalid_type_cyrillic = validate_check_from_lst(self.vehicle_type.data, cyrillic_letters)
        if blank_space_in_brand:
            raise ValidationError(blank_space_msg("the vehicle brand"))
        elif invalid_brand_latin and invalid_brand_cyrillic:
            raise ValidationError(invalid_brand_msg)
        elif (invalid_type_latin and invalid_brand_cyrillic) or (invalid_type_cyrillic and invalid_brand_latin):
            raise ValidationError(brand_type_differance_msg)

    def validate_model(self, model_to_check):
        blank_space_in_model = blank_space_check(model_to_check)
        invalid_model_latin = validate_check_from_lst(model_to_check.data, str_model_latin_compare_lst)
        invalid_model_cyrillic = validate_check_from_lst(model_to_check.data, str_model_cyrillic_compare_lst)
        invalid_type_latin = validate_check_from_lst(self.vehicle_type.data, str_reg_num_latin_compare_lst)
        invalid_type_cyrillic = validate_check_from_lst(self.vehicle_type.data, srt_reg_num_cyrillic_compare_lst)
        if blank_space_in_model:
            raise ValidationError(blank_space_msg("the vehicle model"))
        elif invalid_model_latin and invalid_model_cyrillic:
            raise ValidationError(invalid_model_msg)
        elif (invalid_type_latin and invalid_model_cyrillic) or (invalid_type_cyrillic and invalid_model_latin):
            raise ValidationError(model_type_differance_msg)

    def validate_color(self, color_to_check):
        blank_space_in_color = blank_space_check(color_to_check)
        invalid_color_latin = validate_check_from_lst(color_to_check.data, str_color_latin_dash_compare_lst)
        invalid_color_cyrillic = validate_check_from_lst(color_to_check.data, str_color_cyrillic_dash_compare_lst)
        color_first_or_last_element_is_dash = first_last_ele_check(color_to_check, "-")
        invalid_type_latin = validate_check_from_lst(self.vehicle_type.data, str_reg_num_latin_compare_lst)
        invalid_type_cyrillic = validate_check_from_lst(self.vehicle_type.data, srt_reg_num_cyrillic_compare_lst)
        if blank_space_in_color:
            raise ValidationError(blank_space_msg("the vehicle color"))
        elif (invalid_color_latin and invalid_color_cyrillic) or color_first_or_last_element_is_dash:
            raise ValidationError(invalid_color_msg)
        elif (invalid_type_latin and invalid_color_cyrillic) or (invalid_type_cyrillic and invalid_color_latin):
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
        blank_space_in_type = blank_space_check(type_to_check)
        invalid_type_cyrillic = validate_check_from_lst(type_to_check.data, cyrillic_letters)
        invalid_type_latin = validate_check_from_lst(type_to_check.data, latin_letters)
        if blank_space_in_type:
            raise ValidationError(blank_space_msg("the vehicle type"))
        elif invalid_type_latin and invalid_type_cyrillic:
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
        sub_dt_is_invalid = validate_datetime_differance(dt_now_null_sec,
                                                         end_date_to_check.data,
                                                         self.days
                                                         )
        if sub_dt_is_invalid:
            raise ValidationError(sub_dt_is_invalid)

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
