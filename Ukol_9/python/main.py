import random
import csv
import datetime

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
        return f"{self.nazev} od {self.autor} (ISBN: {self.isbn})"

class Ctenar:
    def __init__(self, jmeno, prijmeni, cislo_prukazky=None):
        self.jmeno = jmeno
        self.prijmeni = prijmeni
        self.cislo_prukazky = cislo_prukazky or Ctenar.vygeneruj_cislo_prukazky()

    @property
    def cislo_prukazky(self):
        return self._cislo_prukazky

    @cislo_prukazky.setter
    def cislo_prukazky(self, value):
        if value is None or value <= 0:
            raise ValueError("Číslo průkazky musí být kladné celé číslo.")
        self._cislo_prukazky = value

    @staticmethod
    def vygeneruj_cislo_prukazky():
        return random.randint(1, 1000000)

    def __str__(self):
        return f"{self.jmeno} {self.prijmeni} (Číslo průkazky: {self.cislo_prukazky})"

def kniha_existuje(func):
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
        knihovna = cls("Neznámá knihovna")
        with open(soubor, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['typ'] == 'kniha':
                    knihovna.knihy.append(Kniha(row['nazev'], row['autor'], int(row['rok_vydani']), row['isbn']))
                elif row['typ'] == 'ctenar':
                    knihovna.ctenari.append(Ctenar(row['jmeno'], row['prijmeni'], int(row['cislo_prukazky'])))
            knihovna.nazev = row.get('nazev_knihovny', "Neznámá knihovna")
        return knihovna

    def pridej_knihu(self, kniha):
        self.knihy.append(kniha)

    @kniha_existuje
    def odeber_knihu(self, isbn):
        self.knihy = [kniha for kniha in self.knihy if kniha.isbn != isbn]

    def vyhledej_knihu(self, klicova_slovo=None, isbn=None):
        results = []
        for kniha in self.knihy:
            if (klicova_slovo and (klicova_slovo in kniha.nazev or klicova_slovo in kniha.autor)) or (isbn and kniha.isbn == isbn):
                results.append(kniha)
        return results

    def registruj_ctenare(self, ctenar):
        self.ctenari.append(ctenar)

    def zrus_registraci_ctenare(self, ctenar):
        self.ctenari.remove(ctenar)

    def vyhledej_ctenare(self, klicova_slovo=None, cislo_prukazky=None):
        results = []
        for ctenar in self.ctenari:
            if (klicova_slovo and (klicova_slovo in ctenar.jmeno or klicova_slovo in ctenar.prijmeni)) or (cislo_prukazky and ctenar.cislo_prukazky == cislo_prukazky):
                results.append(ctenar)
        return results

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

from os.path import realpath, dirname, join

if __name__ == "__main__":
    knihovna = Knihovna.z_csv(join(dirname(realpath(__file__)), "knihovna.csv"))
    print(f"Knihovna načtena z CSV: {knihovna.nazev}")

    kniha1 = Kniha("Stopařův průvodce po Galaxii", "Douglas Adams", 1979, "9780345391803")
    print(f"Kniha 1: {kniha1}")

    try:
        kniha2 = Kniha("Název knihy 2", "Autor 2", 2024, "invalidISBN")
    except ValueError as e:
        print(f"Chyba při vytváření knihy 2: {e}")

    knihovna.pridej_knihu(kniha1)
    print(f"Knihy v knihovně: {[str(k) for k in knihovna.knihy]}")

    knihovna.odeber_knihu("9780345391803")
    print(f"Knihy v knihovně po odebrání: {[str(k) for k in knihovna.knihy]}")

    ctenar1 = Ctenar("Jan", "Novák")
    print(f"Čtenář 1: {ctenar1}")
    
    try:
        ctenar1.cislo_prukazky = -100  # Invalid
    except ValueError as e:
        print(f"Chyba nastavení čísla průkazky: {e}")
    
    print(f"Čtenář 1: {ctenar1}")

    ctenar2 = Ctenar("Petr", "Svoboda")
    knihovna.registruj_ctenare(ctenar1)
    knihovna.registruj_ctenare(ctenar2)
    print(f"Seznam čtenářů: {[str(c) for c in knihovna.ctenari]}")

    knihovna.zrus_registraci_ctenare(ctenar1)
    print(f"Seznam čtenářů po odebrání: {[str(c) for c in knihovna.ctenari]}")

    print(f"Vyhledávání knih podle klíčových slov: {[str(kniha) for kniha in knihovna.vyhledej_knihu(klicova_slovo='1984')]}")
    print(f"Vyhledávání čtenářů podle klíčových slov: {[str(ctenar) for ctenar in knihovna.vyhledej_ctenare(klicova_slovo='Petr')]}")

    knihovna.pridej_knihu(kniha1)
    knihovna.vypujc_knihu(kniha1.isbn, ctenar2)
    print(f"Vypůjčené knihy: {[(isbn, str(ctenar), str(datum)) for isbn, (ctenar, datum) in knihovna.vypujcene_knihy.items()]}")
    knihovna.vrat_knihu(kniha1.isbn, ctenar2)
    print(f"Vypůjčené knihy po vrácení: {[(isbn, str(ctenar), str(datum)) for isbn, (ctenar, datum) in knihovna.vypujcene_knihy.items()]}")

    print(knihovna)