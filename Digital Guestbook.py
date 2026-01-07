# -*- coding: utf-8 -*-
"""
Digital Guestbook.py 
Author: Tuomas Lähteenmäki
Version: 0.1
License: GNU GPLv3

Description: A sleek, lightweight, and localizable digital guestbook 
built with Python and Flet. This application is designed for 
tablets or kiosks where guests can leave messages. 
It supports multiple languages, dark mode, and easy configuration.
"""
import flet as ft
import configparser
import json
import sys
import os
import sqlite3

from modules.localization import Localizer
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- 1. RAJAPINTA (Säännöt tallennukselle) ---
class StorageProvider:
    def tallenna(self, viesti): raise NotImplementedError
    def lue_kaikki(self): raise NotImplementedError

# --- 2. JSON-TOTEUTUS ---
class JSONStorage(StorageProvider):
    def __init__(self, tiedosto="data.json"):
        self.tiedosto = tiedosto

    def lue_rivi(self, indeksi):
        data = self.lue_kaikki()
        try:
            return data[indeksi] # JSONissa ei ole kiinteitä ID-numeroita ellet tee niitä itse
        except IndexError:
            return None

    def lue_kaikki(self):
        if not os.path.exists(self.tiedosto): return []
        with open(self.tiedosto, "r") as f:
            return json.load(f)

    def tallenna(self, viesti):
        data = self.lue_kaikki()
        data.append({"viesti": viesti})
        with open(self.tiedosto, "w") as f:
            json.dump(data, f)

