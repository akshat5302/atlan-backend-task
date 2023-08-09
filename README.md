# Approach / Idea after reading Daisy challenge task

## Optimizing Employee Experience and Operations

Why - After reading Daisy Challenge, I came up with this concept because I had been personally faced with such manual tasks carried out by individuals in small or mid-size companies that are not geared to automate manual jobs or rely on new ML approaches to ease and streamline the workflow in organizations.

What - In this task I tried to cover examples given in daisy-challenge and prepared APIs for each one of them to reduce manual work and somewhat automate manual stuff done in the company by calling their respective APIs

How

These 4 tasks are the high-level idea I get after reading Daisy's challenge examples

## Task 1: Detecting Slangs from Employees' Feedback

Why - Nowadays people use chatgpt to fill in responses and responses given by chatgpt are long and so instead of reading the whole feedback from employees we can get slang from the sentences and detect the moto of employees according to slang

Also later on we can embed ML approaches and tools to better understand the sentiments of employees using various sentiment analysis tools 

What - For this I created an API `slang-detect` which will give slang from sentences(employee_feedback).

How - We have created a separate DB of slang which gets updated with new slang words according to us. Now when we call the `slang-detect` API it searches that word in `slang-db` and gives the list of slang words

Pros - Removing Manual work of reading feedback

Cons - Maintaining `slang-db` is a huge task. For better optimization, we can use the ML sentiment analysis tools and APIs

## Task 2: Validating Employees' Responses

Why - This task is important because many employees fill out forms in a hurry or with laziness. They don't fill the form with the correct information

What - For this I created an API `flagged-employees` that check responses and flag the employees

How - For this demo I took care of two things - 

i. `employee_salary > average_expense` in that case he is entering false values in either one of the two columns.

ii. Enter less than 10 digits in ph no. 

If any of these things happen API will show the `name_of_employee` and `response` he filled incorrectly and create a separate CSV file of `flagged-employees` for that.

Pros - Detecting employees who filled in wrong responses and eliminating manual checking of `employees_info`.

Cons - Not optimized approach Doing this thing with a linear search approach takes a long time and complexity

## Task 3: Transferring Employees Database to CSV

Why - Databases are hard to analyze and study we need more visuals than boring tables with rows and columns

What - We are transferring data into a CSV file by calling `transfer-db-to-csv` 

How - By calling API we run a loop on DB Tables and create CSV Files for each table in the DB

Pros - CSV files are general-purpose files that we can use and integrate with ML as well to do ML operations on data 
Also, we can transfer them to google sheets to better visualize the data using graphs and dashboards provided by google sheets

Cons - No as such con IMO. Maybe we can directly transfer data to google sheets but I don't have access to Google Sheets API so I implemented CSV Method

## Task 4: Sending Onboarding Messages to New Employees

Why - It's a great way to welcome and greet new employees with some message and it should be automated because the company hires a lot of employees 

What - We have created an API `onboard-message` to send a welcome message to new employees

How - We maintain a table named `new-employees` and then `onboard-message` to every new employee from the `new-employee` table

Pros - Removed manual work of writing SMS to new employees.

Cons - API sends SMS to every person in the table so we need to remove persons whom we sent onboard message from the list in order not to send SMS to the same person again

Also, I haven't implemented the mail part as I was not able to enable the mail service in Python


## Prerequisites

Before using atlan_task.py script, make sure you have the following components set up:

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

2. /detect-slangs Endpoint: This endpoint exposes an API that retrieves employee feedback texts from the employee_feedback table in the database. For each feedback, it uses the detect_slangs function to detect any slang present in the feedback. If slang is detected, the feedback's ID, the original feedback text, and the detected slang are stored in a list. The list is returned as the API response.

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

This Python script provides a web API endpoint for transferring data from a database to CSV files. The code is implemented using the FastAPI framework and assumes a connection to a database. When the `/transfer-db-to-csv` endpoint is accessed, it retrieves data from three different database tables: `employee_feedback`, `employees_info`, and `new_employees`, and then writes the data to correspond CSV files.

1. Function to search table in DB and create CSV for them
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
1. Add Screenshots of working api's output
2. Add DB schema structure





