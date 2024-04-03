import decimal
import importlib
from parking import app, db
from flask import render_template, redirect, url_for, request, flash, session
from parking.models import Customers, Vehicles, Subscriptions, Users
from parking.forms import CustomersRegisterForm, VehiclesRegisterForm, EditCustomerFrom, DeleteForm, EditVehicleFrom, \
    AddSubscriptionForm, SelectEditForm, EditSubscriptionForm, LoginForm
from parking.utilities import free_parking_spots, convert_dt_to_str, dt_format_display, \
    dt_format_db, calculate_days_diff, validate_datetime_differance, new_entry_validation, str_split_pick, \
    recalculate_sub_tax, validate_check_from_lst, latin_letters, cyrillic_letters, day_ahead, \
    dt_now, compose_dt, sub_expiry_check, convert_str_to_dt, skipped_dt, db_phone_uniqueness_check, \
    db_reg_uniqueness_check, if_end_dt_bigger
from parking.messages import successful_record_msg, failed_record_msg, no_changes_msg, record_exist_msg, \
    update_record_msg, successful_del_record_msg, failed_del_record_msg, failed_update_record_msg, \
    alphabet_db_mix_msg, fee_refund_msg, full_fee_msg, overdue_fee_msg, login_msg, wrong_user_credential, \
    user_logged_out, display_error_messages
from flask_login import login_user, login_required, logout_user


# TODO
# create log to write errs


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # get a session if the user exist
        attempted_user = Users.query.filter_by(username=form.username.data).first()
        # validate if user exist in our db
        if attempted_user:
            # validate user password
            if attempted_user.password == form.password.data:
                # log in the user
                login_user(user=attempted_user)
                flash(message=login_msg(attempted_user.username),
                      category="success"
                      )
                return redirect(location=url_for("home_page"))
        flash(message=wrong_user_credential,
              category="info"
              )
    display_error_messages(form=form)
    return render_template(template_name_or_list="login.html",
                           form=form
                           )


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash(message=user_logged_out,
          category="info"
          )
    return redirect(location=url_for("home_page"))


@app.route("/")
@app.route("/home")
@login_required
def home_page():
    return render_template(template_name_or_list="home.html")


@app.route("/subscriptions")
@login_required
def subscriptions_page():
    return render_template(template_name_or_list="subscriptions.html")


@app.route("/add_subscription", methods=["GET", "POST"])
@login_required
def add_subscription():
    # create list of not subscribed vehicles
    not_subscribed_vehicles_lst = (db.session.query(
        Vehicles.vehicle_id,
        Vehicles.vehicle_registration_number,
        Customers.first_name,
        Customers.last_name,
        Customers.phone
    ).join(Vehicles,
           Customers.customer_id == Vehicles.customer_id)
                                   ).filter(Vehicles.is_subscribed.is_(False)).all()

    # gets a list of all free parking spots based on active subscription
    free_spots_list = free_parking_spots(
        db_list=Subscriptions.query.join(Vehicles,
                                         Subscriptions.vehicle_id == Vehicles.vehicle_id
                                         ).where(Subscriptions.subscription_status == "ACTIVE")
    )
    current_dt = convert_dt_to_str(dt_format=dt_format_display)
    form = AddSubscriptionForm()

    if form.validate_on_submit():
        # gets dt to display on the page
        session["sub_start_date_display"] = current_dt
        # gets dt to write in the db
        session["add_start_date"] = convert_dt_to_str(dt_format=dt_format_db)
        # gets desire end dt from the form field
        session["add_end_date"] = form.end_date.data
        # gets parking spot choice from html select
        session["add_parking_spot_number"] = request.form.get("selectSpotSubs")
        # gets vehicle-customer info from html select
        vehicle_customer_information = request.form.get("selectVehicleSubs")
        # gets different info from html select and keeps it in order to be used in different route
        session["add_vehicle_id"] = str_split_pick(str_to_split=vehicle_customer_information,
                                                   index=0,
                                                   return_int=True
                                                   )
        session["sub_first_name"] = str_split_pick(str_to_split=vehicle_customer_information,
                                                   index=8
                                                   )
        session["sub_last_name"] = str_split_pick(str_to_split=vehicle_customer_information,
                                                  index=9
                                                  )
        session["sub_reg_number"] = str_split_pick(str_to_split=vehicle_customer_information,
                                                   index=5
                                                   )
        # gets days differance between star dt and end dt from the form def
        days_subscription = form.get_days()
        # calculate the sub tax (5lv per 1 day) and format the result
        tax = "{:.2f}".format(days_subscription * 5)
        session["add_sub_tax"] = tax
        # redirects to different url
        return redirect(location=url_for("confirmation_subscription"))
    # displays messages
    display_error_messages(form=form)
    return render_template(template_name_or_list="add_subscription.html",
                           form=form,
                           vehicle_customer_lst=not_subscribed_vehicles_lst,
                           free_spots_list=free_spots_list,
                           current_dt=current_dt
                           )


@app.route("/confirmation_subscription")
@login_required
def confirmation_subscription():
    # gets the information from add subscription to display it on the confirmation subscription page
    start_date = session.get("add_start_date")
    parking_spot_number = session.get("add_parking_spot_number")
    vehicle_id = session.get("add_vehicle_id")
    sub_tax = session.get("add_sub_tax")
    # converts end dt to str in order to display it on the confirmation page
    end_date = convert_dt_to_str(dt_format=dt_format_display,
                                 dt=session.get("add_end_date")
                                 )
    # creates subscription session which could be added to the db
    session["subscription_to_add"] = Subscriptions(parking_spot_number=parking_spot_number,
                                                   start_date=start_date,
                                                   end_date=session.get("add_end_date"),
                                                   tax=sub_tax,
                                                   subscription_status="ACTIVE",
                                                   vehicle_id=vehicle_id
                                                   )
    return render_template(template_name_or_list="confirmation_subscription.html",
                           start_date=start_date,
                           end_date=end_date,
                           parking_spot_number=parking_spot_number,
                           vehicle_id=vehicle_id,
                           reg_number=session.get("sub_reg_number"),
                           tax=sub_tax,
                           first_name=session.get("sub_first_name"),
                           last_name=session.get("sub_last_name"),
                           st_display=session.get("sub_start_date_display")
                           )


@app.route("/subscription_yes_but_action")
@login_required
def subscription_yes_but_action():
    # handles errors during writing the record in the db
    try:
        vehicle_to_update = db.session.get(Vehicles,
                                           session.get("add_vehicle_id")
                                           )
        # marks a vehicle as subscribed
        vehicle_to_update.is_subscribed = True
        db.session.add(vehicle_to_update)
        db.session.add(session.get("subscription_to_add"))
        db.session.commit()
        flash(message=successful_record_msg,
              category="success"
              )
    except Exception as err:
        # TODO write in log file errs
        print(err)
        db.session.rollback()
        flash(message=failed_record_msg,
              category="danger"
              )
    finally:
        db.session.close()
        return redirect(location=url_for("subscriptions_page"))


