** Digital Guestbook ** A sleek, lightweight, and localizable digital guestbook built with Python and Flet. This application is designed for tablets or kiosks where guests can leave messages. It supports multiple languages, dark mode, and easy configuration.

## Key Features
* **Fast & Lightweight:** Built on Flet (Flutter for Python), starts instantly.
* **Auto-Learning Localization:** Supports English (default) and Finnish. Automatically adds missing keys to translation files.
* **Portable Configuration:** Generates a config.conf file on the first run for easy customization.
* **Secure Admin Access:** Protect guestbook management with an admin password.
* **Database:** Uses a local SQLite database (data.db) for message storage.
* **Theming:** Built-in support for Dark and Light modes.

## Getting Started
1. **Prerequisites:**
   * Python 3.9 or newer
   * Flet 0.27.1

### 1. Basic Usage
Simply run the script with Python:
```bash
python "Digital Guestbook.py
´´´
### 2. Installation
Clone the repository:
```bash
pip install -r requirements.txt
´´´

## Project Structure
   * ```Digital Guestbook.py```       : Main program Windows and Linux environments.
   *    modules/localization.py       : Automatic loacalization engine
   * ```assets/DigitalGuestbook.ico```: The application icon.
   *    assets/DigitalGuestbook.png```: The application icon/png```.
   *    /locales/lang_en.json         : English locales
   *    /locales/lang_fi.json         : Finnish locales
   *    config.json                   : Configuration file
   *    data.db                       : sqlite database
   *    LISENCE.md                    : GPLv3 lisence
   *    README.md                      :readme.md

---
## Version History
   * v0.1: Initial release, basic file operations.

## License & Credits
   * Author: Tuomas Lähteenmäki
   * License: GNU GPLv3 - Free to use, modify, and distribute.
---
Developed for the flow of coding.