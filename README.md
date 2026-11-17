# PulseFitStudio
Menu-driven Python CLI for a boutique fitness studio: manage classes, view bookings and payments, and generate reports from plain text files. 
<br>
Features
<br>
Login with lockout: three attempts, then the program exits.
<br>
Manage classes: add, update and remove classes.
<br>
Class IDs are generated automatically (C001, C002, ...).
<br>
Input is validated: real calendar dates (DD-MM-YYYY, including leap years), 24-hour times, capacity as a whole number, and no blank or comma-containing values.
<br>
A class cannot be removed while it still has confirmed or waitlisted bookings.
<br>
View all data: classes (with booked counts), members, bookings, payments and equipment, each with a record total.
<br>
Overall report: confirmed bookings, revenue from paid payments, outstanding payments, the most popular class, and slots left for every class. The report can be saved to admin_report.txt.
<br>
View waitlists: waitlisted bookings matched with member and class names.
<br>
Error handling: missing files and malformed lines are reported instead of crashing the program.
<br>
Built with:
<br>
Python 3 (developed on Windows with Python 3.14),
Standard library only (datetime),
Comma-separated .txt files as storage.
