import os
import sys


def get_template_dir() -> str:
    if getattr(sys, "frozen", False):
        # Running as a PyInstaller bundle
        template_dir = os.path.join(sys._MEIPASS, "src", "templates")
    else:
        # Running in development
        template_dir = os.path.join(os.path.dirname(__file__), "templates")

    return template_dir
