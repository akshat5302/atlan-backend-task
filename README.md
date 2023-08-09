# Approach / Idea after reading Daisy challenge task

## Optimizing Employee Experience and Operational Efficiency: A Comprehensive Approach

In today's dynamic business landscape, ensuring a seamless and productive work environment is paramount. To achieve this, organizations must harness technology and innovation to address diverse challenges that arise within their workforce. This comprehensive approach outlines a series of tasks designed to enhance employee experience, streamline operations, and uphold the values and standards of your company.

These 4 tasks are the high-level idea I get after reading Daisy's challenge examples

## Task 1: Detecting Slangs from Employees' Feedback

Effective communication is the cornerstone of a healthy workplace culture. However, amidst the myriad interactions that occur, it's crucial to maintain a professional and respectful tone. Task 1 focuses on leveraging language processing techniques to automatically identify and flag any instances of slangs or inappropriate language in employees' feedback. By implementing this solution, we aim to promote a respectful and inclusive communication environment while preserving the integrity of our corporate discourse.

## Task 2: Validating Employees' Responses

Consistency and adherence to established guidelines are vital components of maintaining a cohesive organizational identity. Task 2 delves into the development of an automated validation system that ensures employees' responses align with predefined standards. Through systematic checks and thoughtful feedback, this task aims to cultivate a culture of effective and professional communication, enhancing both internal and external interactions.

## Task 3: Transferring Employees Database to CSV

NOTE - Also by enabling Google Sheets feature we could have great graphs and dashboards as an inbuilt feature of the database to better analyze the data. But I don't have the access to GCP so that's why transferred the db to csv for this demo

Data management plays a pivotal role in informed decision-making and strategic planning. Task 3 centers on the seamless transfer of employees' database to a CSV format, enabling effortless data sharing and analysis. By streamlining this process, we facilitate the availability of accurate and structured employee information, empowering teams across the organization to leverage insights and drive data-driven initiatives.



## Task 4: Sending Onboarding Messages to New Employees

The onboarding process is a pivotal moment for new hires, setting the tone for their journey within the company. Task 4 revolves around automating the delivery of personalized onboarding messages to new employees. By engaging them with timely and relevant information, we aim to foster a positive initial experience, facilitate a smooth integration into the team, and ultimately contribute to employee satisfaction and retention.


## Prerequisites

Before using this script, make sure you have the following components set up:

1. Python environment with required libraries installed.
2. A running database with the specified tables (`employee_feedback`, `employees_info`, and `new_employees`).
3. FastAPI framework installed.

## How to Use

1. Import the necessary libraries at the beginning of your script:

```python
from fastapi import FastAPI, HTTPException
import csv
import mysql.connector
```
2. Initialize FastAPI App
Create an instance of the FastAPI app:

```python
app = FastAPI()
```
## Task 1 -> Slang Detection API

This code snippet provides a simple FastAPI application that implements an API for detecting slangs in employee feedback texts stored in a database. The application connects to a database using the provided connection and performs the following tasks:

1. detect_slangs(sentence) Function: This function takes a sentence as input and detects slangs by querying the slang_words table in the database. It splits the sentence into words, converts them to lowercase, and checks if each word exists in the database. If a slang word is found, it is added to the list of detected slangs.

```python
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
```

2. /detect-slangs Endpoint: This endpoint exposes an API that retrieves employee feedback texts from the employee_feedback table in the database. For each feedback, it uses the detect_slangs function to detect any slangs present in the feedback. If slangs are detected, the feedback's ID, the original feedback text, and the detected slangs are stored in a list. The list is returned as the API response.

```python
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
```

## Task 2 -> Flagged Employees Detection API
This code snippet demonstrates a FastAPI application that identifies and flags employees who meet specific criteria based on their salary, expenses, and mobile phone number. The application connects to a database and performs the following tasks:

1. phone_number_pattern Regular Expression: This regular expression pattern is used to validate phone numbers. It ensures that phone numbers are exactly 10 digits long.

```regex
phone_number_pattern = re.compile(r'^\d{10}$')
```

2. /flagged-employees Endpoint: This endpoint exposes an API that retrieves employee data from the employees_info table in the database. For each employee, it checks whether their current salary is less than their average expense or if their mobile phone number is invalid. If an employee meets any of these conditions, their name and the reasons for flagging are recorded in a dictionary.

```python
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
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))

```

3. The flagged employees' information, including their names and reasons for being flagged, are written to a CSV file named "flagged_employees.csv".

```python
# Write flagged employees and their reasons to a CSV file
flagged_csv_file = "flagged_employees.csv"
with open(flagged_csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Name", "Reasons"])
    for name, reasons in flagged_employees.items():
        writer.writerow([name, ', '.join(reasons)])

return {"flagged_employees_csv": flagged_csv_file}

```

## Task 3 -> Database to CSV Transfer Api

This Python script provides a web API endpoint for transferring data from a database to CSV files. The code is implemented using the FastAPI framework and assumes a connection to a database. When the `/transfer-db-to-csv` endpoint is accessed, it retrieves data from three different database tables: `employee_feedback`, `employees_info`, and `new_employees`, and then writes the data to corresponding CSV files.

1. Function to search table in db and create csv for them
```python
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
```
2. Define the /transfer-db-to-csv endpoint that performs the data transfer:
```python
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
```
## Task 4 -> Employee Onboarding SMS Sender
This code snippet showcases a FastAPI application that automates sending onboarding SMS messages to new employees using the Twilio service. The application connects to a database and performs the following tasks:

```plaintext
# Twilio Configuration
twilio_account_sid = "ACc39c72d9a6d18d8a7146bcxxxxxxxx"
twilio_auth_token = "c7b0c4f67305f37431xxxxxxxxx"
twilio_phone_number = "+14176xxxxxx"
```

2. /send-onboarding-messages Endpoint: This endpoint exposes an API that retrieves data of new employees from the new_employees table in the database. For each new employee, it generates an onboarding message using their name and sends an SMS using the Twilio API.

```python
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
```
## Important Notes
1. Replace Database Connection Details
Replace the placeholders in the script with your actual database connection details.

```plaintext
# MySQL Database Configuration
db_host = "localhost"
db_user = "employeedb"
db_password = "Password@1"
db_name = "employees"
```

2. Run the FastAPI App
Launch the FastAPI app using the following command:

```bash
#Replace your_script_name with the name of your Python script.
uvicorn your_script_name:app --host 0.0.0.0 --port 8000
```


3. Access the Data Transfer Endpoint
Use an HTTP POST request to access the /<api-endpoint>, for example:

```plaintext
# For POST Method
curl -X POST localhost:8000/transfer-db-to-csv

# For GET Method
curl localhost:8000/detect-slangs
```

## Warnings
1. Ensure that sensitive information like database credentials is handled securely.
Consider implementing proper error handling and authentication mechanisms for production use.
2. Customize and enhance the script to suit your specific requirements.

## TODO
Add Screenshots of working api's output