# --- 3. SQLITE-TOTEUTUS ---
class SQLiteStorage(StorageProvider):
    def __init__(self, db_nimi="data.db"):
        self.db_nimi = db_nimi
        self._luo_taulu()

    def _luo_taulu(self):
        with sqlite3.connect(self.db_nimi) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS loki (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    viesti TEXT,
                    lisatty_pvm DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def lue_rivi(self, kohde_id):
        with sqlite3.connect(self.db_nimi) as conn:
            cursor = conn.execute("SELECT id, viesti FROM loki WHERE id = ?", (kohde_id,))
            rivi = cursor.fetchone() # Hakee vain yhden rivin
            if rivi:
                return {"id": rivi[0], "viesti": rivi[1]}
            return None

    def lue_viimeisin(self):
        with sqlite3.connect(self.db_nimi) as conn:
            # Järjestetään ID:n mukaan laskevasti ja otetaan ensimmäinen
            cursor = conn.execute("SELECT id, viesti FROM loki ORDER BY id DESC LIMIT 1",)
            rivi = cursor.fetchone()
            if rivi:
                return {"id": rivi[0], "viesti": rivi[1]}
            return None

    def lue_kaikki(self):
        with sqlite3.connect(self.db_nimi) as conn:
            cursor = conn.execute("SELECT id, viesti FROM loki")
            # Palautetaan nyt myös ID:t
            return [{"id": r[0], "viesti": r[1]} for r in cursor.fetchall()]

    def tallenna(self, viesti):
        with sqlite3.connect(self.db_nimi) as conn:
            conn.execute("INSERT INTO loki (viesti) VALUES (?)", (viesti,))

    def poista(self, kohde_id):
        """Uusi toiminto: poistaminen ID:n perusteella"""
        with sqlite3.connect(self.db_nimi) as conn:
            conn.execute("DELETE FROM loki WHERE id = ?", (kohde_id,))

    def poista_yksittainen(self, kohde_id):
        with sqlite3.connect(self.db_nimi) as conn:
            conn.execute("DELETE FROM loki WHERE id = ?", (kohde_id,))

    def tyhjenna_kaikki(self):
        with sqlite3.connect(self.db_nimi) as conn:
            conn.execute("DELETE FROM loki")
            # Valinnainen: nollataan myös AUTOINCREMENT-laskuri
            conn.execute("DELETE FROM sqlite_sequence WHERE name='loki'")

    def etsi_viestit(self, hakusana):
        with sqlite3.connect(self.db_nimi) as conn:
            # %-merkit hakusanan ympärillä tarkoittavat "mitä tahansa tekstiä ennen tai jälkeen"
            hakutermi = f"%{hakusana}%"
            cursor = conn.execute(
                "SELECT id, viesti FROM loki WHERE viesti LIKE ?",
                (hakutermi,)
            )
            return [{"id": r[0], "viesti": r[1]} for r in cursor.fetchall()]

    def paivita_viesti(self, kohde_id, uusi_teksti):
        with sqlite3.connect(self.db_nimi) as conn:
            conn.execute(
                "UPDATE loki SET viesti = ? WHERE id = ?",
                (uusi_teksti, kohde_id)
            )


# --- 4. BACKEND (Daemon-logiikka) ---
class BackendDaemon:
    def __init__(self, tapa="sqlite", localizer=None):
        # Tässä valitaan, kumpaa käytetään
        if tapa == "sqlite":
            self.storage = SQLiteStorage()
        else:
            self.storage = JSONStorage()
        self.loc = localizer if localizer else Localizer()

    def lisaa_dataa(self, teksti):
        self.storage.tallenna(teksti)
        return self.loc.L("saved_msg", "Saved ({}): {}").format(self.storage.__class__.__name__, teksti)

    def hae_yksittäinen(self, kohde_id):
        data = self.storage.lue_rivi(kohde_id) # Olettaen että lisäsit lue_rivi-metodin
        if data:
            return self.loc.L("found_msg", "Fetched content: {}").format(data['viesti'])

    def hae_dataa(self, hakusana):
        if not hakusana:
            return self.storage.lue_kaikki()
        return self.storage.etsi_viestit(hakusana)

    def muokkaa_viestia(self, kohde_id, uusi_teksti):
        self.storage.paivita_viesti(kohde_id, uusi_teksti)
        return self.loc.L("update_success_msg", "Message {} is updated.").format(kohde_id)

    def poista_rivi(self, kohde_id):
        self.storage.poista_yksittainen(kohde_id)
        return self.loc.L("line_msg", "line {} has been removed").format(kohde_id)

    def tyhjenna_data(self):
        self.storage.tyhjenna_kaikki()
        return self.loc.L("db_cleared_msg", "Database cleared.")

def main(page: ft.Page):
    # 1. TUNNISTETAAN POLKU (EXE vs SKRIPTI)
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    # 2. MÄÄRITETÄÄN TIEDOSTOPOLUT
    db_path = os.path.join(base_path, "data.db")
    config_path = os.path.join(base_path, "config.conf")
    
    page.title = "Digital Guestbook"
    
    # Alustetaan lokalisointi
    loc = Localizer()
    
    # Passataan db_path Backendille
    # Muista muuttaa BackendDaemon tai SQLiteStorage ottamaan tämä polku vastaan
    be = BackendDaemon(tapa="sqlite") 
    # (Vinkki: Voit muuttaa SQLiteStorage(db_nimi=db_path))
    
    base_path = os.path.dirname(os.path.realpath(__file__))
    icon_path = os.path.join(base_path, "assets", "DigitalGuestbook.ico")
    page.title = "Digital Guestbook"
    page.update()

    # Voit vaihtaa tästä "json" tai "sqlite"
    be = BackendDaemon(tapa="sqlite")
    muokattava_id = None
    poistettava_id_nyt = None

    # Salasanakenttä dialogia varten
    admin_password = ft.TextField(
    label=loc.L("password_label", "Password"),
    password=True,
    can_reveal_password=True)

    # ASETUSTEN LUKU (config.conf)
    config = configparser.ConfigParser()
    if not os.path.exists('config.conf'):
        config['SETTINGS'] = {'password': '1234', 'theme': 'dark', 'language': 'en'}
        with open('config.conf', 'w') as f: config.write(f)
    config.read('config.conf')

    admin_config_password = config.get('SETTINGS', 'password', fallback='1234')
    lang_code = config.get('SETTINGS', 'language', fallback='en')
    page.theme_mode = ft.ThemeMode.DARK if config.get('SETTINGS', 'theme') == 'dark' else ft.ThemeMode.LIGHT

    def tarkista_salasana_ja_tyhjenna(e):
        if admin_password.value == admin_config_password:
            info_text.value = be.tyhjenna_data()
            päivitä_lista()
            tyhjenna_varmistus_dialogi.open = False
            admin_password.value = ""
        else:
            info_text.value = loc.L("wrong_password_msg", "Wrong password")
            info_text.color = "red"
        page.update()

    tyhjenna_varmistus_dialogi = ft.AlertDialog(
        title=ft.Text(loc.L("ConfirmDBdeletion_label", "Confirm database deletion")),
        content=ft.Column([
            ft.Text(loc.L("this_delete_all_messages_label", "This will permanently delete all messages.")),
            admin_password
        ], tight=True),
        actions=[
            ft.TextButton(loc.L("delete_btn", "Delete all"), on_click=tarkista_salasana_ja_tyhjenna, icon=ft.Icons.DELETE_FOREVER),
            ft.TextButton(loc.L("cancel_btn", "Cancel"), on_click=lambda _: setattr(tyhjenna_varmistus_dialogi, "open", False) or page.update()),
        ],
    )
    page.overlay.append(tyhjenna_varmistus_dialogi)
    # --- Tapahtumafunktiot ---

    def vahvista_poisto(kylla):
        nonlocal poistettava_id_nyt
        if kylla:
            info_text.value = be.poista_rivi(poistettava_id_nyt)
            päivitä_lista()
        poisto_dialogi.open = False
        page.update()

    def valitse_muokattavaksi(data):
        nonlocal muokattava_id
        muokattava_id = data['id']
        input_field.value = data['viesti']
        peruuta_nappi.visible = True
        tallenna_nappi.text = "Päivitä"
        info_text.value = loc.L("editing_row_msg", "Editing the line {}").format(muokattava_id)
        info_text.color = "amber"
        input_field.focus()
        page.update()

    def peruuta_muokkaus_evt(e):
        nonlocal muokattava_id
        muokattava_id = None
        input_field.value = ""
        peruuta_nappi.visible = False
        tallenna_nappi.text = loc.L("update_btn", "Update")
        info_text.value = loc.L("edit_cancel_msg", "Cancel edit")
        info_text.color = "blue"
        page.update()

    def tallenna_evt(e):
        nonlocal muokattava_id
        if input_field.value.strip():
            if muokattava_id is None:
                info_text.value = be.lisaa_dataa(input_field.value)
            else:
                info_text.value = be.muokkaa_viestia(muokattava_id, input_field.value)
                muokattava_id = None

            input_field.value = ""
            peruuta_nappi.visible = False
            tallenna_nappi.text = loc.L("save_btn", "Save")
            päivitä_lista()
        else:
            info_text.value = loc.L("empty_field_label", "The field is empty!")
            info_text.color = "red"
        page.update()

    def tyhjenna_haku_evt(e):
        haku_kentta.value = ""
        päivitä_lista()
        page.update()

    def tyhjenna_evt(e):
        admin_password.value = "" # Nollataan kenttä
        tyhjenna_varmistus_dialogi.open = True
        page.update()

    def poista_yksittainen_evt(rivi_id):
        nonlocal poistettava_id_nyt
        poistettava_id_nyt = rivi_id
        poisto_dialogi.open = True
        page.update()

    def päivitä_lista():
        viestilista.controls.clear()
        kaikki_data = be.hae_dataa(haku_kentta.value)
        for d in kaikki_data:
            rivi_id = d['id']
            viesti_data = d
            viestilista.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.EDIT_NOTE, color="amber"),
                    title=ft.Text(d['viesti'], color="white"),
                    subtitle=ft.Text(f"ID: {rivi_id}", color="bluegrey400"),
                    on_click=lambda e, data=viesti_data: valitse_muokattavaksi(data),
                    trailing=ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color="red700",
                        on_click=lambda e, rid=rivi_id: poista_yksittainen_evt(rid)
                    )
                )
            )
        page.update()

    # --- UI Komponentit ---


    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 450
    page.window_height = 500

    input_field = ft.TextField(label=loc.L("input_label", "Message"), on_submit=tallenna_evt)
    info_text = ft.Text(loc.L("ready_msg", "Ready"), color="blue")
    viestilista = ft.ListView(expand=1, spacing=10, padding=10)

    poisto_dialogi = ft.AlertDialog(
        modal=True,
        title=ft.Text(loc.L("confirm_label", "Delete")),
        content=ft.Text(loc.L("are_you_sure_label", "Are you sure you want to delete this message?")),
        actions=[
            ft.TextButton(loc.L("yes_label", "Yes"), on_click=lambda e: vahvista_poisto(True)),
            ft.TextButton(loc.L("cancel_label", "Cancel"), on_click=lambda e: vahvista_poisto(False)),
        ],
    )
    page.overlay.append(poisto_dialogi)

    haku_kentta = ft.TextField(
        label=loc.L("search_msg", "Search Messages..."),
        prefix_icon=ft.Icons.SEARCH,
        expand=True,
        on_change=lambda e: päivitä_lista()
    )

    haku_rivi = ft.Row([
        haku_kentta,
        ft.IconButton(icon=ft.Icons.CLEAR, on_click=tyhjenna_haku_evt)
    ])

    tallenna_nappi = ft.ElevatedButton(
        text=loc.L("save_btn", "Save"),
        on_click=tallenna_evt,
        icon=ft.Icons.SAVE
    )

    peruuta_nappi = ft.TextButton(loc.L("cancel_label", "Cancel"), on_click=peruuta_muokkaus_evt, visible=False, icon=ft.Icons.CANCEL)

    # --- Sivun rakennus ---

    page.add(
        ft.Text(loc.L("main_title", "Guestbook"), size=25, weight=ft.FontWeight.BOLD),
        input_field,
        info_text,
        ft.Row([
            tallenna_nappi,
            peruuta_nappi,
            ft.ElevatedButton(
        text=loc.L("empty_btn", "Empty"),
        on_click=tyhjenna_evt,
        icon=ft.Icons.DELETE_SWEEP,
        color="red"
    )
        ], wrap=True),
        ft.Divider(),
        haku_rivi,
        ft.Text(loc.L("message_label", "Saved messages"), size=20),
        viestilista
    )

    päivitä_lista()

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")

