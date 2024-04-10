# WEB APPLICATION FOR PRIVATE PARKING MANAGEMENT


My first Flask project so there is room for future improvements.

FEATURES
This is a web application for managing paid parking areas.
The idea of the project is for local PostgreSQL database usage because at this point a loader is skipped in case of time-demanding tasks.
The app takes care of:
1. Customers:
- Registration
- Editing.
- Deleting.
2. Vehicles:
- Registration.
- Editing.
- Deleting.
3. Subscription:
- Parking spots - 60 spots, but can be extended or reduced.
- Adding - minimum period is 1 day and maximum 1 year. The calculation is 5 BGN per day. Settings can be changed.
- Editing - if the subscription has not expired it allows for editing or cancellation.
  If canceled it calculates the amount of the fee left for the period that has to be returned.
- Expiring - refresh in 10 minutes for subscriptions about to expire (less than 24 hours of the subscription period) or expire.
  If the sub is expired allows for renewal or cancellation. In both scenarios calculating overdue fee if the subscription period is overdue.
4. Reporting:
- Unoccupied parking spaces - makes a report of all unoccupied spaces.
- Full report - makes a report for the customer, owning vehicles, and subscription history.

APP CONCEPT
1. Models:
- Users - takes care of the credentials of the application users that are provided by the app provider.
  A user account is required to access any of the application functionality.
- Customers - takes care of the customer's information. The uniqueness of each registered user is restricted by phone number.
  In case of deleting all related to the customer information like vehicle and subscription history will be wiped out.
- Vehicles - takes care of the vehicle's information. A foreign key allows one or more vehicles to be related to a single customer.
  In case of deleting all related to the vehicle information like subscription history will be wiped out.
- Subscriptions - takes care of the subscription's information. A foreign key allows a relation between one subscription and one vehicle.
  Only one subscription can be active for a given vehicle. Inactive subscription status is used for reporting purposes.
2. Database records:
-  My idea for the project was to implement Latin and Cyrillic for the database records restricted by a few exceptions.
   First, mixing between both alphabets in a single record is not allowed, which means a record can be only Latin or
   Cyrillic (ex. first name mixed in both alphabets or first name in Latin and last name in Cyrillic).
   Second, there is an exception only with the registration number because the Bulgaria registration contains Cyrillic letters,
   which means a Latin record can have a Cyrillic registration number and vice versa.
