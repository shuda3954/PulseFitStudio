import datetime

CLASSES_FILE     = "Classes.txt"
USERS_FILE       = "Users.txt"
MEMBERS_FILE     = "Members.txt"
BOOKINGS_FILE    = "Bookings.txt"
PAYMENTS_FILE    = "Payments.txt"
MAINTENANCE_FILE = "Maintenance.txt"
REPORT_FILE      = "Admin_report.txt"

# Expected field counts per file - used to skip corrupted lines.
EXPECTED_FIELDS = {
    CLASSES_FILE: 7,      # class_id, name, instructor, date, time, capacity, current_bookings
    USERS_FILE: 3,        # username, password, role
    MEMBERS_FILE: 7,      # member_id, name, phone, email, join_date, plan, status
    BOOKINGS_FILE: 6,     # booking_id, member_id, class_id, date, status, attendance
    PAYMENTS_FILE: 6,     # payment_id, member_id, booking_id, amount, date, status
    MAINTENANCE_FILE: 5,  # equipment_id, equipment_name, status, last_service, notes
}

# PURE VALIDATION CHECKS (return True/False)
def is_valid_text(value):
    """Text must not be blank and must not contain a comma."""
    return value != "" and "," not in value


def is_valid_date(value):
    """Date must use DD-MM-YYYY format, fall within 2000-2100, and be a real calendar date."""
    if len(value) == 10 and value[2] == "-" and value[5] == "-":
        dd = value[:2]
        mm = value[3:5]
        yyyy = value[6:]
        if is_all_digits(dd) and is_all_digits(mm) and is_all_digits(yyyy):
            day = int(dd)
            month = int(mm)
            year = int(yyyy)
            if year >= 2000 and year <= 2100:
                # leap-year aware day limit for each month:
                # work out February first with a normal if/else, then build the list
                if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                    february_days = 29
                else:
                    february_days = 28
                days_in_month = [31, february_days, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                if month >= 1 and month <= 12 and day >= 1 and day <= days_in_month[month - 1]:
                    return True
    return False


def is_valid_time(value):
    """Time must be HH:MM format"""
    if len(value) == 5 and value[2] == ":":
        hh = value[:2]
        mm = value[3:]
        if is_all_digits(hh) and is_all_digits(mm):
            hour = int(hh)
            minute = int(mm)
            if hour >= 0 and hour <= 23 and minute >= 0 and minute <= 59:
                return True
    return False


def is_valid_capacity(value):
    """Capacity must be a whole number of at least 1"""
    if is_all_digits(value):
        return int(value) >= 1
    return False


def is_all_digits(value):
    """True only if every character is a plain digit 0-9."""
    if value == "":
        return False
    for ch in value:
        if ch not in "0123456789":
            return False
    return True


# VALIDATED INPUT LOOPS
def get_non_empty(prompt):
    """Keep asking until the input is not blank and contains no comma."""
    while True:
        value = input(prompt).strip()
        if is_valid_text(value):
            return value
        print("  ! Blank or commas not allowed. Try again.")


def get_valid_date(prompt):
    """Keep asking until the input passes is_valid_date."""
    while True:
        value = input(prompt).strip()
        if is_valid_date(value):
            return value
        print("  ! Use a real date in DD-MM-YYYY format, e.g. 05-10-2026.")


def get_valid_time(prompt):
    """Keep asking until the input passes is_valid_time."""
    while True:
        value = input(prompt).strip()
        if is_valid_time(value):
            return value
        print("  ! Use 24-hour HH:MM format, e.g. 18:30.")


def get_valid_capacity(prompt):
    """Keep asking until the input passes is_valid_capacity."""
    while True:
        value = input(prompt).strip()
        if is_valid_capacity(value):
            return value
        print("  ! Enter a whole number >= 1.")


def get_menu_choice(prompt, valid_choices):
    """Menu loop in which answer is returned in lower case."""
    while True:
        value = input(prompt).strip().lower()
        if value in valid_choices:
            return value
        print("  ! Invalid option. Choose from: " + "/".join(valid_choices))


def pause():
    input("\nPress Enter to continue...")


#FILE
def read_records(filename):
    """Read a text file into a list of records."""
    records = []
    expected = EXPECTED_FIELDS.get(filename)
    try:
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if line != "":                       # skip blank lines
                    fields = []
                    for field in line.split(","):
                        fields.append(field.strip())
                    if expected is not None and len(fields) != expected:
                        print("! Skipping malformed line in", filename, ":", line)
                        continue
                    records.append(fields)
    except FileNotFoundError:
        print("! File not found:", filename, "- starting with empty data.")
    return records


def write_records(filename, records):

    try:
        with open(filename, "w") as f:
            for rec in records:
                f.write(",".join(rec) + "\n")
        return True
    except OSError:
        print("! Error: could not write to", filename)
        return False


def next_id(prefix, records):
    """Generate the next zero-padded ID for a prefix."""
    highest = 0
    for rec in records:
        if rec[0].startswith(prefix):
            try:
                number = int(rec[0][len(prefix):])
            except ValueError:
                continue                       # suffix is not numeric - skip this record
            if number > highest:
                highest = number
    return prefix + "{:03d}".format(highest + 1)


# BOOKING COUNT

def count_bookings(class_id, bookings, status):
    """counting bookings of one status"""
    total = 0
    for b in bookings:
        if b[2] == class_id and b[4].lower() == status:
            total += 1
    return total

def confirmed_counts_by_class(bookings):
    """Counting confirmed bookings.
     dictionary format- {class_id: count}."""
    counts = {}
    for b in bookings:
        if b[4].lower() == "confirmed":
            counts[b[2]] = counts.get(b[2], 0) + 1
    return counts

# ---------------- LOGIN ----------------
def login_admin():
    """Verify admin input against users.txt.Only 3 attempts allowed"""
    users = read_records(USERS_FILE)
    attempts = 0
    MAX_ATTEMPTS = 3
    while attempts < MAX_ATTEMPTS:
        username = get_non_empty("Username: ")
        password = get_non_empty("Password: ")
        for user in users:
            if user[0] == username and user[1] == password and user[2].lower() == "admin":
                print("\nWelcome " + user[0] + "! You are logged in as Studio Administrator.\n")
                return True
        attempts += 1
        print("Invalid credentials.Attempts left:", MAX_ATTEMPTS - attempts)
    print("Too many failed attempts. Exiting.")
    return False


# ---------------- ADMIN MAIN MENU ----------------
def admin_menu():
    """Main loop for the Studio Administrator role."""
    while True:
        print("========== STUDIO ADMINISTRATOR MENU ==========")
        print("  1. Manage Classes and Schedules")
        print("  2. View All Data (Members / Bookings / Payments / Equipment)")
        print("  3. Generate Overall Report")
        print("  4. View Waitlists")
        print("  0. Logout")
        choice = get_menu_choice("Enter choice: ", ["0", "1", "2", "3", "4"])

        if choice == "1":
            manage_classes_menu()
        elif choice == "2":
            view_all_data()
        elif choice == "3":
            generate_report()
        elif choice == "4":
            view_waitlists()
        elif choice == "0":
            print("Logged out. Goodbye!")
            break


# ============ MANAGE CLASSES AND SCHEDULES ============
def manage_classes_menu():
    while True:
        print("----- Manage Classes and Schedules -----")
        print("  1. Add a New Class")
        print("  2. Update a Class")
        print("  3. Remove a Class")
        print("  0. Back")
        choice = get_menu_choice("Enter choice: ", ["0", "1", "2", "3"])

        if choice == "1":
            add_class()
        elif choice == "2":
            update_class()
        elif choice == "3":
            remove_class()
        elif choice == "0":
            break


def print_class_table(classes, booking_counts):
    print()
    print("{:<6}{:<34}{:<20}{:<11}{:<7}{:<10}{:<7}".format(
        "ID", "Class Name", "Instructor", "Date", "Time", "Capacity", "Booked"))
    print("-" * 95)
    for c in classes:
        # classes.txt fields: class_id, name, instructor, date, time, capacity, current_bookings
        booked = booking_counts.get(c[0], 0)
        print("{:<6}{:<34}{:<20}{:<11}{:<7}{:<10}{:<7}".format(
            c[0], c[1], c[2], c[3], c[4], c[5], str(booked)))
    print()


def find_record(records, rec_id):
    """Return (record, position) for the given ID, or (None, -1) if not found."""
    for i in range(len(records)):
        if records[i][0] == rec_id:
            return records[i], i
    return None, -1


def add_class():
    """Add a new class according to the input and an auto-generated class ID."""
    classes = read_records(CLASSES_FILE)
    print("\n----- Add a New Class -----")
    name       = get_non_empty("Class name: ")
    instructor = get_non_empty("Instructor full name: ")
    class_date = get_valid_date("Class date (DD-MM-YYYY): ")
    time       = get_valid_time("Time (HH:MM, 24-hour): ")
    capacity   = get_valid_capacity("Maximum capacity: ")

    class_id = next_id("C", classes)
    # new class starts with 0 bookings (booked counts are always computed
    # from bookings.txt, not read from this column)
    classes.append([class_id, name, instructor, class_date, time, capacity, "0"])
    if write_records(CLASSES_FILE, classes):
        print(">> Class added:", class_id, "|", name, "|", class_date, time)
    pause()


def update_class():
    classes = read_records(CLASSES_FILE)
    if len(classes) == 0:
        print("\nNo classes found.")
        pause()
        return

    bookings = read_records(BOOKINGS_FILE)
    print_class_table(classes, confirmed_counts_by_class(bookings))
    # retry loop for the ID prompt - '0' still cancels; .upper() so c005 matches C005
    while True:
        class_id = get_non_empty("Enter Class ID to update (or type 0 to cancel): ").upper()
        if class_id == "0":
            return
        target, pos = find_record(classes, class_id)
        if target is not None:
            break
        print("! Class ID not found:", class_id)

    print("\nEditing", target[0], "- press Enter to keep the current value.")
    while True:
        value = input("Class name [" + target[1] + "]: ").strip()
        if value == "":
            break
        if is_valid_text(value):
            target[1] = value
            break
        print("Blank or commas not allowed.")

    while True:
        value = input("Instructor [" + target[2] + "]: ").strip()
        if value == "":
            break
        if is_valid_text(value):
            target[2] = value
            break
        print("Blank or commas not allowed.")

    while True:
        value = input("Date [" + target[3] + "]: ").strip()
        if value == "":
            break
        if is_valid_date(value):
            target[3] = value
            break
        print("Use a real date in DD-MM-YYYY format, e.g. 05-10-2026.")

    while True:
        value = input("Time [" + target[4] + "]: ").strip()
        if value == "":
            break
        if is_valid_time(value):
            target[4] = value
            break
        print("  ! Use 24-hour HH:MM format.")

    classes[pos] = target
    if write_records(CLASSES_FILE, classes):
        print(">> Class updated successfully.")
    pause()


def remove_class():
    """Remove a class from classes.txt."""
    classes = read_records(CLASSES_FILE)
    if len(classes) == 0:
        print("\nNo classes found.")
        pause()
        return

    bookings = read_records(BOOKINGS_FILE)
    print_class_table(classes, confirmed_counts_by_class(bookings))
    # retry loop for the ID prompt - '0' still cancels; .upper() so c005 matches C005
    while True:
        class_id = get_non_empty("Enter Class ID to remove (or type 0 to cancel): ").upper()
        if class_id == "0":
            return
        target, pos = find_record(classes, class_id)
        if target is not None:
            break
        print("! Class ID not found:", class_id)

    confirmed  = count_bookings(class_id, bookings, "confirmed")
    waitlisted = count_bookings(class_id, bookings, "waitlisted")
    if confirmed > 0 or waitlisted > 0:
        print("! This class still has", confirmed, "confirmed and",
              waitlisted, "waitlisted booking(s).")
        print("! Ask the Booking Officer to cancel them before removing the class.")
        pause()
        return

    confirm = get_menu_choice("Remove " + target[0] + " " + target[1] + " permanently? (y/n): ", ["y", "n"])
    if confirm == "y":
        classes.pop(pos)
        if write_records(CLASSES_FILE, classes):
            print(">> Class removed.")
    else:
        print("Removal cancelled.")
    pause()


# ============VIEW ALL DATA ============
def print_table(title, headers, rows):
    print("\n----- " + title + " -----")
    widths = []
    for i in range(len(headers)):
        widths.append(len(headers[i]) + 2)
    for r in rows:
        for i in range(len(headers)):
            if len(r[i]) + 2 > widths[i]:
                widths[i] = len(r[i]) + 2
    line = ""
    for i in range(len(headers)):
        line = line + headers[i] + " " * (widths[i] - len(headers[i]))
    print(line)
    total_width = 0
    for w in widths:
        total_width = total_width + w
    print("-" * total_width)
    for r in rows:
        line = ""
        for i in range(len(headers)):
            line = line + r[i] + " " * (widths[i] - len(r[i]))
        print(line)
    print("Total records:", len(rows))
    print()


def view_all_data():
    classes=read_records(CLASSES_FILE)
    members=read_records(MEMBERS_FILE)
    bookings=read_records(BOOKINGS_FILE)
    payments=read_records(PAYMENTS_FILE)
    maintenance=read_records(MAINTENANCE_FILE)

    booking_counts = confirmed_counts_by_class(bookings)

    class_rows = []
    for c in classes:
        class_rows.append([c[0], c[1], c[2], c[3], c[4], c[5], str(booking_counts.get(c[0], 0))])
    print_table("Classes", ["ID", "Name", "Instructor", "Date", "Time", "Capacity", "Booked"], class_rows)

    member_rows = []
    for m in members:
        member_rows.append([m[0], m[1], m[2], m[3], m[4], m[5], m[6]])
    print_table("Members", ["ID", "Name", "Phone", "Email", "Join Date", "Plan", "Status"], member_rows)

    booking_rows = []
    for b in bookings:
        booking_rows.append([b[0], b[1], b[2], b[3], b[4], b[5]])
    print_table("Bookings", ["Booking ID", "Member ID", "Class ID", "Date", "Status", "Attendance"], booking_rows)

    payment_rows = []
    for p in payments:
        payment_rows.append([p[0], p[1], p[2], p[3], p[4], p[5]])
    print_table("Payments", ["Payment ID", "Member ID", "Booking ID", "Amount", "Date", "Status"], payment_rows)

    # headers aligned with the data dictionary: equipment_id, equipment_name
    equipment_rows = []
    for e in maintenance:
        equipment_rows.append([e[0], e[1], e[2], e[3], e[4]])
    print_table("Equipment / Maintenance",
                ["Equipment ID", "Equipment Name", "Status", "Last Service", "Notes"], equipment_rows)
    pause()

# ============GENERATE OVERALL REPORT============
def generate_report():
    """The studio-wide report:
    total bookings, revenue (paid), outstanding (pending), most popular class
    and instructor, plus per-class availability."""
    classes  = read_records(CLASSES_FILE)
    bookings = read_records(BOOKINGS_FILE)
    payments = read_records(PAYMENTS_FILE)

    # booking counts per class (confirmed only
    booking_count = confirmed_counts_by_class(bookings)
    total_bookings = 0
    for count in booking_count.values():
        total_bookings = total_bookings + count

    #most popular class and its instructor
    most_popular_id, top_count = "None", 0
    instructor_lookup = {}
    for c in classes:
        instructor_lookup[c[0]] = c[2]
    for c in classes:
        n = booking_count.get(c[0], 0)
        if n > top_count:
            most_popular_id, top_count = c[0], n
    top_instructor = instructor_lookup.get(most_popular_id, "-")
    # first match wins; "-" if there is no class with that ID
    top_name = "-"
    for c in classes:
        if c[0] == most_popular_id:
            top_name = c[1]
            break

    total_revenue = 0.0
    outstanding = 0.0
    for p in payments:
        try:
            amount = float(p[3])
        except ValueError:
            print("! Skipping payment with non-numeric amount:", p[0])
            continue
        if p[5].lower() == "paid":            # .lower() so "Paid" also counts
            total_revenue = total_revenue + amount
        elif p[5].lower() == "pending":
            outstanding = outstanding + amount

    # --- build report lines ---
    today = datetime.date.today().strftime("%d-%m-%Y")
    lines = []
    lines.append("PULSEFIT STUDIO - ADMIN OVERALL REPORT")
    lines.append("Generated on: " + today)
    lines.append("=" * 72)
    lines.append("Total confirmed bookings : " + str(total_bookings))
    lines.append("Total revenue (paid)     : RM {:.2f}".format(total_revenue))
    lines.append("Outstanding (pending)    : RM {:.2f}".format(outstanding))
    if most_popular_id != "None":
        lines.append("Most popular class       : " + most_popular_id + " " + top_name
                     + " (" + str(top_count) + " bookings) - " + top_instructor)
    else:
        lines.append("Most popular class       : no confirmed bookings yet")
    lines.append("=" * 72)
    lines.append("{:<6}{:<34}{:<10}{:<10}{:<12}".format("ID", "Class", "Booked", "Capacity", "Slots Left"))
    lines.append("-" * 72)
    for c in classes:
        booked = booking_count.get(c[0], 0)
        try:
            capacity = int(c[5])
        except ValueError:
            capacity = 0
        slots_left = capacity - booked
        # flag clearly if the class is somehow over capacity
        if slots_left < 0:
            slots_text = str(slots_left) + " (over)"
        else:
            slots_text = str(slots_left)
        lines.append("{:<6}{:<34}{:<10}{:<10}{:<12}".format(c[0], c[1], str(booked), c[5], slots_text))
    lines.append("=" * 72)

    print()
    for line in lines:
        print(line)

    save = get_menu_choice("\nSave this report to " + REPORT_FILE + "? (y/n): ", ["y", "n"])
    if save == "y":
        try:
            with open(REPORT_FILE, "w") as f:
                for line in lines:
                    f.write(line + "\n")
            print(">> Report saved to", REPORT_FILE)
        except OSError:
            # OSError is the Python 3 name for IOError - they are the same exception.
            print("! Error: could not save the report file.")
    pause()


# ============VIEW WAITLISTS ============
def view_waitlists():
    """Show all waitlisted bookings joined with member and class names."""
    bookings = read_records(BOOKINGS_FILE)
    members  = read_records(MEMBERS_FILE)
    classes  = read_records(CLASSES_FILE)

    member_names = {}
    for m in members:
        member_names[m[0]] = m[1]
    class_names = {}
    for c in classes:
        class_names[c[0]] = c[1] + " " + c[3] + " " + c[4]   # class name + date + time

    rows = []
    for b in bookings:
        if b[4].lower() == "waitlisted":
            rows.append([b[0], b[1], member_names.get(b[1], "?"),
                         b[2], class_names.get(b[2], "?"), b[3]])
    if len(rows) == 0:
        print("\nNo members are currently on any waitlist.")
    else:
        print_table("Current Waitlists",
                    ["Booking ID", "Member ID", "Member Name", "Class ID", "Class", "Date"], rows)
    pause()


# ---------------- ENTRY POINT ----------------
def main():
    print("======================================")
    print("  PulseFit Studio Booking System")
    print("  Login - Studio Administrator")
    print("======================================")
    if login_admin():
        admin_menu()


if __name__ == "__main__":
    main()