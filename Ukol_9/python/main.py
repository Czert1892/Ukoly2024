class Kniha:
    def __init__(self, nazev, autor, rok_vydani, isbn):
        self.nazev = nazev
        self.autor = autor
        self.rok_vydani = rok_vydani
        self.isbn = isbn

    @property
    def isbn(self):
        return self._isbn

    @isbn.setter
    def isbn(self, value):
        if len(value) != 13 or not value.isdigit():
            raise ValueError("ISBN musí mít formát ISBN-13 (13 číslic).")
        self._isbn = value

    def __str__(self):
        return f"{self.nazev} od {self.autor} ({self.rok_vydani}), ISBN: {self.isbn}"


import random
class Ctenar:
    def __init__(self, jmeno, prijmeni):
        self.jmeno = jmeno
        self.prijmeni = prijmeni
        self.cislo_prukazky = self.vygeneruj_cislo_prukazky()

    @property
    def cislo_prukazky(self):
        return self._cislo_prukazky

    @cislo_prukazky.setter
    def cislo_prukazky(self, value):
        if value <= 0:
            raise ValueError("Číslo průkazky musí být kladné celé číslo.")
        self._cislo_prukazky = value

    @staticmethod
    def vygeneruj_cislo_prukazky():
        return random.randint(1, 10000)

    def __str__(self):
        return f"{self.jmeno} {self.prijmeni}, číslo průkazky: {self.cislo_prukazky}"

import csv
from functools import wraps

def kniha_existuje(func):
    @wraps(func)
    def wrapper(self, isbn, *args, **kwargs):
        if not any(kniha.isbn == isbn for kniha in self.knihy):
            raise ValueError(f"Kniha s ISBN {isbn} neexistuje.")
        return func(self, isbn, *args, **kwargs)
    return wrapper

class Knihovna:
    def __init__(self, nazev):
        self.nazev = nazev
        self.knihy = []
        self.ctenari = []
        self.vypujcene_knihy = {}

    @classmethod
    def z_csv(cls, soubor):
        with open(soubor, newline='') as csvfile:
            reader = csv.reader(csvfile)
            nazev = next(reader)[0].split(":")[1]
            knihovna = cls(nazev)
            for row in reader:
                if row[0] == "kniha":
                    knihovna.pridej_knihu(Kniha(row[1], row[2], int(row[3]), row[4]))
                elif row[0] == "ctenar":
                    ctenar = Ctenar(row[5], row[6])
                    ctenar.cislo_prukazky = int(row[4])
                    knihovna.registruj_ctenare(ctenar)
        return knihovna

    def pridej_knihu(self, kniha):
        self.knihy.append(kniha)

    @kniha_existuje
    def odeber_knihu(self, isbn):
        self.knihy = [kniha for kniha in self.knihy if kniha.isbn != isbn]

    def vyhledej_knihu(self, klicova_slovo=None, isbn=None):
        if isbn:
            return [kniha for kniha in self.knihy if kniha.isbn == isbn]
        return [kniha for kniha in self.knihy if klicova_slovo.lower() in kniha.nazev.lower()]

    def registruj_ctenare(self, ctenar):
        self.ctenari.append(ctenar)

    def zrus_registraci_ctenare(self, ctenar):
        self.ctenari.remove(ctenar)

    def vyhledej_ctenare(self, klicova_slovo=None, cislo_prukazky=None):
        if cislo_prukazky:
            return [ctenar for ctenar in self.ctenari if ctenar.cislo_prukazky == cislo_prukazky]
        return [ctenar for ctenar in self.ctenari if klicova_slovo.lower() in ctenar.jmeno.lower()]

    @kniha_existuje
    def vypujc_knihu(self, isbn, ctenar):
        if isbn in self.vypujcene_knihy:
            raise ValueError(f"Kniha s ISBN {isbn} je již vypůjčena.")
        self.vypujcene_knihy[isbn] = (ctenar, datetime.date.today())

    @kniha_existuje
    def vrat_knihu(self, isbn, ctenar):
        if isbn not in self.vypujcene_knihy:
            raise ValueError(f"Kniha s ISBN {isbn} není vypůjčena.")
        del self.vypujcene_knihy[isbn]

    def __str__(self):
        return f"Knihovna {self.nazev} má {len(self.knihy)} knih a {len(self.ctenari)} čtenářů."