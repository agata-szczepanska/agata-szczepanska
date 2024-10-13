import psutil
import pyodbc
import socket

# funkcja do laczenia z Azure
def connect_to_azure_sql():
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 18 for SQL Server};'
            'SERVER=agataandorinha.database.windows.net;'
            'DATABASE=Dynatrace;'
            'UID=AgataAndorinha;'
            'PWD=Dynatrace123'
        )
        print("Połączenie z bazą danych udane!")
        return conn
    except Exception as e:
        print(f"Błąd podczas łączenia się z bazą danych: {e}")
        return None

# funkcja sprawdzajaca ram i zapusjaca wyniki
def sprawdz_i_zapisz_ram(conn):
    pamiec = psutil.virtual_memory()

  # pobranie nazwy komputera
    nazwa_komputera = socket.gethostname()  

    calkowita_pamiec = pamiec.total / (1024 ** 3)  # w GB
    uzywana_pamiec = pamiec.used / (1024 ** 3)     # w GB
    wolna_pamiec = pamiec.available / (1024 ** 3)  # w GB
    procent_uzycia = pamiec.percent                # w %

    # przygotowanie kursora i zapytania SQL
    cursor = conn.cursor()
    
    zapytanie = """
    INSERT INTO RamUsage (ComputerName, TotalMemoryGB, UsedMemoryGB, FreeMemoryGB, MemoryUsagePercent)
    VALUES (?, ?, ?, ?, ?)
    """
    
    dane = (nazwa_komputera, calkowita_pamiec, uzywana_pamiec, wolna_pamiec, procent_uzycia)

    # wstawienie danych do bazy
    try:
        cursor.execute(zapytanie, dane)
        conn.commit()
        print(f"Dane o zużyciu RAM z komputera {nazwa_komputera} zostały zapisane do bazy danych.")
    except Exception as e:
        print(f"Błąd podczas zapisywania danych: {e}")
    finally:
        cursor.close()
# funkcja odczytujaca dane z tabeli RamUsage
def odczytaj_dane(conn):
    cursor = conn.cursor()
    
    zapytanie = "SELECT * FROM RamUsage ORDER BY CreatedAt DESC"
    
    try:
        cursor.execute(zapytanie)
        wiersze = cursor.fetchall()
        if len(wiersze) > 0:
            for wiersz in wiersze:
                print(f"ID: {wiersz.Id}, Komputer: {wiersz.ComputerName}, Całkowita: {wiersz.TotalMemoryGB:.2f} GB, "
                      f"Używana: {wiersz.UsedMemoryGB:.2f} GB, Wolna: {wiersz.FreeMemoryGB:.2f} GB, "
                      f"Użycie: {wiersz.MemoryUsagePercent:.2f}%, Data: {wiersz.CreatedAt}")
        else:
            print("Brak zapisanych danych w tabeli RamUsage.")
    except Exception as e:
        print(f"Błąd podczas odczytywania danych: {e}")
    finally:
        cursor.close()

# glowna funkcja
if __name__ == "__main__":
    conn = connect_to_azure_sql()
    if conn:
        wybor = input("Co chcesz zrobić? (1: Zapisz dane, 2: Odczytaj dane): ")
        
        if wybor == '1':
            sprawdz_i_zapisz_ram(conn)  # zapis danych o zuzyciu RAM
        elif wybor == '2':
            odczytaj_dane(conn)  # odczyt zapisanych danych
        else:
            print("Nieprawidłowy wybór. Wybierz 1, aby zapisać dane, lub 2, aby je odczytać.")
        
        conn.close()  