@app.route("/select_subscription_edit", methods=["GET", "POST"])
@login_required
def select_subscription_edit():
    # creates a list that shows only subscribed vehicles which subscription not expire in the next 24 hours
    sub_lst = (db.session.query(
        Subscriptions.subscription_id,
        Customers.customer_id,
        Customers.first_name,
        Customers.last_name,
        Vehicles.vehicle_registration_number,
        Subscriptions.start_date,
        Subscriptions.end_date,
        Subscriptions.parking_spot_number,
        Subscriptions.tax,
        Vehicles.vehicle_id
    ).join(Vehicles,
           Customers.customer_id == Vehicles.customer_id
           ).join(Subscriptions,
                  Vehicles.vehicle_id == Subscriptions.vehicle_id)
               ).filter(Vehicles.is_subscribed.is_(True),
                        Subscriptions.end_date > day_ahead(),
                        Subscriptions.subscription_status == "ACTIVE").all()

    form = SelectEditForm()

    if form.validate_on_submit():
        # gets desired sub info from select_subscription_edit.html as a single str
        subscription_information = request.form.get("selectSubsEdit")
        # extracts every needed element from the subscription_information by splitting it
        session["sub_parking_id"] = str_split_pick(str_to_split=subscription_information,
                                                   index=0,
                                                   return_int=True
                                                   )
        session["sub_vehicle_plate_num"] = str_split_pick(str_to_split=subscription_information,
                                                          index=8
                                                          )
        session["tax_edit"] = str_split_pick(str_to_split=subscription_information,
                                             index=23
                                             )
        session["start_date_edit"] = str_split_pick(str_to_split=subscription_information,
                                                    index=15
                                                    )
        session["start_time_edit"] = str_split_pick(str_to_split=subscription_information,
                                                    index=16
                                                    )
        session["sub_customer_id"] = str_split_pick(str_to_split=subscription_information,
                                                    index=28
                                                    )
        session["select_sub_spot"] = str_split_pick(str_to_split=subscription_information,
                                                    index=12
                                                    )
        session["select_sub_first_name"] = str_split_pick(str_to_split=subscription_information,
                                                          index=3
                                                          )
        session["select_sub_last_name"] = str_split_pick(str_to_split=subscription_information,
                                                         index=4
                                                         )
        session["end_date_edit"] = str_split_pick(str_to_split=subscription_information,
                                                  index=19
                                                  )
        session["end_time_edit"] = str_split_pick(str_to_split=subscription_information,
                                                  index=20
                                                  )
        session["sub_current_vehicle_id"] = str_split_pick(str_to_split=subscription_information,
                                                           index=32
                                                           )
        session["select_sub_edit_end_dt"] = convert_str_to_dt(str_dt=session.get("end_date_edit") + " " +
                                                                     session.get("end_time_edit"),
                                                              dt_format=dt_format_display
                                                              )
        return redirect(location=url_for("edit_subscription_option"))

    display_error_messages(form=form)
    return render_template(template_name_or_list="select_subscription_edit.html",
                           form=form,
                           vehicle_sub_lst=sub_lst,
                           imprt=importlib.import_module  # imports custom format dt im the html
                           )


@app.route("/edit_subscription_option")
@login_required
def edit_subscription_option():
    return render_template(template_name_or_list="edit_subscription_option.html")


@app.route("/confirmation_edit_cancel_subscription")
@login_required
def confirmation_edit_cancel_subscription():
    # gets selected subscription end date for calculation porous
    end_dt = session.get("select_sub_edit_end_dt")
    tax_to_refund_msg = ""
    # calculates if the subscription is canceled before end dt and some part of the tax has to be refund
    is_end_dt_bigger = if_end_dt_bigger(end_dt=end_dt)

    if is_end_dt_bigger:
        dt_difference_below_a_day = calculate_days_diff(start_date=end_dt, end_date=dt_now())[0] == 0
        if dt_difference_below_a_day:
            days = 1
        else:
            days = calculate_days_diff(start_date=end_dt, end_date=dt_now())[0]
        tax_to_refund = float(days * 5)
        tax_to_refund_msg = fee_refund_msg(obj=tax_to_refund)
    else:
        tax_to_refund = ""

    session["tax_to_refund"] = tax_to_refund
    return render_template(template_name_or_list="confirmation_edit_cancel_subscription.html",
                           first_name=session.get("select_sub_first_name"),
                           last_name=session.get("select_sub_last_name"),
                           reg_number=session.get("sub_vehicle_plate_num"),
                           parking_spot=session.get("select_sub_spot"),
                           full_sub_fee=full_fee_msg(session.get("tax_edit")),
                           fee_refund=tax_to_refund_msg
                           )


@app.route("/cancel_edit_yes_but_action")
@login_required
def cancel_edit_yes_but_action():
    try:
        # gets db sessions for subscriptions and vehicles in order to update teh records
        subscription_to_update = db.session.get(Subscriptions,
                                                session.get("sub_parking_id")
                                                )
        vehicle_to_update = db.session.get(Vehicles,
                                           session.get("sub_current_vehicle_id")
                                           )
        tax_to_refund = session.get("tax_to_refund")
        if tax_to_refund != "":
            tax_above_five_lv = int(tax_to_refund) != 5
            # calculates refund if subscription is above 5 lv. Skips one-day subs
            if tax_above_five_lv:
                if subscription_to_update.tax > tax_to_refund:
                    subscription_to_update.tax -= decimal.Decimal(tax_to_refund)
                else:
                    subscription_to_update.tax = decimal.Decimal(tax_to_refund) - subscription_to_update.tax
        # Does not allow the start date to be greater than the end date. This happened if renew the sub and cancel
        # it in the same day
        is_start_dt_greater = if_end_dt_bigger(end_dt=subscription_to_update.start_date)
        if is_start_dt_greater:
            subscription_to_update.start_date = dt_now()

        # updates subscriptions and vehicles records
        subscription_to_update.end_date = dt_now()
        subscription_to_update.subscription_status = "CANCELED"
        vehicle_to_update.is_subscribed = False
        db.session.commit()
        flash(message=successful_record_msg,
              category="success"
              )
    except Exception as err:
        print(err)
        # TODO write in log file errs
        db.session.rollback()
        flash(message=failed_record_msg,
              category="danger"
              )
    finally:
        db.session.close()
        return redirect(location=url_for("subscriptions_page"))


