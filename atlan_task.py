from twilio.rest import Client
import re
from fastapi import FastAPI, HTTPException
import csv
import pymysql

app = FastAPI()

# MySQL Database Configuration
db_host = "localhost"
db_user = "employeedb"
db_password = "Password@1"
db_name = "employees"

# Twilio Configuration
twilio_account_sid = "ACc39c72d9a6d18d8a7146bc35d8dc1d2f"
twilio_auth_token = "c7b0c4f67305f3743124c621785dc250"
twilio_phone_number = "+14176373817"

# Establish a database connection
db = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name)

def detect_slangs(sentence):
    with db.cursor() as cursor:
        words = sentence.lower().split()
        detected_slangs = []

        for word in words:
            query = "SELECT word FROM slang_words WHERE word = %s"
            cursor.execute(query, (word,))
            slang = cursor.fetchone()
            if slang:
                detected_slangs.append(slang[0])

    return detected_slangs

@app.get("/detect-slangs")
def detect_slangs_api():
    feedbacks_with_slangs = []

    with db.cursor() as cursor:
        select_query = "SELECT ID, Feedback FROM employee_feedback"
        cursor.execute(select_query)
        feedbacks = cursor.fetchall()

        for feedback_id, feedback_text in feedbacks:
            detected_slangs = detect_slangs(feedback_text)
            if detected_slangs:
                feedbacks_with_slangs.append({"id": feedback_id, "feedback": feedback_text, "slangs": detected_slangs})

    return feedbacks_with_slangs


phone_number_pattern = re.compile(r'^\d{10}$')

@app.get("/flagged-employees")
async def get_flagged_employees():
    try:
        # Create a dictionary to store flagged employees and their reasons
        flagged_employees = {}

        # Retrieve data from the database
        cursor = db.cursor()
        query = "SELECT UID, Name, CurrentSalary, AverageExpense, MobileNo FROM employees_info"
        cursor.execute(query)
        all_employees = cursor.fetchall()

        # Check conditions and store reasons for flagged employees
        for employee in all_employees:
            uid, name, current_salary, average_expense, mobile_no = employee
            reasons = []

            if current_salary < average_expense:
                reasons.append("Salary less than expenses")

            if not phone_number_pattern.match(mobile_no):
                reasons.append("Invalid phone number")

            if reasons:
                flagged_employees[name] = reasons

        # Close the cursor and database connection
        cursor.close()
        db.close()

        # Write flagged employees and their reasons to a CSV file
        flagged_csv_file = "flagged_employees.csv"
        with open(flagged_csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "Reasons"])
            for name, reasons in flagged_employees.items():
                writer.writerow([name, ', '.join(reasons)])

        return {"flagged_employees_csv": flagged_csv_file}
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


def transfer_table_to_csv(cursor, table_name):
    try:
        # Retrieve data from the specified table along with column names
        query = f"SELECT * FROM {table_name}"
        cursor.execute(query)
        table_data = cursor.fetchall()
        table_columns = [column[0] for column in cursor.description]
        
        # Write data to CSV file
        csv_file = f"{table_name}.csv"
        with open(csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(table_columns)
            writer.writerows(table_data)
        
        return csv_file
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transfer-db-to-csv")
async def transfer_db_to_csv():
    try:
        cursor = db.cursor()
        
        # Get the list of tables from the database
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        csv_files = {}

        for table in tables:
            csv_file = transfer_table_to_csv(cursor, table)
            csv_files[table] = csv_file

        cursor.close()
        db.close()

        return {"message": "Data transferred to CSV files successfully.", "csv_files": csv_files}
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
    

@app.post("/send-onboarding-messages")
async def send_onboarding_messages():
    try:
        # Retrieve new employees data from the database
        cursor = db.cursor()
        query = "SELECT Name, Phone FROM new_employees"  # Removed 'Email' from query
        cursor.execute(query)
        new_employees = cursor.fetchall()

        # Initialize Twilio client
        client = Client(twilio_account_sid, twilio_auth_token)

        # Send SMS to each new employee
        for employee in new_employees:
            name, phone = employee
            
            # Generate onboarding message
            onboarding_message = f"Welcome, {name}! We're excited to have you on board."

            # Send SMS
            client.messages.create(to=phone, from_=twilio_phone_number, body=onboarding_message)

        # Close the cursor and database connection
        cursor.close()
        db.close()

        return {"message": "Onboarding SMS messages sent successfully."}
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
    


