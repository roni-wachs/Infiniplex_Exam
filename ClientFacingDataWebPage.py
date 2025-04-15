from flask import Flask, request, redirect, url_for
import pandas as pd
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Database setup
DATABASE = 'patients.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS patient_data
                 (patient_id TEXT, outcome TEXT, timestamp TEXT, archived BOOLEAN DEFAULT 0)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    sort_by = request.args.get('sort_by', 'patient_id')  # Default sorting by Patient ID
    sort_order = request.args.get('sort_order', 'ASC')  # Default order is ascending
    
    # Validate sort order and sort by columns
    if sort_by not in ['patient_id', 'timestamp'] or sort_order not in ['ASC', 'DESC']:
        return "Invalid sorting parameters.", 400

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    query = f"SELECT * FROM patient_data WHERE archived = 0 ORDER BY {sort_by} {sort_order}, timestamp DESC"
    c.execute(query)
    data = c.fetchall()
    conn.close()
    
    # Mark old outcomes as archived for each patient
    processed_data = []
    last_patient_id = None
    for row in data:
        if row[0] != last_patient_id:
            processed_data.append(row)
            last_patient_id = row[0]
        else:
            processed_data.append(row)  # Archived rows should be shown with strike-through
    
    # Print the data to the console (instead of rendering HTML)
    print("Patient Data (sorted by", sort_by, "and", sort_order, "):")
    for row in processed_data:
        print(row)
    
    return "Check the console for the patient data.", 200

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    
    if not file or not file.filename.endswith('.csv'):
        return 'Error: Please upload a valid CSV file.', 400
    
    # Process CSV file
    try:
        df = pd.read_csv(file)
        
        if 'Patient ID' not in df.columns or 'Outcome' not in df.columns:
            return 'Error: CSV must contain "Patient ID" and "Outcome" columns.', 400
        
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Process each row in the CSV and archive old outcomes if the patient already exists
        for index, row in df.iterrows():
            patient_id = row['Patient ID']
            outcome = row['Outcome']
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Archive the old outcome if the patient already exists
            c.execute('''UPDATE patient_data SET archived = 1 WHERE patient_id = ? AND archived = 0''', (patient_id,))
            
            # Insert the new outcome
            c.execute("INSERT INTO patient_data (patient_id, outcome, timestamp, archived) VALUES (?, ?, ?, ?)", 
                      (patient_id, outcome, timestamp, 0))
        
        conn.commit()
        conn.close()
        
        return redirect(url_for('index'))
    
    except Exception as e:
        return f'Error: {str(e)}', 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True)