@app.route("/edit_subscription", methods=["GET", "POST"])
@login_required
def edit_subscription():
    # gets all the needed data via sessions from select_subscription_edit route
    vehicle_plate_num = session.get("sub_vehicle_plate_num")
    parking_spot = session.get("select_sub_spot")
    start_date = session.get("start_date_edit")
    start_time = session.get("start_time_edit")
    # gets all vehicle for given customers that are not subscribed yet. Allows to swap customer vehicles for a given sub
    vehicle_customer_lst = (db.session.query(
        Vehicles.vehicle_id,
        Vehicles.vehicle_registration_number,
        Customers.first_name,
        Customers.last_name,
        Customers.customer_id,
        Customers.phone
    ).join(Vehicles,
           Customers.customer_id == Vehicles.customer_id)
                            ).filter(Vehicles.is_subscribed.is_(False),
                                     Customers.customer_id == session.get("sub_customer_id")).all()
    # gets list of the not occupied parking spots
    free_spots_list = free_parking_spots(
        db_list=Subscriptions.query.join(Vehicles,
                                         Subscriptions.vehicle_id == Vehicles.vehicle_id
                                         ).where(Subscriptions.subscription_status == "ACTIVE")
    )
    # gets subscription session by id
    subscription = Subscriptions.query.get(session.get("sub_parking_id"))
    # populates edit form with selected sub info
    form = EditSubscriptionForm(obj=subscription)

    start_dt = convert_str_to_dt(str_dt=start_date + " " + start_time,
                                 dt_format=dt_format_display
                                 )
    current_end_dt = convert_str_to_dt(str_dt=session.get("end_date_edit") + " " + session.get("end_time_edit"),
                                       dt_format=dt_format_display
                                       )
    # desire new end dt from the form field
    new_end_dt = form.end_date.data
    # days differance between start dt and new end dt
    days = calculate_days_diff(start_date=start_dt, end_date=new_end_dt)[0]
    # dt min max validation
    dt_is_invalid = validate_datetime_differance(start_dt=dt_now(),
                                                 end_dt=new_end_dt,
                                                 days=days
                                                 )
    if form.validate_on_submit():
        # new vehicle id
        new_vehicle_id = str_split_pick(str_to_split=request.form.get("selectVehicleSubs"),
                                        index=0,
                                        return_int=True
                                        )
        # validated the new subscription choices
        updated_vehicle, vehicle_not_changed = new_entry_validation(
            current_record=session.get("sub_current_vehicle_id"),
            new_entry=new_vehicle_id
        )
        # new parking spot
        new_spot = request.form.get("selectSpotSubs")
        updated_spot, spot_not_changed = new_entry_validation(current_record=parking_spot,
                                                              new_entry=new_spot
                                                              )
        updated_sub_end_dt = calculate_days_diff(start_date=current_end_dt, end_date=new_end_dt)[0]
        sub_period_not_changed = updated_sub_end_dt == 0
        # checks for correct dt different
        if dt_is_invalid:
            flash(message=dt_is_invalid,
                  category="info"
                  )
        # prevents continuing if the user does not make any changes
        elif vehicle_not_changed and spot_not_changed and sub_period_not_changed:
            flash(message=no_changes_msg,
                  category="info"
                  )
        else:
            # keeps new entries in sessions
            session["the_new_vehicle_reg_numb"] = new_entry_validation(
                current_record=vehicle_plate_num,
                new_entry=str_split_pick(str_to_split=request.form.get("selectVehicleSubs"),
                                         index=4
                                         )
            )
            session["the_new_vehicle_id"] = (updated_vehicle, vehicle_not_changed)
            session["the_new_spot"] = (updated_spot, spot_not_changed)
            session["the_new_days_diff"] = updated_sub_end_dt
            # used for tax calculation if end dt is changing
            session["is_negative"] = calculate_days_diff(start_date=current_end_dt, end_date=new_end_dt)[1]
            session["the_new_end_dt"] = convert_dt_to_str(dt_format=dt_format_display,
                                                          dt=new_end_dt
                                                          )
            session["the_new_end_dt_db"] = new_end_dt
            return redirect(location=url_for("confirmation_edit_subscription"))

    display_error_messages(form=form)
    return render_template(template_name_or_list="edit_subscription.html",
                           form=form,
                           vehicle_plate_num=vehicle_plate_num,
                           start_date=start_date,
                           start_time=start_time,
                           vehicle_customer_lst=vehicle_customer_lst,
                           free_spots_list=free_spots_list,
                           parking_spot=parking_spot,
                           first_name=session.get("select_sub_first_name"),
                           last_name=session.get("select_sub_last_name")
                           )


@app.route("/confirmation_edit_subscription")
@login_required
def confirmation_edit_subscription():
    old_tax = session.get("tax_edit")
    # calculates the new sub fee, if there is reduction or increasing of sub period and the differance in
    # lv in both cases
    new_sub_tax, diff_action, diff_in_lv = recalculate_sub_tax(old_tax=float(old_tax),
                                                               dt_change=int(session.get("the_new_days_diff")),
                                                               is_negative=session.get("is_negative")
                                                               )
    session["new_sub_tax"] = new_sub_tax
    return render_template(template_name_or_list="confirmation_edit_subscription.html",
                           reg_number=session.get("the_new_vehicle_reg_numb")[0],
                           parking_spot_number=session.get("the_new_spot")[0],
                           end_date=session.get("the_new_end_dt"),
                           new_sub_tax=new_sub_tax,
                           diff_action=diff_action,
                           diff_in_lv=diff_in_lv,
                           old_tax=old_tax
                           )


@app.route("/edit_sub_yes_but_action")
@login_required
def edit_sub_yes_but_action():
    try:
        subscription_to_update = db.session.get(Subscriptions,
                                                session.get("sub_parking_id")
                                                )
        vehicle_id, vehicle_id_not_changed = session.get("the_new_vehicle_id")
        parking_spot, spot_not_changed = session.get("the_new_spot")
        sub_period_not_changed = session.get("the_new_days_diff") == 0
        # skips the db record if given field not changed. Otherwise, records the new entry
        if vehicle_id_not_changed:
            pass
        else:
            subscription_to_update.vehicle_id = int(vehicle_id)
            replacement_vehicle_to_update = db.session.get(Vehicles,
                                                           session.get("sub_current_vehicle_id")
                                                           )
            selected_vehicle_to_update = db.session.get(Vehicles,
                                                        vehicle_id
                                                        )
            # makes teh replaced vehicle unsubscribed and subscribe the selected one
            replacement_vehicle_to_update.is_subscribed = False
            selected_vehicle_to_update.is_subscribed = True

        if spot_not_changed:
            pass
        else:
            subscription_to_update.parking_spot_number = parking_spot

        if sub_period_not_changed:
            pass
        else:
            # if there is datetime differance it records both new sub tax and new end dt
            subscription_to_update.end_date = session.get("the_new_end_dt_db")
            subscription_to_update.tax = float(session.get("new_sub_tax"))

        subscription_to_update.date_of_editing = convert_dt_to_str(dt_format=dt_format_db)
        db.session.commit()
        flash(message=update_record_msg,
              category="success"
              )
    except Exception as err:
        # TODO write in log file errs
        db.session.rollback()
        print(err)
        flash(message=failed_update_record_msg,
              category="danger"
              )
    finally:
        db.session.close()
        return redirect(location=url_for("subscriptions_page"))


