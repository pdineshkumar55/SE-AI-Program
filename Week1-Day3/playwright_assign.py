import asyncio
import csv
import json
import random
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
from playwright.async_api import async_playwright


# -----------------------------------------
# File names
# -----------------------------------------

today = datetime.now().strftime("%Y-%m-%d")

json_file = "whatsapp_report_" + today + ".json"
excel_file = "whatsapp_report_" + today + ".xlsx"

contact_file_name = "contacts.csv"

# Look next to this script first, then in the folder you run it from
script_dir = Path(__file__).resolve().parent

contact_file = next(
    (p for p in [script_dir / contact_file_name, Path.cwd() / contact_file_name] if p.exists()),
    script_dir / contact_file_name
)


# -----------------------------------------
# Random delay
# -----------------------------------------

async def random_delay():

    seconds = random.randint(2, 5)

    print("Waiting", seconds, "seconds...")

    await asyncio.sleep(seconds)


# -----------------------------------------
# Read contacts.csv
# -----------------------------------------

def read_contacts():

    contacts = []

    if not contact_file.exists():
        raise FileNotFoundError(
            "Could not find " + contact_file_name
            + " in " + str(script_dir) + " or " + str(Path.cwd())
        )

    print("Reading contacts from:", contact_file)

    # utf-8-sig handles the BOM that Excel adds when saving CSV
    with open(contact_file, "r", encoding="utf-8-sig") as file:

        reader = csv.DictReader(file)

        for row in reader:

            phone = row["Phone"].strip()

            # Excel turns long numbers into 9.1638E+11 and drops digits
            if "E+" in phone.upper():
                raise ValueError(
                    "Phone for " + row["Name"] + " is in scientific notation ("
                    + phone + "). Re-type the full number in contacts.csv."
                )

            contacts.append({
                "name": row["Name"],
                "phone": phone,
                "message": row["Message"]
            })

    return contacts


# -----------------------------------------
# Close WhatsApp "What's new" popup
# -----------------------------------------

def get_search_box(page):

    # WhatsApp changes this label between versions
    # ("Search or start new chat" / "Search or start a new chat"),
    # so match loosely and fall back to the old CSS selector
    return (
        page.get_by_role("textbox", name=re.compile("search", re.I))
        .or_(page.locator('div[contenteditable="true"][data-tab="3"]'))
    ).first


def get_message_box(page):

    return (
        page.get_by_role("textbox", name=re.compile("type a message", re.I))
        .or_(page.locator('footer div[contenteditable="true"]'))
    ).first


async def close_whatsapp_popup(page):

    print("Checking for WhatsApp popup...")

    # The popup title - used to detect and confirm the popup is gone
    # (WhatsApp uses a curly apostrophe in "What’s", so match the rest)
    popup_title = page.get_by_text("new on WhatsApp Web")

    # WhatsApp's "Continue" is often a div/span, not a real <button>,
    # so try several ways of finding it
    continue_button = (
        page.get_by_role("button", name="Continue")
        .or_(page.get_by_text("Continue", exact=True))
    ).first

    try:

        # The popup can appear a few seconds after the chat list loads
        await continue_button.wait_for(
            state="visible",
            timeout=20000
        )

    except Exception:

        print("No popup found.")

        return

    print("WhatsApp popup found.")

    try:

        await continue_button.click()

    except Exception as error:

        print("Could not click Continue:", error)

        # Fallback: Escape usually closes WhatsApp dialogs
        await page.keyboard.press("Escape")

    try:

        await popup_title.wait_for(
            state="hidden",
            timeout=5000
        )

        print("Popup closed.")

    except Exception:

        print("Popup still open, pressing Escape...")

        await page.keyboard.press("Escape")

    await page.wait_for_timeout(2000)

    return


# -----------------------------------------
# Send WhatsApp message
# -----------------------------------------

