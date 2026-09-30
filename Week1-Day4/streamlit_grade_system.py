import streamlit as st

st.title("Student Grade System")

mark = st.number_input(
    "Enter your mark (0 - 100):",
    min_value=0.0,
    max_value=100.0,
    value=None
)

if mark is not None:

    if mark >= 90:
        grade = "A"
    elif mark >= 80:
        grade = "B"
    elif mark >= 70:
        grade = "C"
    elif mark >= 60:
        grade = "D"
    else:
        grade = "E"

    st.write("Your mark:", mark)
    st.write("Your grade:", grade)