@app.route("/expire_subscriptions", methods=["GET", "POST"])
@login_required
def expire_subscriptions():
    # list of all expired and about to expire in the next 24h subscriptions
    expiry_sub_lst = (db.session.query(
        Subscriptions.end_date,
        Subscriptions.parking_spot_number,
        Vehicles.vehicle_registration_number,
        Customers.first_name,
        Customers.last_name,
        Customers.phone,
        Vehicles.vehicle_id,
        Subscriptions.subscription_id
    ).join(Vehicles,
           Customers.customer_id == Vehicles.customer_id
           ).join(Subscriptions,
                  Vehicles.vehicle_id == Subscriptions.vehicle_id)
                      ).filter(Subscriptions.end_date < day_ahead(),
                               Vehicles.is_subscribed.is_(True),
                               Subscriptions.subscription_status == "ACTIVE"
                               ).order_by(Subscriptions.end_date).all()

    if request.method == "POST":
        subscription_information = request.form.get("sub_table_info")

        session["exp_sub_parking_id"] = str_split_pick(str_to_split=subscription_information,
                                                       index=-1,
                                                       return_int=True
                                                       )
        session["exp_sub_end_date"] = str_split_pick(str_to_split=subscription_information,
                                                     index=0
                                                     )
        session["exp_sub_end_time"] = str_split_pick(str_to_split=subscription_information,
                                                     index=1
                                                     )
        session["exp_sub_spot_num"] = str_split_pick(str_to_split=subscription_information,
                                                     index=3
                                                     )
        session["exp_sub_reg_num"] = str_split_pick(str_to_split=subscription_information,
                                                    index=5
                                                    )
        session["exp_sub_first_name"] = str_split_pick(str_to_split=subscription_information,
                                                       index=7
                                                       )
        session["exp_sub_last_name"] = str_split_pick(str_to_split=subscription_information,
                                                      index=9
                                                      )
        session["exp_sub_vehicle_id"] = str_split_pick(str_to_split=subscription_information,
                                                       index=11
                                                       )
        end_date = str_split_pick(str_to_split=subscription_information,
                                  index=0
                                  )
        end_time = str_split_pick(str_to_split=subscription_information,
                                  index=1
                                  )
        end_dt = compose_dt(date=end_date,
                            time=end_time,
                            dt_format=dt_format_display
                            )
        expiry_check = sub_expiry_check(end_dt=end_dt,
                                        now_dt=dt_now()
                                        )
        session["expiry_check"] = expiry_check
        session["exp_end_dt"] = end_dt
        session["overdue_fee"] = expiry_check[0]
        return redirect(location=url_for("expire_subscription_option"))

    return render_template(template_name_or_list="expire_subscriptions.html",
                           expiry_sub_lst=expiry_sub_lst,
                           imprt=importlib.import_module
                           )


@app.route("/expire_subscription_option")
@login_required
def expire_subscription_option():
    return render_template(template_name_or_list="expire_subscription_option.html")


@app.route("/confirmation_exp_cancel_subscription")
@login_required
def confirmation_exp_cancel_subscription():
    overdue_msg = ""
    overdue = session.get("overdue_fee") != "--"
    if overdue:
        overdue_msg = overdue_fee_msg(session.get('overdue_fee'))

    return render_template(template_name_or_list="confirmation_exp_cancel_subscription.html",
                           first_name=session.get("exp_sub_first_name"),
                           last_name=session.get("exp_sub_last_name"),
                           reg_number=session.get("exp_sub_reg_num"),
                           parking_spot=session.get("exp_sub_spot_num"),
                           custom_msg=overdue_msg,
                           )


@app.route("/cancel_exp_yes_but_action")
@login_required
def cancel_exp_yes_but_action():
    try:
        overdue = session.get("overdue_fee") != "--"
        subscription_to_update = db.session.get(Subscriptions,
                                                session.get("exp_sub_parking_id")
                                                )

        vehicle_to_update = db.session.get(Vehicles,
                                           session.get("exp_sub_vehicle_id")
                                           )

        if overdue:
            subscription_to_update.overdue_fee = decimal.Decimal(session.get("overdue_fee"))

        subscription_to_update.end_date = dt_now()
        subscription_to_update.subscription_status = "CANCELED"
        vehicle_to_update.is_subscribed = False
        db.session.commit()
        flash(message=successful_record_msg,
              category="success"
              )
    except Exception as err:
        print(err)
        # TODO write in log file errs
        db.session.rollback()
        flash(message=failed_record_msg,
              category="danger"
              )
    finally:
        db.session.close()
        return redirect(location=url_for("subscriptions_page"))


@app.route("/renew_subscription", methods=["GET", "POST"])
@login_required
def renew_subscription():
    parking_spot = session.get("exp_sub_spot_num")
    free_spots_list = free_parking_spots(
        db_list=Subscriptions.query.join(Vehicles,
                                         Subscriptions.vehicle_id == Vehicles.vehicle_id
                                         ).where(Subscriptions.subscription_status == "ACTIVE")
    )
    expiry_check = session.get("expiry_check")
    form = EditSubscriptionForm()

    if form.validate_on_submit():
        new_spot = request.form.get("selectSpotSubs")
        new_end_dt = form.end_date.data
        updated_spot, spot_not_changed = new_entry_validation(current_record=parking_spot,
                                                              new_entry=new_spot
                                                              )
        days = calculate_days_diff(start_date=expiry_check[5], end_date=new_end_dt)[0]
        less_than_a_day = days == 0
        dt_invalid = validate_datetime_differance(start_dt=expiry_check[5],
                                                  end_dt=new_end_dt,
                                                  days=days
                                                  )
        if dt_invalid:
            flash(message=dt_invalid,
                  category="info"
                  )
        elif spot_not_changed and less_than_a_day:
            flash(message=no_changes_msg,
                  category="info"
                  )
        else:
            session["renew_new_spot"] = (updated_spot, spot_not_changed)
            session["renew_new_end_dt"] = convert_dt_to_str(dt_format=dt_format_display,
                                                            dt=new_end_dt
                                                            )
            session["renew_start_dt"] = expiry_check[2]
            session["renew_days_diff"] = days
            session["renew_start_dt_db"] = expiry_check[4]
            session["renew_new_end_dt_db"] = convert_dt_to_str(dt_format=dt_format_db,
                                                               dt=new_end_dt
                                                               )
            return redirect(location=url_for("confirmation_renew_subscription"))

    display_error_messages(form=form)
    return render_template(template_name_or_list="renew_subscription.html",
                           free_spots_list=free_spots_list,
                           form=form,
                           parking_spot=parking_spot,
                           overdue_check=expiry_check[1],
                           first_name=session.get("exp_sub_first_name"),
                           last_name=session.get("exp_sub_last_name"),
                           reg_number=session.get("exp_sub_reg_num"),
                           start_dt=expiry_check[2],
                           start_dt_info=expiry_check[3]
                           )


