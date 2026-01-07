# -*- coding: utf-8 -*-
"""
localization.py
Author: Tuomas Lähteenmäki
Version: 0.1
License: GNU GPLv3
Description: Auto localization
"""
import json
import os
import configparser
import sys

class Localizer:
    def __init__(self, lang_code=None):
        # 1. TUNNISTETAAN SIJAINTI: Onko EXE vai skripti?
        if getattr(sys, 'frozen', False):
            # Jos ollaan .exe, base_path on kansio missä .exe on
            self.base_path = os.path.dirname(sys.executable)
            # Locales on pakattu exen sisään (väliaikainen kansio)
            self.internal_path = getattr(sys, '_MEIPASS', self.base_path)
        else:
            # Normaali ajo skriptinä
            self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.internal_path = self.base_path

        config = configparser.ConfigParser()
        config_path = os.path.join(self.base_path, 'config.conf')

        # 2. Selvitetään käytettävä kieli ja luodaan oletukset
        if lang_code is None:
            if os.path.exists(config_path):
                config.read(config_path, encoding='utf-8')
                lang_code = config.get('SETTINGS', 'language', fallback='en')
            else:
                lang_code = 'en'
                # LUODAAN KAIKKI OLETUSASETUKSET TÄSSÄ
                if not config.has_section('SETTINGS'):
                    config.add_section('SETTINGS')
                
                config.set('SETTINGS', 'language', lang_code)
                # Lisätään salasana ja muut tarvittavat
                config.set('SETTINGS', 'admin_password', '1234')
                config.set('SETTINGS', 'theme', 'dark')
                
                with open(config_path, 'w', encoding='utf-8') as f:
                    config.write(f)

        # 3. Määritetään polku kielitiedostoon
        # Käytetään internal_pathia, jotta löydetään exen sisään pakatut JSONit
        locales_dir = os.path.join(self.internal_path, "locales")
        self.lang_file = os.path.join(locales_dir, f"lang_{lang_code}.json")
        
        # Luodaan kansio vain jos ajetaan skriptinä (exen sisään ei voi luoda)
        if not getattr(sys, 'frozen', False) and not os.path.exists(locales_dir):
            os.makedirs(locales_dir)
            
        self.texts = self._lataa_tekstit()

    def _lataa_tekstit(self):
        if not os.path.exists(self.lang_file):
            return {}
        try:
            with open(self.lang_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Virhe ladattaessa kielitiedostoa: {e}")
            return {}

    def L(self, avain, oletus):
        """Hakee käännöksen. Huom: Exe-muodossa uusia avaimia ei tallenneta exen sisään."""
        if avain not in self.texts:
            self.texts[avain] = oletus
            # Tallennetaan uudet avaimet vain, jos ei olla exen sisällä
            if not getattr(sys, 'frozen', False):
                try:
                    with open(self.lang_file, 'w', encoding='utf-8') as f:
                        json.dump(self.texts, f, indent=4, ensure_ascii=False)
                except:
                    pass
        return self.texts.get(avain, oletus)