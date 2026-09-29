import pyautogui
import pyperclip
import time
from datetime import datetime


# -----------------------------------
# 1. Get today's date and time
# -----------------------------------

now = datetime.now()

date = now.strftime("%Y-%m-%d")
date_time = now.strftime("%d-%m-%Y %H:%M")

print("Today's date and time:", date_time)


# -----------------------------------
# 2. Open Chrome
# -----------------------------------

print("Opening Chrome...")

pyautogui.hotkey("win", "r")
time.sleep(2)

pyautogui.write("chrome")
pyautogui.press("enter")

time.sleep(5)


# -----------------------------------
# 3. Open a public weather website
# -----------------------------------

print("Opening weather website...")

pyautogui.hotkey("ctrl", "l")

pyautogui.write(
    "https://www.google.com/search?q=weather+in+Udumalpet"
)

pyautogui.press("enter")

time.sleep(5)


# -----------------------------------
# 4. Copy the temperature
# -----------------------------------

print("Getting temperature...")

# Move to the weather information area.
# These coordinates may need small adjustment
# depending on your screen.

pyautogui.click(500, 300)

time.sleep(1)

# Use keyboard navigation to select text
pyautogui.hotkey("ctrl", "a")

time.sleep(1)

# Copy the page text
pyautogui.hotkey("ctrl", "c")

time.sleep(1)

page_text = pyperclip.paste()


# Find temperature from the copied text
temperature = ""

lines = page_text.split("\n")

for line in lines:

    if "°C" in line:

        temperature = line.strip()
        break


# If temperature was not found
if temperature == "":
    temperature = "Temperature not found"


print("Temperature:", temperature)


# -----------------------------------
# 5. Open Microsoft Excel
# -----------------------------------

print("Opening Microsoft Excel...")

pyautogui.hotkey("win", "r")
time.sleep(2)

pyautogui.write("excel")
pyautogui.press("enter")

time.sleep(7)


# -----------------------------------
# 6. Create a new Excel workbook
# -----------------------------------

print("Creating new Excel workbook...")

pyautogui.hotkey("ctrl", "n")

time.sleep(3)


# -----------------------------------
# 7. Create column headings
# -----------------------------------

pyautogui.write("Date & Time")

pyautogui.press("tab")

pyautogui.write("Weather")

pyautogui.press("tab")

pyautogui.write("Comment")

pyautogui.press("enter")


# -----------------------------------
# 8. Create today's report row
# -----------------------------------

# Date and time
pyautogui.write(date_time)

pyautogui.press("tab")


# Temperature
pyautogui.write(temperature)

pyautogui.press("tab")


# Comment
pyautogui.write("Good for outdoor activities")


# -----------------------------------
# 9. Save the Excel file
# -----------------------------------

print("Saving Excel file...")

file_name = "daily_report_" + date + ".xlsx"

pyautogui.hotkey("ctrl", "s")

time.sleep(3)

pyautogui.hotkey("ctrl", "a")

pyautogui.write(file_name)

pyautogui.press("enter")

time.sleep(5)

# If Excel asks about file format
pyautogui.press("enter")

time.sleep(3)


# -----------------------------------
# 10. Take screenshot of Excel
# -----------------------------------

print("Taking screenshot...")

screenshot_name = "daily_report_" + date + ".png"

screenshot = pyautogui.screenshot()

screenshot.save(screenshot_name)


# -----------------------------------
# 11. Finish
# -----------------------------------

print("-----------------------------------")
print("Daily report completed successfully!")
print("-----------------------------------")

print("Date and Time:", date_time)
print("Weather:", temperature)
print("Excel File:", file_name)
print("Screenshot:", screenshot_name)