@app.route("/confirmation_renew_subscription")
@login_required
def confirmation_renew_subscription():
    parking_spot = session.get("renew_new_spot")[0]
    # calculates renewed sub tax
    sub_tax = "{:.2f}".format(session.get("renew_days_diff") * 5)
    session["renew_sub_to_add"] = Subscriptions(parking_spot_number=parking_spot,
                                                start_date=session.get("renew_start_dt_db"),
                                                end_date=session.get("renew_new_end_dt_db"),
                                                tax=sub_tax,
                                                subscription_status="ACTIVE",
                                                vehicle_id=session.get("exp_sub_vehicle_id")
                                                )
    return render_template(template_name_or_list="confirmation_renew_subscription.html",
                           reg_number=session.get("exp_sub_reg_num"),
                           parking_spot=parking_spot,
                           overdue_fee=session.get("overdue_fee"),
                           end_date=session.get("renew_new_end_dt"),
                           first_name=session.get("exp_sub_first_name"),
                           last_name=session.get("exp_sub_last_name"),
                           start_dt=session.get("renew_start_dt"),
                           sub_tax=sub_tax
                           )


@app.route("/renew_yes_but_action")
@login_required
def renew_yes_but_action():
    try:
        # updates expired/about to expire subscription record to inactive and add overdue if needed
        subscription_to_update = db.session.get(Subscriptions,
                                                session.get("exp_sub_parking_id")
                                                )
        no_overdue = session.get("overdue_fee") == "--"
        if no_overdue:
            pass
        else:
            # TODO test if enter correct format after decimal
            subscription_to_update.overdue_fee = float(session.get("overdue_fee"))
        subscription_to_update.subscription_status = "RENEWED"
        # adds the renewed subscription as new db record
        db.session.add(session.get("renew_sub_to_add"))
        db.session.commit()
        flash(message=successful_record_msg,
              category="success"
              )
    except Exception as err:
        print(err)
        # TODO write in log file errs
        db.session.rollback()
        flash(message=failed_record_msg,
              category="danger"
              )
    finally:
        db.session.close()
        return redirect(location=url_for("subscriptions_page"))


@app.route("/customers")
@login_required
def customers_page():
    return render_template(template_name_or_list="customers.html")


@app.route("/add_customer", methods=["GET", "POST"])
@login_required
def add_customer():
    form = CustomersRegisterForm()
    if form.validate_on_submit():
        phone_exist = db_phone_uniqueness_check(model=Customers,
                                                form_data=request.form["phone"]
                                                )
        # checks if phone number is unique
        if phone_exist:
            flash(message=record_exist_msg("phone number"),
                  category="info"
                  )
        else:
            session["add_first_name"] = form.first_name.data.upper()
            session["add_last_name"] = form.last_name.data.upper()
            session["add_phone"] = form.phone.data
            session["add_address"] = form.address.data.upper()
            # redirect to different page
            return redirect(location=url_for("confirmation_customer"))

    display_error_messages(form=form)
    return render_template(template_name_or_list="add_customer.html",
                           form=form
                           )


@app.route("/confirmation_customer")
@login_required
def confirmation_customer():
    first_name = session.get("add_first_name")
    last_name = session.get("add_last_name")
    phone = session.get("add_phone")
    address = session.get("add_address")
    # if the user did not provide address it fills it. Used for checks during updating customers info
    if not address:
        address = "--"
    session["customer_to_add"] = Customers(first_name=first_name,
                                           last_name=last_name,
                                           phone=phone,
                                           address=address,
                                           registration_date=convert_dt_to_str(dt_format=dt_format_db)
                                           )
    return render_template(template_name_or_list="confirmation_customer.html",
                           first_name=first_name,
                           last_name=last_name,
                           phone=phone,
                           address=address
                           )


@app.route("/add_customer_yes_but_action")
@login_required
def add_customer_yes_but_action():
    try:
        db.session.add(session.get("customer_to_add"))
        db.session.commit()
        flash(message=successful_record_msg,
              category="success"
              )
        return redirect(location=url_for("vehicles_page"))
    except Exception as err:
        # TODO write in log file errs
        db.session.rollback()
        flash(message=failed_record_msg,
              category="danger"
              )
        return redirect(location=url_for("customers_page"))
    finally:
        db.session.close()


@app.route("/select_customer_edit", methods=["GET", "POST"])
@login_required
def select_customer_edit():
    # create list of all existing customers which will be used for the drop-down select menu
    customers_list = Customers.query.order_by(Customers.customer_id).all()
    form = SelectEditForm()
    if form.validate_on_submit():
        session["customer_information"] = request.form.get("selectCustomerEdit")
        return redirect(location=url_for("edit_customer"))

    display_error_messages(form=form)
    return render_template(template_name_or_list="select_customer_edit.html",
                           form=form,
                           customers_list=customers_list
                           )


@app.route("/edit_customer", methods=["GET", "POST"])
@login_required
def edit_customer():
    # gets the info for the selected customer
    customer_information = session.get("customer_information")
    customer_id = str_split_pick(str_to_split=customer_information,
                                 index=0,
                                 return_int=True
                                 )
    # creates a session for the selected customer
    customer_to_update = db.session.get(Customers,
                                        customer_id
                                        )
    form = EditCustomerFrom(obj=customer_to_update)
    if form.validate_on_submit():
        # checks phone for uniqueness
        phone_exist = db_phone_uniqueness_check(model=Customers,
                                                form_data=request.form["phone"]
                                                )
        # takes customer's first name from html select in order to make alphabet differance check
        current_first_name = str_split_pick(str_to_split=customer_information,
                                            index=4
                                            )
        updated_first_name, f_name_not_changed = new_entry_validation(current_record=current_first_name,
                                                                      new_entry=request.form["first_name"].upper()
                                                                      )

        current_last_name = str_split_pick(str_to_split=customer_information,
                                           index=8
                                           )
        new_last_name = request.form["last_name"].upper()
        updated_last_name, l_name_not_changed = new_entry_validation(current_record=current_last_name,
                                                                     new_entry=new_last_name
                                                                     )

        current_phone = str_split_pick(str_to_split=customer_information,
                                       index=11
                                       )
        new_phone = request.form["phone"]
        updated_phone, phone_not_changed = new_entry_validation(current_record=current_phone,
                                                                new_entry=new_phone
                                                                )

        current_address = str_split_pick(str_to_split=customer_information,
                                         index=14
                                         )
        new_address = request.form["address"].upper()
        updated_address, address_not_changed = new_entry_validation(current_record=current_address,
                                                                    new_entry=new_address,
                                                                    is_address=True
                                                                    )
        new_phone = current_phone != updated_phone
        invalid_current_first_name_latin = validate_check_from_lst(var_to_check=current_first_name,
                                                                   list_to_compare=latin_letters
                                                                   )
        invalid_updated_first_name_cyrillic = validate_check_from_lst(var_to_check=updated_first_name,
                                                                      list_to_compare=cyrillic_letters
                                                                      )
        invalid_current_first_name_cyrillic = validate_check_from_lst(var_to_check=current_first_name,
                                                                      list_to_compare=cyrillic_letters
                                                                      )
        invalid_updated_first_name_latin = validate_check_from_lst(var_to_check=updated_first_name,
                                                                   list_to_compare=latin_letters
                                                                   )
        # prevents to continue if the first name is different alphabet from the existing db record. The same check
        # for the rest customer's fields continues in the edit customer form. There, for comparing is used the
        # first name again which is already in the correct alphabet because of this check
        if (invalid_current_first_name_latin and invalid_updated_first_name_cyrillic) or \
                (invalid_current_first_name_cyrillic and invalid_updated_first_name_latin):
            flash(message=alphabet_db_mix_msg("The first name"),
                  category="info"
                  )
        # checks if new phone number is unique
        elif phone_exist and new_phone:
            flash(message=record_exist_msg("phone number"),
                  category="info"
                  )
        # prevents continue if changes are not made
        elif f_name_not_changed and l_name_not_changed and phone_not_changed and address_not_changed:
            flash(message=no_changes_msg,
                  category="info"
                  )
        else:
            session["the_new_first_name"] = (updated_first_name, f_name_not_changed)
            session["the_new_last_name"] = (updated_last_name, l_name_not_changed)
            session["the_new_phone"] = (updated_phone, phone_not_changed)
            session["the_new_address"] = (updated_address, address_not_changed)
            session["edit_customer_id"] = customer_id
            return redirect(location=url_for("confirmation_edit_customer"))

    display_error_messages(form=form)
    return render_template(template_name_or_list="edit_customer.html",
                           form=form
                           )