async def send_message(page, contact):

    name = contact["name"]
    phone = contact["phone"]

    message_template = contact["message"]

    # Replace {name}
    message = message_template.replace(
        "{name}",
        name
    )

    print("--------------------------------")
    print("Processing:", name)
    print("Phone:", phone)
    print("Message:", message)

    try:

        # ---------------------------------
        # Find search box
        # ---------------------------------

        # Clear any search left over from the previous contact.
        # (While the search box has text, its "Search..." label
        # disappears and the locator can't find it.)
        await page.keyboard.press("Escape")
        await page.keyboard.press("Escape")

        search_box = get_search_box(page)

        await search_box.wait_for(
            state="visible",
            timeout=15000
        )

        # Click search box
        await search_box.click()

        # From here use the keyboard, not the locator:
        # once text is typed the locator no longer matches
        await page.keyboard.press("Control+A")
        await page.keyboard.press("Backspace")

        # Enter phone number
        await page.keyboard.type(phone, delay=50)

        await random_delay()


        # ---------------------------------
        # Open contact
        # ---------------------------------

        await page.keyboard.press("Enter")

        await page.wait_for_timeout(3000)


        # ---------------------------------
        # Find message box
        # ---------------------------------

        message_box = get_message_box(page)

        await message_box.wait_for(
            state="visible",
            timeout=15000
        )


        # ---------------------------------
        # Type message
        # ---------------------------------

        await message_box.click()

        # Same issue as the search box: the "Type a message" label
        # disappears once text is typed, so use the keyboard
        await page.keyboard.type(message, delay=30)

        await random_delay()


        # ---------------------------------
        # Send message
        # ---------------------------------

        await page.keyboard.press("Enter")

        print("Message sent.")

        await page.wait_for_timeout(3000)


        # ---------------------------------
        # Take screenshot
        # ---------------------------------

        screenshot_name = (
            "sent_"
            + name.replace(" ", "_")
            + "_"
            + today
            + ".png"
        )

        await page.screenshot(
            path=screenshot_name
        )

        print(
            "Screenshot saved:",
            screenshot_name
        )


        # ---------------------------------
        # Extract last 3 messages
        # ---------------------------------

        messages = []

        try:

            message_elements = await page.locator(
                '[data-testid="msg-container"]'
            ).all_inner_texts()

            messages = message_elements[-3:]

        except:

            print("Could not extract messages.")


        # ---------------------------------
        # Return result
        # ---------------------------------

        return {
            "name": name,
            "phone": phone,
            "message": message,
            "status": "Sent",
            "time": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "screenshot": screenshot_name,
            "last_3_messages": messages
        }


    except Exception as error:

        print("Message failed.")

        print("Error:", error)

        return {
            "name": name,
            "phone": phone,
            "message": message,
            "status": "Failed",
            "time": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "screenshot": "",
            "last_3_messages": [],
            "error": str(error)
        }


# -----------------------------------------
# Main program
# -----------------------------------------

async def main():

    print("--------------------------------")
    print("WhatsApp Automation Bot")
    print("--------------------------------")


    # ---------------------------------
    # Read contacts
    # ---------------------------------

    contacts = read_contacts()

    print(
        "Number of contacts:",
        len(contacts)
    )


    # ---------------------------------
    # Start Playwright
    # ---------------------------------

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=False
        )

        page = await browser.new_page()


        # ---------------------------------
        # Open WhatsApp Web
        # ---------------------------------

        print("Opening WhatsApp Web...")

        await page.goto(
            "https://web.whatsapp.com"
        )


        # ---------------------------------
        # Manual QR login
        # ---------------------------------

        print("--------------------------------")
        print("If QR code appears, scan it")
        print("using WhatsApp on your phone.")
        print("--------------------------------")


        # Wait until EITHER the search box OR the popup shows up.
        # While the popup is open, the search box is hidden from
        # get_by_role, so waiting only for it would time out.
        search_box = get_search_box(page)

        popup_title = page.get_by_text("new on WhatsApp Web")

        await search_box.or_(popup_title).first.wait_for(
            state="visible",
            timeout=120000
        )


        print("WhatsApp Web is ready.")


        # ---------------------------------
        # IMPORTANT:
        # Close What's New popup
        # ---------------------------------

        await close_whatsapp_popup(page)


        # Wait again for search box
        await search_box.wait_for(
            state="visible",
            timeout=30000
        )


        print("Ready to send messages.")


        # ---------------------------------
        # Process contacts
        # ---------------------------------

        report = []


        for contact in contacts:

            result = await send_message(
                page,
                contact
            )

            report.append(result)


            # Wait before next contact
            await random_delay()


        # ---------------------------------
        # Save JSON report
        # ---------------------------------

        with open(
            json_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                report,
                file,
                indent=4,
                ensure_ascii=False
            )


        print(
            "JSON report saved:",
            json_file
        )


        # ---------------------------------
        # Save Excel report
        # ---------------------------------

        dataframe = pd.DataFrame(report)

        dataframe.to_excel(
            excel_file,
            index=False
        )


        print(
            "Excel report saved:",
            excel_file
        )


        # ---------------------------------
        # Keep browser open briefly
        # ---------------------------------

        await page.wait_for_timeout(5000)

        await browser.close()


    print("--------------------------------")
    print("Automation completed!")
    print("--------------------------------")


# -----------------------------------------
# Start program
# -----------------------------------------

if __name__ == "__main__":

    asyncio.run(main())