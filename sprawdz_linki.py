import re
import requests
import pandas as pd
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}

MATERIAL_KEYWORDS = [
    "bawełna", "elastan", "poliester", "wiskoza", "len", "modal",
    "akryl", "wełna", "poliamid", "lyocell", "denim", "skład", "materiał"
]

COLOR_KEYWORDS = [
    "czarny", "czarna", "czarne", "black",
    "niebieski", "niebieska", "niebieskie", "blue",
    "mid blue", "dark blue", "light blue",
    "granatowy", "navy",
    "szary", "szara", "szare", "grey", "gray",
    "biały", "biała", "białe", "white",
    "beżowy", "beżowa", "beżowe", "beige",
    "zielony", "zielona", "zielone", "green",
    "różowy", "różowa", "różowe", "pink",
    "czerwony", "czerwona", "czerwone", "red",
    "brązowy", "brązowa", "brązowe", "brown",
    "khaki", "oliwkowy",
    "ecru",
    "kremowy", "kremowa", "kremowe",
    "żółty", "żółta", "żółte", "yellow",
    "pomarańczowy", "pomarańczowa", "pomarańczowe", "orange",
    "fioletowy", "fioletowa", "fioletowe", "purple",
    "turkusowy", "turkusowa", "turkusowe", "turquoise"
]

# Łapie np.:
# C 132-017
# C 132-017 BLACK
# C 132-017 DARK BLUE
# 0578A-130
# 0578A-130 TURQUOISE
# 0578A-130 DARK BLUE
NUMER_PATTERN = re.compile(
    r'\b('
    r'[A-Z]\s?\d{3,4}-\d{3}(?:\s+[A-Z]+(?:\s+[A-Z]+)?)?'
    r'|'
    r'\d{4}[A-Z]-\d{3}(?:\s+[A-Z]+(?:\s+[A-Z]+)?)?'
    r')\b'
)

def wczytaj_linki(nazwa_pliku):
    with open(nazwa_pliku, "r", encoding="utf-8") as f:
        return [linia.strip() for linia in f if linia.strip()]

def pobierz_html(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Błąd przy pobieraniu {url}: {e}")
        return None

def wyciagnij_naglowek(soup):
    h1 = soup.find("h1")
    if h1:
        tekst = h1.get_text(" ", strip=True)
        if tekst:
            return tekst

    if soup.title:
        tekst = soup.title.get_text(" ", strip=True)
        if tekst:
            return tekst

    return ""

def czy_jest_material(tekst_strony):
    tekst = tekst_strony.lower()
    for slowo in MATERIAL_KEYWORDS:
        if slowo in tekst:
            return "tak"
    return "nie"

def znajdz_kolor(naglowek, tekst_strony):
    caly_tekst = f"{naglowek} {tekst_strony}".lower()

    znalezione = []
    for kolor in COLOR_KEYWORDS:
        if kolor.lower() in caly_tekst:
            znalezione.append(kolor)

    unikalne = []
    for k in znalezione:
        if k not in unikalne:
            unikalne.append(k)

    if unikalne:
        return "tak", ", ".join(unikalne)

    return "nie", ""

def znajdz_numer(naglowek, tekst_strony):
    match_naglowek = NUMER_PATTERN.search(naglowek)
    if match_naglowek:
        numer = " ".join(match_naglowek.group(1).split())
        return "tak", numer

    match_strona = NUMER_PATTERN.search(tekst_strony)
    if match_strona:
        numer = " ".join(match_strona.group(1).split())
        return "tak", numer

    return "nie", ""

def analizuj_link(url):
    html = pobierz_html(url)

    if not html:
        return {
            "Wykaz linków": url,
            "treść nagłówka": "",
            "czy jest materiał": "błąd",
            "czy jest kolor": "błąd",
            "wypisany kolor": "",
            "czy jest numer": "błąd",
            "wypisany numer": ""
        }

    soup = BeautifulSoup(html, "html.parser")
    naglowek = wyciagnij_naglowek(soup)
    tekst_strony = soup.get_text(" ", strip=True)

    material = czy_jest_material(tekst_strony)
    czy_kolor, kolor = znajdz_kolor(naglowek, tekst_strony)
    czy_numer, numer = znajdz_numer(naglowek, tekst_strony)

    return {
        "Wykaz linków": url,
        "treść nagłówka": naglowek,
        "czy jest materiał": material,
        "czy jest kolor": czy_kolor,
        "wypisany kolor": kolor,
        "czy jest numer": czy_numer,
        "wypisany numer": numer
    }

def main():
    linki = wczytaj_linki("linki.txt")
    wyniki = []

    for i, link in enumerate(linki, start=1):
        print(f"Sprawdzam {i}/{len(linki)}: {link}")
        wynik = analizuj_link(link)
        wyniki.append(wynik)

    df = pd.DataFrame(wyniki)
    df.to_excel("wyniki.xlsx", index=False)
    df.to_csv("wyniki.csv", index=False, encoding="utf-8-sig")

    print("Gotowe. Zapisano pliki: wyniki.xlsx oraz wyniki.csv")

if __name__ == "__main__":
    main()