@app.route("/confirmation_edit_customer")
@login_required
def confirmation_edit_customer():
    return render_template(template_name_or_list="confirmation_edit_customer.html",
                           updated_first_name=session.get("the_new_first_name")[0],
                           updated_last_name=session.get("the_new_last_name")[0],
                           updated_phone=session.get("the_new_phone")[0],
                           updated_address=session.get("the_new_address")[0]
                           )


@app.route("/edit_customer_yes_but_action")
@login_required
def edit_customer_yes_but_action():
    try:
        customer_to_update = db.session.get(Customers,
                                            session.get("edit_customer_id")
                                            )
        updated_first_name, f_name_not_changed = session.get("the_new_first_name")
        updated_last_name, l_name_not_changed = session.get("the_new_last_name")
        updated_phone, phone_not_changed = session.get("the_new_phone")
        updated_address, address_not_changed = session.get("the_new_address")

        if f_name_not_changed:
            pass
        else:
            customer_to_update.first_name = updated_first_name.upper()

        if l_name_not_changed:
            pass
        else:
            customer_to_update.last_name = updated_last_name.upper()

        if phone_not_changed:
            pass
        else:
            customer_to_update.phone = updated_phone

        if address_not_changed:
            pass
        else:
            customer_to_update.address = updated_address.upper()

        customer_to_update.date_of_editing = convert_dt_to_str(dt_format=dt_format_db)
        db.session.commit()
        flash(message=update_record_msg,
              category="success"
              )
    except Exception as err:
        # TODO write in log file errs
        db.session.rollback()
        flash(message=failed_update_record_msg,
              category="danger"
              )
    finally:
        db.session.close()
        return redirect(location=url_for("customers_page"))


@app.route("/select_delete_customer", methods=["GET", "POST"])
@login_required
def select_delete_customer():
    # create list of all existing customers which will be used for the drop-down select menu
    customers_list = Customers.query.order_by(Customers.customer_id).all()
    form = DeleteForm()

    if form.validate_on_submit():
        customer_information = request.form.get("selectCustomerDelete")

        session["del_customer_id"] = str_split_pick(str_to_split=customer_information,
                                                    index=0,
                                                    return_int=True
                                                    )
        session["del_first_name"] = str_split_pick(str_to_split=customer_information,
                                                   index=4
                                                   )
        session["del_last_name"] = str_split_pick(str_to_split=customer_information,
                                                  index=8
                                                  )
        session["del_phone"] = str_split_pick(str_to_split=customer_information,
                                              index=11
                                              )
        return redirect(location=url_for("confirmation_deleting_customer"))

    display_error_messages(form=form)
    return render_template(template_name_or_list="select_delete_customer.html",
                           form=form,
                           customers_list=customers_list
                           )


@app.route("/confirmation_deleting_customer", methods=["GET", "POST"])
@login_required
def confirmation_deleting_customer():
    session["customer_to_delete"] = db.session.get(Customers,
                                                   session.get("del_customer_id")
                                                   )

    return render_template(template_name_or_list="confirmation_deleting_customer.html",
                           first_name=session.get("del_first_name"),
                           last_name=session.get("del_last_name"),
                           phone=session.get("del_phone")
                           )


@app.route("/customer_yes_but_del_action")
@login_required
def customer_yes_but_del_action():
    try:
        db.session.delete(session.get("customer_to_delete"))
        db.session.commit()
        flash(message=successful_del_record_msg,
              category="success"
              )
    except Exception as err:
        # TODO write err in log
        db.session.rollback()
        flash(message=failed_del_record_msg,
              category="danger"
              )
    finally:
        db.session.close()
        return redirect(location=url_for("customers_page"))


@app.route("/vehicles")
@login_required
def vehicles_page():
    return render_template("vehicles.html")


@app.route("/add_vehicle", methods=["GET", "POST"])
@login_required
def add_vehicle():
    customers_list = Customers.query.order_by(Customers.customer_id).all()
    form = VehiclesRegisterForm()

    if form.validate_on_submit():
        reg_number_exist = db_reg_uniqueness_check(model=Vehicles,
                                                   form_data=request.form["vehicle_registration_number"]
                                                   )
        if reg_number_exist:
            flash(message=record_exist_msg("registration number"),
                  category="info"
                  )
        else:
            session["add_registration_number"] = form.vehicle_registration_number.data.upper()
            session["add_type"] = form.vehicle_type.data.upper()
            session["add_brand"] = form.brand.data.upper()
            session["add_model"] = form.model.data.upper()
            session["add_color"] = form.color.data.upper()
            session["add_customer_id"] = str_split_pick(str_to_split=request.form.get("selectCustomer"),
                                                        index=0,
                                                        return_int=True
                                                        )
            first_name = str_split_pick(str_to_split=request.form.get("selectCustomer"),
                                        index=2
                                        )
            last_name = str_split_pick(str_to_split=request.form.get("selectCustomer"),
                                       index=3
                                       )
            # customer full name
            session["add_vehicle_to_customer"] = (first_name + " " + last_name)
            return redirect(location=url_for("confirmation_vehicle"))

    display_error_messages(form=form)
    return render_template(template_name_or_list="add_vehicle.html",
                           form=form,
                           customers_list=customers_list
                           )


