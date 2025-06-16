import os


APP_MODE = os.environ.get("APP_MODE", "notify")
if APP_MODE in ["notify"]:
    SMTP_SERVER = os.environ["SMTP_SERVER"]
    SMTP_PORT = os.environ["SMTP_PORT"]
    SMTP_USERNAME = os.environ["SMTP_USERNAME"]
    SMTP_PASSWORD = os.environ["SMTP_PASSWORD"]
    FROM_EMAIL = os.environ["FROM_EMAIL"]
    TO_EMAIL = os.environ["TO_EMAIL"]
