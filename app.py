from flask import Flask, render_template, request
import subprocess
import logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home():
    return render_template('deaf.html')

@app.route('/start.html')
@app.route('/start')
def start():
    logging.info("Running the inference classifier script...")
    result = subprocess.run(
        ['python', r'C:\Users\Subhobroto Sasmal\Downloads\DeafTech---SignLanguageDetector-main\DeafTech---SignLanguageDetector-main\Backend\app69.py'], 
        capture_output=True, 
        text=True
    )
    logging.info(f"Script output: {result.stdout}")
    logging.error(f"Script error (if any): {result.stderr}")
    
    if result.returncode != 0:
        return render_template('start.html', message=f"Error: {result.stderr}")

    return render_template('deaf.html')

@app.route('/contact.html')
@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/faq.html')
@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/signin.html')
@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route('/login.html')
@app.route('/login')
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