@app.route("/confirmation_vehicle")
@login_required
def confirmation_vehicle():
    reg_number = session.get("add_registration_number")
    vehicle_type = session.get("add_type")
    brand = session.get("add_brand")
    model = session.get("add_model")
    color = session.get("add_color")

    session["vehicle_to_add"] = Vehicles(vehicle_registration_number=reg_number,
                                         vehicle_type=vehicle_type,
                                         brand=brand,
                                         model=model,
                                         color=color,
                                         registration_date=convert_dt_to_str(dt_format=dt_format_db),
                                         is_subscribed=False,
                                         customer_id=session.get("add_customer_id")
                                         )
    return render_template(template_name_or_list="confirmation_vehicle.html",
                           reg_number=reg_number,
                           vehicle_type=vehicle_type,
                           brand=brand,
                           model=model,
                           color=color,
                           customer=session.get("add_vehicle_to_customer")
                           )


@app.route("/add_vehicle_yes_but_action")
@login_required
def add_vehicle_yes_but_action():
    try:
        db.session.add(session.get("vehicle_to_add"))
        db.session.commit()
        flash(message=successful_record_msg,
              category="success"
              )
        return redirect(location=url_for("subscriptions_page"))
    except Exception as err:
        # TODO write in log file errs
        db.session.rollback()
        flash(message=failed_record_msg,
              category="danger"
              )
        return redirect(location=url_for("vehicles_page"))
    finally:
        db.session.close()


@app.route("/select_vehicle_edit", methods=["GET", "POST"])
@login_required
def select_vehicle_edit():
    # create lis of all existing vehicles which will be used for the drop-down select menu
    vehicles_list = Vehicles.query.order_by(Vehicles.vehicle_id).all()
    form = SelectEditForm()

    if form.validate_on_submit():
        session["vehicle_information"] = request.form.get("selectVehicleEdit")
        return redirect(location=url_for("edit_vehicle"))

    display_error_messages(form=form)
    return render_template(template_name_or_list="select_vehicle_edit.html",
                           form=form,
                           vehicles_list=vehicles_list
                           )


@app.route("/edit_vehicle", methods=["GET", "POST"])
@login_required
def edit_vehicle():
    vehicle_information = session.get("vehicle_information")

    vehicle_id = str_split_pick(str_to_split=vehicle_information,
                                index=0,
                                return_int=True
                                )
    vehicle_to_update = db.session.get(Vehicles,
                                       vehicle_id
                                       )
    # gets a customer name from the db that corresponds of the given vehicle. It will be used for latin-cyrillic check
    # and preventing mix db records between them
    customer_first_name_db = (db.session.query(
        Customers.first_name
    ).join(Vehicles,
           Customers.customer_id == Vehicles.customer_id)
                              ).filter(Vehicles.vehicle_id == vehicle_id).first()[0]

    form = EditVehicleFrom(obj=vehicle_to_update)

    if form.validate_on_submit():
        reg_number_exist = db_reg_uniqueness_check(model=Vehicles,
                                                   form_data=request.form["vehicle_registration_number"]
                                                   )

        current_reg_number = str_split_pick(str_to_split=vehicle_information,
                                            index=4
                                            )
        new_reg_number = request.form["vehicle_registration_number"].upper()
        updated_reg_number, reg_number_not_changed = new_entry_validation(current_record=current_reg_number,
                                                                          new_entry=new_reg_number
                                                                          )

        current_type = str_split_pick(str_to_split=vehicle_information,
                                      index=7
                                      )
        new_type = request.form["vehicle_type"].upper()
        updated_type, type_not_changed = new_entry_validation(current_record=current_type,
                                                              new_entry=new_type
                                                              )

        current_brand = str_split_pick(str_to_split=vehicle_information,
                                       index=10
                                       )
        new_brand = request.form["brand"].upper()
        updated_brand, brand_not_changed = new_entry_validation(current_record=current_brand,
                                                                new_entry=new_brand
                                                                )

        current_model = str_split_pick(str_to_split=vehicle_information,
                                       index=13
                                       )
        new_model = request.form["model"].upper()
        updated_model, model_not_changed = new_entry_validation(current_record=current_model,
                                                                new_entry=new_model
                                                                )

        current_color = str_split_pick(str_to_split=vehicle_information,
                                       index=16
                                       )
        new_color = request.form["color"].upper()
        updated_color, color_not_changed = new_entry_validation(current_record=current_color,
                                                                new_entry=new_color
                                                                )
        new_reg_number = current_reg_number != updated_reg_number
        invalid_current_first_name_latin = validate_check_from_lst(var_to_check=customer_first_name_db,
                                                                   list_to_compare=latin_letters
                                                                   )
        invalid_updated_type_cyrillic = validate_check_from_lst(var_to_check=updated_type,
                                                                list_to_compare=cyrillic_letters
                                                                )
        invalid_current_first_name_cyrillic = validate_check_from_lst(var_to_check=customer_first_name_db,
                                                                      list_to_compare=cyrillic_letters
                                                                      )
        invalid_updated_type_latin = validate_check_from_lst(var_to_check=updated_type,
                                                             list_to_compare=latin_letters
                                                             )
        if (invalid_current_first_name_latin and invalid_updated_type_cyrillic) or \
                (invalid_current_first_name_cyrillic and invalid_updated_type_latin):
            flash(message=alphabet_db_mix_msg("The vehicle type"),
                  category="info"
                  )
        elif reg_number_exist and new_reg_number:
            flash(message=record_exist_msg("registration number"),
                  category="info"
                  )
        elif (reg_number_not_changed and type_not_changed and brand_not_changed and model_not_changed and
              color_not_changed):
            flash(message=no_changes_msg,
                  category="info"
                  )
        else:
            session["the_new_reg_number"] = (updated_reg_number, reg_number_not_changed)
            session["the_new_type"] = (updated_type, type_not_changed)
            session["the_new_brand"] = (updated_brand, brand_not_changed)
            session["the_new_model"] = (updated_model, model_not_changed)
            session["the_new_color"] = (updated_color, color_not_changed)
            session["edit_vehicle_id"] = vehicle_id
            return redirect(location=url_for("confirmation_edit_vehicle"))

    display_error_messages(form=form)
    return render_template(template_name_or_list="edit_vehicle.html",
                           form=form
                           )


@app.route("/confirmation_edit_vehicle")
@login_required
def confirmation_edit_vehicle():
    return render_template(template_name_or_list="confirmation_edit_vehicle.html",
                           updated_reg_number=session.get("the_new_reg_number")[0],
                           updated_type=session.get("the_new_type")[0],
                           updated_brand=session.get("the_new_brand")[0],
                           updated_model=session.get("the_new_model")[0],
                           updated_color=session.get("the_new_color")[0]
                           )


