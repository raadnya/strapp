import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
from datetime import date

# Utility functions for login and signup
def load_credentials():
    if os.path.exists('credentials.json'):
        with open('credentials.json', 'r') as file:
            return json.load(file)
    return {}

def save_credentials(credentials):
    with open('credentials.json', 'w') as file:
        json.dump(credentials, file)

def signup_user(name, phone, dob, email, password):
    credentials = load_credentials()
    
    # Convert date to string before saving
    dob_str = dob.strftime('%Y-%m-%d')
    
    if email in credentials:
        st.warning("User with this email already exists!")
    else:
        credentials[email] = {
            'name': name,
            'phone': phone,
            'dob': dob_str,  # Save date as a string
            'password': password
        }
        save_credentials(credentials)
        os.makedirs(email, exist_ok=True)
        st.success("Signup successful! You can now login.")

def validate_login(email, password):
    credentials = load_credentials()
    if email in credentials and credentials[email]['password'] == password:
        return True, credentials[email]['name']
    return False, None

def save_marks(email, subjects, marks):
    data = {"Subject": subjects, "Marks": marks}
    df = pd.DataFrame(data)
    df.to_csv(f"{email}/marks.csv", index=False)
    st.success("Marks saved successfully!")

def generate_reports(email):
    file_path = f"{email}/marks.csv"
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        
        # Bar chart for average marks
        avg_marks = df['Marks'].mean()
        fig_bar = px.bar(df, x='Subject', y='Marks', title='Marks per Subject')
        st.plotly_chart(fig_bar)
        
        # Line chart
        fig_line = px.line(df, x='Subject', y='Marks', title='Marks Line Chart')
        st.plotly_chart(fig_line)
        
        # Pie chart
        fig_pie = px.pie(df, values='Marks', names='Subject', title='Marks Distribution')
        st.plotly_chart(fig_pie)
    else:
        st.error("No marks found. Please enter your marks first.")

# Initialize session state for login
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""
if 'email' not in st.session_state:
    st.session_state['email'] = ""

# Main Streamlit App
st.title("Student Marks Management")

menu = ["Login", "Sign Up"]
choice = st.sidebar.selectbox("Menu", menu)

# Sign Up Page
if choice == "Sign Up":
    st.subheader("Create a New Account")
    name = st.text_input("Name")
    phone = st.text_input("Phone")
    dob = st.date_input("Date of Birth", max_value=date.today())
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Sign Up"):
        signup_user(name, phone, dob, email, password)

# Login Page
elif choice == "Login":
    if not st.session_state['logged_in']:
        st.subheader("Login to Your Account")
        
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            valid, username = validate_login(email, password)
            
            if valid:
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.session_state['email'] = email
                st.success(f"Welcome {username}!")

                # Check if marks file exists and generate reports
                if os.path.exists(f"{email}/marks.csv"):
                    generate_reports(email)  # Automatically generate reports on login
            else:
                st.error("Invalid credentials. Please try again.")

# If user is logged in, show the main app
if st.session_state['logged_in']:
    st.subheader(f"Welcome, {st.session_state['username']}")
    
    # Marks input section
    st.subheader("Enter Your Marks")
    subjects = []
    marks = []
    
    for i in range(7):
        subject = st.text_input(f"Subject {i+1}", key=f"subject_{i}")
        mark = st.slider(f"Marks for {subject}", 0, 100, 50, key=f"mark_{i}")
        
        if subject:
            subjects.append(subject)
            marks.append(mark)
    
    if st.button("Submit Marks"):
        save_marks(st.session_state['email'], subjects, marks)
    
    # Generate report button
    st.subheader("Your Reports")
    if st.button("Generate Report"):
        generate_reports(st.session_state['email'])
    
    # Sign out button
    if st.button("Sign Out"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = ""
        st.session_state['email'] = ""
        st.success("You have been signed out.")
