from flask import Flask, request, redirect, url_for, render_template
import pandas as pd
import sqlite3
from datetime import datetime

app = Flask(__name__)
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
    sort_by = request.args.get('sort_by', 'patient_id')
    sort_order = request.args.get('sort_order', 'ASC')

    if sort_by not in ['patient_id', 'timestamp'] or sort_order not in ['ASC', 'DESC']:
        return "Invalid sorting parameters.", 400

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute(f'''
        SELECT patient_id, outcome, timestamp, archived
        FROM patient_data
        ORDER BY {sort_by} {sort_order}, timestamp DESC
    ''')
    data = c.fetchall()
    conn.close()

    return render_template('index.html', data=data)

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')

    if not file or not file.filename.endswith('.csv'):
        return 'Error: Please upload a valid CSV file.', 400

    try:
        df = pd.read_csv(file)

        if 'Patient ID' not in df.columns or 'Outcome' not in df.columns:
            return 'Error: CSV must contain "Patient ID" and "Outcome" columns.', 400

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()

        for _, row in df.iterrows():
            patient_id = row['Patient ID']
            outcome = row['Outcome']
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            c.execute('UPDATE patient_data SET archived = 1 WHERE patient_id = ? AND archived = 0', (patient_id,))
            c.execute('INSERT INTO patient_data (patient_id, outcome, timestamp, archived) VALUES (?, ?, ?, ?)',
                      (patient_id, outcome, timestamp, 0))

        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    except Exception as e:
        return f'Error: {str(e)}', 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