@app.route("/edit_vehicle_yes_but_action")
@login_required
def edit_vehicle_yes_but_action():
    try:
        vehicle_to_update = db.session.get(Vehicles,
                                           session.get("edit_vehicle_id")
                                           )
        updated_reg_number, reg_number_not_changed = session.get("the_new_reg_number")
        updated_type, type_not_changed = session.get("the_new_type")
        updated_brand, brand_not_changed = session.get("the_new_brand")
        updated_model, model_not_changed = session.get("the_new_model")
        updated_color, color_not_changed = session.get("the_new_color")

        if reg_number_not_changed:
            pass
        else:
            vehicle_to_update.vehicle_registration_number = updated_reg_number.upper()

        if type_not_changed:
            pass
        else:
            vehicle_to_update.vehicle_type = updated_type.upper()

        if brand_not_changed:
            pass
        else:
            vehicle_to_update.brand = updated_brand.upper()

        if model_not_changed:
            pass
        else:
            vehicle_to_update.model = updated_model.upper()

        if color_not_changed:
            pass
        else:
            vehicle_to_update.color = updated_color.upper()

        vehicle_to_update.date_of_editing = convert_dt_to_str(dt_format=dt_format_db)

        db.session.commit()
        flash(message=update_record_msg,
              category="success"
              )
    except Exception as err:
        # TODO write in log file errs
        db.session.rollback()
        flash(message=failed_update_record_msg,
              category="danger"
              )
    finally:
        db.session.close()
        return redirect(location=url_for("vehicles_page"))


@app.route("/select_delete_vehicle", methods=["GET", "POST"])
@login_required
def select_delete_vehicle():
    vehicles_list = Vehicles.query.order_by(Vehicles.vehicle_id).all()
    form = DeleteForm()

    if form.validate_on_submit():
        vehicle_information = request.form.get("selectVehicleDelete")

        session["del_vehicle_id"] = str_split_pick(str_to_split=vehicle_information,
                                                   index=0,
                                                   return_int=True
                                                   )
        session["del_vehicle_reg_num"] = str_split_pick(str_to_split=vehicle_information,
                                                        index=4
                                                        )
        return redirect(location=url_for("confirmation_deleting_vehicle"))

    display_error_messages(form=form)
    return render_template(template_name_or_list="select_delete_vehicle.html",
                           form=form,
                           vehicles_list=vehicles_list
                           )


@app.route("/confirmation_deleting_vehicle", methods=["GET", "POST"])
@login_required
def confirmation_deleting_vehicle():
    # gets owners full name
    first_name, last_name = (db.session.query(
        Customers.first_name,
        Customers.last_name
    ).join(Vehicles,
           Customers.customer_id == Vehicles.customer_id)
                             ).filter(Vehicles.vehicle_id == session.get("del_vehicle_id")).first()

    session["vehicle_to_delete"] = db.session.get(Vehicles,
                                                  session.get("del_vehicle_id")
                                                  )

    return render_template(template_name_or_list="confirmation_deleting_vehicle.html",
                           first_name=first_name,
                           last_name=last_name,
                           reg_number=session.get("del_vehicle_reg_num")
                           )


@app.route("/vehicle_yes_but_del_action")
@login_required
def vehicle_yes_but_del_action():
    try:
        db.session.delete(session.get("vehicle_to_delete"))
        db.session.commit()
        flash(message=successful_del_record_msg,
              category="success"
              )
    except Exception as err:
        # TODO write err in log
        db.session.rollback()
        flash(message=failed_del_record_msg,
              category="danger"
              )
    finally:
        db.session.close()
        return redirect(location=url_for("vehicles_page"))


@app.route("/reports")
@login_required
def reports_page():
    return render_template(template_name_or_list="reports.html")


@app.route("/select_customer_report", methods=["GET", "POST"])
@login_required
def select_customer_report():
    customers_list = Customers.query.order_by(Customers.customer_id).all()
    form = SelectEditForm()

    if form.validate_on_submit():
        customer_information = request.form.get("selectCustomerReport")

        session["customer_id_report"] = str_split_pick(str_to_split=customer_information,
                                                       index=0,
                                                       return_int=True
                                                       )
        session["first_name_report"] = str_split_pick(str_to_split=customer_information,
                                                      index=4
                                                      )
        session["last_name_report"] = str_split_pick(str_to_split=customer_information,
                                                     index=8
                                                     )
        return redirect(location=url_for("customer_report"))

    return render_template(template_name_or_list="select_customer_report.html",
                           customers_list=customers_list,
                           form=form
                           )


@app.route("/customer_report")
@login_required
def customer_report():
    customer_id = session.get("customer_id_report")
    customer_record = db.session.get(Customers,
                                     customer_id
                                     )
    # list of all customer vehicles
    vehicle_customer_lst = (db.session.query(
        Customers.customer_id,
        Vehicles.vehicle_registration_number,
        Vehicles.vehicle_type,
        Vehicles.brand,
        Vehicles.model,
        Vehicles.color,
        Vehicles.registration_date,
        Vehicles.date_of_editing,
        Vehicles.is_subscribed
    ).join(Vehicles,
           Customers.customer_id == Vehicles.customer_id)
                            ).filter(Customers.customer_id == customer_id
                                     ).order_by(Vehicles.registration_date).all()
    # full list of customer subscription
    subscription_customer_lst = db.session.query(
        Customers.customer_id,
        Subscriptions.subscription_status,
        Vehicles.vehicle_registration_number,
        Subscriptions.parking_spot_number,
        Subscriptions.tax,
        Subscriptions.start_date,
        Subscriptions.end_date,
        Subscriptions.overdue_fee,
        Subscriptions.date_of_editing
    ).join(Vehicles,
           Vehicles.customer_id == Customers.customer_id
           ).join(Subscriptions,
                  Subscriptions.vehicle_id == Vehicles.vehicle_id
                  ).filter(Customers.customer_id == customer_id
                           ).order_by(Vehicles.vehicle_registration_number,
                                      Subscriptions.start_date).all()

    date_of_registration = convert_dt_to_str(dt_format=dt_format_display,
                                             dt=customer_record.registration_date
                                             )
    date_of_editing = skipped_dt(dt_db=customer_record.date_of_editing)

    return render_template(template_name_or_list="customer_report.html",
                           imprt=importlib.import_module,
                           first_name=session.get("first_name_report"),
                           last_name=session.get("last_name_report"),
                           date_of_registration=date_of_registration,
                           date_of_editing=date_of_editing,
                           phone=customer_record.phone,
                           address=customer_record.address,
                           vehicle_customer_lst=vehicle_customer_lst,
                           subscription_customer_lst=subscription_customer_lst
                           )


@app.route("/free_parking_spots_report")
@login_required
def free_parking_spots_report():
    free_spots_list = free_parking_spots(
        db_list=Subscriptions.query.join(Vehicles,
                                         Subscriptions.vehicle_id == Vehicles.vehicle_id
                                         ).where(Subscriptions.subscription_status == "ACTIVE")
    )
    return render_template(template_name_or_list="free_parking_spots_report.html",
                           free_spots_list=free_spots_list
                           )
