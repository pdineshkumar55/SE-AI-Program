
def calculate_grade(score):
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "E"

while True:
    raw = input("Enter the Mark (0-100): ").strip()
    try:
        score = float(raw)
    except ValueError:
        print(f"'{raw}' is not a number. Please try again.")
        continue

    if not 0 <= score <= 100:
        print(f"'{score:g}' is not A valid score. Please enter a number between 0 and 100.")
        continue

    grade = calculate_grade(score)
    print(f"Mark: {score:g} -> Grade: {grade}")
    break
