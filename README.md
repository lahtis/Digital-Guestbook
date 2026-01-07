**Digital Guestbook** A sleek, lightweight, and localizable digital guestbook built with Python and Flet. This application is designed for tablets or kiosks where guests can leave messages. It supports multiple languages, dark mode, and easy configuration.

## Key Features
* **Fast & Lightweight:** Built on Flet (Flutter for Python), starts instantly.
* **Auto-Learning Localization:** Supports English (default) and Finnish. Automatically adds missing keys to translation files.
* **Portable Configuration:** Generates a config.conf file on the first run for easy customization.
* **Secure Admin Access:** Protect guestbook management with an admin password.
* **Database:** Uses a local SQLite database (data.db) for message storage.
* **Theming:** Built-in support for Dark and Light modes.


## Getting Started
**1. Prerequisites:**
```text
Python 3.9+
Flet 0.27.1
```

### 2. Basic Usage
```bash
python "Digital Guestbook.py"
```

### 3. Installation
Clone the repository:
```bash
pip install -r requirements.txt
```

## Project Structure
```text
|── Digital Guestbook.py              # Main program Windows and Linux environments.
├── modules/                       		# Modules
│   ├── localization.py             	# Automatic loacalization engine
│
├── assets/                       		# Assets
│   ├── DigitalGuestbook.ico          # The application icon.  
│   └── DigitalGuestbook.png          # The application logo.
│
├── locales/                       		# Assets
│   ├── lang_en.json                  # English locales
│   └── lang_fi.json                  # Finnish locales
├── config.json            			      # Configuration file
├── data.db                     			# SQlite database
├── LISENCE.md                   			# GPLv3 lisence
├── README.md                     		# readme.md
├── requirements.txt            			# requirements
│
```

## Version History
   * v0.1: Initial release, basic file operations.
---
## License & Credits
* **Author:** Tuomas Lähteenmäki
* **License:** GNU GPLv3
---
*Developed for the flow of coding.*
