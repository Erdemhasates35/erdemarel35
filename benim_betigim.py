#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Kullanıcı Yapılandırma Yardımcı Betiği (Python Versiyonu)
# Açıklama: Ortam değişkenlerini yönetmeye ve yardımcı görevleri çalıştırmaya yarar.
#           Bash'in 'source' mekanizmasının doğrudan alternatifi değildir.
# Kullanım:
#   Ortam değişkenlerini shell'e aktarmak için: eval $(python bu_betik.py export_env)
#   Bir fonksiyonu çalıştırmak için: python bu_betik.py <fonksiyon_adı> [argümanlar]
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import os
import subprocess
import sys
import json
import socket
import shutil
from pathlib import Path

# --- Güvenlik Uyarısı ---
# Hassas bilgileri (API Anahtarları, Mnemonic vb.) doğrudan koda yazmak
# SON DERECE GÜVENLİKSİZDİR. Bunun yerine .env dosyası veya güvenli bir
# sır yönetim sistemi kullanın.
# Örnek .env kullanımı için: pip install python-dotenv
# from dotenv import load_dotenv
# load_dotenv() # .env dosyasındaki değişkenleri yükler
# ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")

# === Ortam Değişkenleri (Örnekler - GÜVENLİ DEĞİL!) ===
# Bu değerleri .env dosyasından veya başka güvenli bir yerden okuyun.
ENV_VARS = {
    "ETHERSCAN_API_KEY": "NPK428YFFKRU3UPJ29NVT9YEHZHVN9MRAF",
    "GNOSISCHAIN_API_KEY": "FHRU2RQC7KAB4QACKGPENER5165FY5BHNB",
    "COINGECKO_API_KEY": "CG-XVRR3nPYJmmYr96ZbuQgtbbk",
    "DUNE_API_KEY": "rQD8StqSkdUiGi28i7rdXCkJjdjXNgpV",
    "BSCSCAN_API_KEY": "MZWQXXXPP4JGTZ97T8W15ZZX2CRW72MYZV",
    "PANCAKESWAP_API_KEY": "595f2096ec273d5781b439b7359dd33a768afe27bb3df8fe0f3d4db42ea3c79a",
    "PANCAKESWAP_SECRET_KEY": "778c571a51f0ae90a1a3bca4c39635b1ee9dc287a36d11c93bdb9d361c11db48",
    # "MNEMONIC": "BU ALANA ASLA GERÇEK KELİMELERİNİZİ YAZMAYIN", # !!! KESİNLİKLE KULLANMAYIN !!!

    # === PROJE Ayarları (Örnekler) ===
    "PROJE_NAME": "proje",
    "PROJE_API_URL": "http://api.proje.test",
    "PROJE_API_KEY": "PROJE_API_ANAHTARINIZI_BURAYA_GIRIN", # Güvenli yerden okuyun!
    "PROJE_DB_HOST": "localhost",
    "PROJE_DB_PORT": "5432",
    "PROJE_DB_NAME": "proje_db",
    "PROJE_DEBUG_MODE": "true",
}

# === Yardımcı Fonksiyonlar ===

def run_command(command, **kwargs):
    """Verilen komutu çalıştırır ve çıktıyı yakalar."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, **kwargs)
        return result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        print(f"Hata: Komut çalıştırılamadı '{command}'", file=sys.stderr)
        print(f"Stderr: {e.stderr}", file=sys.stderr)
        return None, e.stderr.strip()
    except FileNotFoundError:
        print(f"Hata: Komut bulunamadı '{command.split()[0]}'", file=sys.stderr)
        return None, f"Komut bulunamadı: {command.split()[0]}"

def git_status_short():
    """Kısa git durumunu gösterir."""
    stdout, stderr = run_command("git status -sb")
    if stdout is not None:
        print(stdout)

def git_prune_local():
    """Uzakta silinmiş dalları yerelden temizler."""
    print("Yerel dallar temizleniyor (pruning)...")
    run_command("git fetch -p && git branch -vv | awk '/: gone]/{print $1}' | xargs git branch -D")
    print("Temizleme tamamlandı.")

def docker_clean():
    """Durdurulmuş container'ları, kullanılmayan volume'leri ve network'leri, eski imajları temizler."""
    print("Durdurulmuş Docker container'ları temizleniyor...")
    run_command("docker ps -a -q -f status=exited | xargs --no-run-if-empty docker rm")
    print("Kullanılmayan Docker volume'leri temizleniyor...")
    run_command("docker volume ls -q -f dangling=true | xargs --no-run-if-empty docker volume rm")
    print("Kullanılmayan Docker network'leri temizleniyor...")
    run_command("docker network ls -q -f dangling=true | xargs --no-run-if-empty docker network rm")
    print("Eski (dangling) Docker imajları temizleniyor...")
    run_command("docker images -q -f dangling=true | xargs --no-run-if-empty docker rmi")
    print("Docker temizliği tamamlandı.")

def my_ips():
    """Yerel ve genel IP adreslerini gösterir."""
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"Yerel Host Adı: {hostname}")
        print(f"Yerel IP Adresi: {local_ip}")
    except socket.gaierror:
        print("Yerel IP adresi alınamadı.")

    print("Genel IP Adresi alınıyor...")
    # Genel IP için harici bir servis kullanmak gerekir (örneğin ifconfig.me)
    stdout, stderr = run_command("curl -s ifconfig.me")
    if stdout:
        print(f"Genel IP Adresi: {stdout}")
    else:
        print("Genel IP adresi alınamadı.")

def mkcd(dir_name):
    """Yeni bir dizin oluşturur. DİKKAT: Shell'in dizinini DEĞİŞTİRMEZ."""
    try:
        path = Path(dir_name)
        path.mkdir(parents=True, exist_ok=True)
        print(f"Dizin oluşturuldu: {path.resolve()}")
        # ÖNEMLİ: Python betiği bittiğinde shell'in çalışma dizini değişmez.
        # Kullanıcının manuel olarak 'cd dir_name' yapması gerekir.
    except Exception as e:
        print(f"Hata: Dizin oluşturulamadı '{dir_name}': {e}", file=sys.stderr)

def fsearch(pattern, search_path="."):
    """Belirtilen dizinde dosya adı desenine göre arama yapar (find alternatifi)."""
    print(f"'{search_path}' içinde '{pattern}' deseni aranıyor...")
    try:
        for entry in Path(search_path).rglob(pattern):
            print(entry)
    except FileNotFoundError:
        print(f"Hata: Arama yolu bulunamadı '{search_path}'", file=sys.stderr)
    except Exception as e:
        print(f"Arama sırasında hata: {e}", file=sys.stderr)


def serve_here(port=8000):
    """Bulunulan dizini basit bir HTTP sunucusu ile yayınlar."""
    try:
        port = int(port)
        print(f"Bulunulan dizin http://0.0.0.0:{port} adresinde yayınlanıyor...")
        print("Sunucuyu durdurmak için Ctrl+C basın.")
        # Python'un kendi http sunucusunu çalıştırır
        run_command(f"python -m http.server {port}")
    except ValueError:
        print("Hata: Geçersiz port numarası.", file=sys.stderr)
    except Exception as e:
        print(f"Sunucu başlatılırken hata: {e}", file=sys.stderr)


def top_procs(n=10):
    """CPU ve Belleği en çok kullanan N süreci gösterir."""
    try:
        n = int(n)
        print(f"CPU Kullanımına Göre İlk {n} Süreç:")
        run_command(f"ps aux --sort=-%cpu | head -n {n+1}") # +1 başlık satırı için
        print(f"\nBellek Kullanımına Göre İlk {n} Süreç:")
        run_command(f"ps aux --sort=-%mem | head -n {n+1}") # +1 başlık satırı için
    except ValueError:
        print("Hata: Geçersiz süreç sayısı.", file=sys.stderr)

def crypto_price(symbol="bitcoin"):
    """CoinGecko API kullanarak kripto para fiyatını gösterir (API Anahtarı Gerekebilir)."""
    # Bu fonksiyon için 'requests' kütüphanesi gerekir: pip install requests
    try:
        import requests
    except ImportError:
        print("Hata: 'requests' kütüphanesi gerekli. 'pip install requests' komutu ile kurun.", file=sys.stderr)
        return

    # CoinGecko API anahtarını ortam değişkeninden almayı deneyin (daha güvenli)
    api_key = os.getenv("COINGECKO_API_KEY", ENV_VARS.get("COINGECKO_API_KEY"))
    headers = {}
    if api_key and api_key.startswith("CG-"):
         # Ücretsiz API anahtarı için header gerekmez, ancak ücretli planlar için gerekebilir.
         # Şimdilik header'ı boş bırakıyoruz veya API dokümantasyonuna göre ayarlıyoruz.
         # headers = {'X-Cg-Demo-Api-Key': api_key} # Ücretsiz anahtar için bu GEREKMEZ
         pass

    # CoinGecko API'den coinin ID'sini almak gerekebilir. 'symbol' genellikle 'id'dir.
    coin_id = symbol.lower()
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() # HTTP hatalarını kontrol et
        data = response.json()

        if coin_id in data and 'usd' in data[coin_id]:
            price = data[coin_id]['usd']
            print(f"{symbol.upper()} Fiyatı: ${price:,.2f}")
        else:
            print(f"Hata: '{symbol}' için fiyat bilgisi bulunamadı.")

    except requests.exceptions.RequestException as e:
        print(f"API isteği sırasında hata: {e}", file=sys.stderr)
    except json.JSONDecodeError:
        print("API'den geçersiz yanıt alındı.", file=sys.stderr)


def copy_pubkey(key_path="~/.ssh/id_rsa.pub"):
    """SSH public anahtarını panoya kopyalar (platforma bağlı olabilir)."""
    key_file = Path(key_path).expanduser()
    if not key_file.is_file():
        print(f"Hata: Public key dosyası bulunamadı: {key_file}", file=sys.stderr)
        return

    try:
        # Platforma göre pano komutunu belirle
        if sys.platform == "darwin": # macOS
            cmd = f"cat {key_file} | pbcopy"
        elif sys.platform.startswith("linux"): # Linux (xclip veya xsel gerektirir)
             if shutil.which("xclip"):
                 cmd = f"cat {key_file} | xclip -selection clipboard"
             elif shutil.which("xsel"):
                 cmd = f"cat {key_file} | xsel --clipboard --input"
             else:
                 print("Hata: Panoya kopyalama için 'xclip' veya 'xsel' kurulu olmalı.", file=sys.stderr)
                 return
        elif sys.platform == "win32": # Windows
            cmd = f"type {key_file} | clip"
        else:
            print(f"Hata: Bu platform ({sys.platform}) için pano desteği eklenmedi.", file=sys.stderr)
            return

        subprocess.run(cmd, shell=True, check=True)
        print(f"Public key ({key_file}) panoya kopyalandı.")

    except Exception as e:
        print(f"Anahtar panoya kopyalanırken hata: {e}", file=sys.stderr)


def export_env_vars():
    """Ortam değişkenlerini 'export VAR=değer' formatında yazdırır."""
    print("# Özel 'proje' ayarları yükleniyor...")
    # Güvenli Depolama: Gerçek uygulamada bu değişkenleri .env veya başka yerden okuyun
    # Örneğin:
    # from dotenv import load_dotenv
    # load_dotenv()
    # for key in ENV_VARS: # Ya da .env dosyasında tanımlı anahtarlar için döngü
    #    value = os.getenv(key)
    #    if value:
    #        print(f'export {key}="{value}"')

    # --- GÜVENLİK RİSKİ: Aşağıdaki kod hassas bilgileri yazdırabilir! ---
    # Sadece GÜVENLİ ortam değişkenlerini (örn. PROJE_NAME) yazdırmak daha iyidir.
    # VEYA tüm değişkenleri .env dosyasından okuyup yazdırmak daha mantıklıdır.
    for key, value in ENV_VARS.items():
         # MNEMONIC gibi çok hassas verileri KESİNLİKLE yazdırmayın!
        if key == "MNEMONIC":
             print(f"# UYARI: MNEMONIC değişkeni güvenlik nedeniyle yazdırılmadı.", file=sys.stderr)
             continue
        # Değerdeki özel karakterlerden kaçınmak için çift tırnak kullan
        # ve içindeki çift tırnakları escape et (gerçi bu basit örnekte yok)
        print(f'export {key}="{value}"')
    print("# Shell yapılandırma değişkenleri dışa aktarıldı.")


def print_usage():
    """Kullanım bilgilerini yazdırır."""
    print("Kullanım:")
    print(f"  Ortam değişkenlerini dışa aktar: python {sys.argv[0]} export_env")
    print(f"  Yardımcı fonksiyonları çalıştır:")
    # Fonksiyonları dinamik olarak listelemek daha iyi olabilir ama şimdilik manuel:
    print(f"    python {sys.argv[0]} git_status_short")
    print(f"    python {sys.argv[0]} git_prune_local")
    print(f"    python {sys.argv[0]} docker_clean")
    print(f"    python {sys.argv[0]} my_ips")
    print(f"    python {sys.argv[0]} mkcd <dizin_adı>")
    print(f"    python {sys.argv[0]} fsearch <desen> [yol]")
    print(f"    python {sys.argv[0]} serve_here [port]")
    print(f"    python {sys.argv[0]} top_procs [sayı]")
    print(f"    python {sys.argv[0]} crypto_price <sembol>")
    print(f"    python {sys.argv[0]} copy_pubkey [anahtar_yolu]")


# === Betik Ana Çalışma Bloğu ===
if __name__ == "__main__":
    # Komut satırı argümanlarını al
    args = sys.argv[1:] # Betik adı hariç

    if not args:
        print_usage()
        sys.exit(1)

    command = args[0]
    func_args = args[1:]

    # Komuta göre ilgili fonksiyonu çağır
    if command == "export_env":
        if func_args:
             print("Hata: 'export_env' komutu argüman almaz.", file=sys.stderr)
             sys.exit(1)
        export_env_vars()
    elif command == "git_status_short":
        git_status_short()
    elif command == "git_prune_local":
        git_prune_local()
    elif command == "docker_clean":
        docker_clean()
    elif command == "my_ips":
        my_ips()
    elif command == "mkcd":
        if len(func_args) != 1:
            print("Hata: 'mkcd' komutu bir dizin adı argümanı gerektirir.", file=sys.stderr)
            sys.exit(1)
        mkcd(func_args[0])
    elif command == "fsearch":
        if not func_args:
            print("Hata: 'fsearch' komutu en az bir arama deseni argümanı gerektirir.", file=sys.stderr)
            sys.exit(1)
        pattern = func_args[0]
        search_path = func_args[1] if len(func_args) > 1 else "."
        fsearch(pattern, search_path)
    elif command == "serve_here":
        port = func_args[0] if func_args else 8000
        serve_here(port)
    elif command == "top_procs":
        n = func_args[0] if func_args else 10
        top_procs(n)
    elif command == "crypto_price":
        if not func_args:
            print("Hata: 'crypto_price' komutu bir kripto para sembolü/id'si gerektirir.", file=sys.stderr)
            sys.exit(1)
        crypto_price(func_args[0])
    elif command == "copy_pubkey":
        key_path = func_args[0] if func_args else "~/.ssh/id_rsa.pub"
        copy_pubkey(key_path)
    else:
        print(f"Hata: Bilinmeyen komut '{command}'", file=sys.stderr)
        print_usage()
        sys.exit(1)

    # Betik sonu mesajı (opsiyonel)
    # print("Python yapılandırma yardımcısı tamamlandı.")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Kullanıcı Yapılandırma ve Kapsamlı Yardımcı Görev Betiği (Python Versiyonu)
#
# Açıklama: Ortam değişkenlerini dışa aktarmaya (shell'e yüklemek için) ve
#           çeşitli geliştirici yardımcı görevlerini çalıştırmaya yarar.
#           Temizlik fonksiyonları (Docker, Git prune) tanımlıdır ancak
#           güvenlik ve isteğiniz üzerine fiili temizlik yapmayacak şekilde
#           devre dışı bırakılmıştır.
#
# Nasıl Kaydedilir ve Çalıştırılır (Örn: nano editörü ile):
#   1. Terminali açın.
#   2. `nano yardimci_betik.py` yazıp Enter'a basın.
#   3. Bu kodun tamamını kopyalayıp terminal penceresine yapıştırın.
#   4. Kaydetmek için `Ctrl+O` tuşlarına basın, dosya adını onaylamak için Enter'a basın.
#   5. Editörden çıkmak için `Ctrl+X` tuşlarına basın.
#   6. (Opsiyonel) Betiği çalıştırılabilir yapmak için: `chmod +x yardimci_betik.py`
#
# Kullanım:
#   Ortam Değişkenlerini Shell'e Aktarmak İçin:
#     eval $(python yardimci_betik.py export_env)
#     # veya çalıştırılabilir yaptıysanız:
#     eval $(./yardimci_betik.py export_env)
#
#   Bir Yardımcı Fonksiyonu Çalıştırmak İçin:
#     python yardimci_betik.py <fonksiyon_adı> [argümanlar]
#     # veya çalıştırılabilir yaptıysanız:
#     ./yardimci_betik.py <fonksiyon_adı> [argümanlar]
#     # Örnek: ./yardimci_betik.py my_ips
#     # Örnek: ./yardimci_betik.py crypto_price bitcoin
#     # Örnek: ./yardimci_betik.py generate_password 18
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import os
import subprocess
import sys
import json
import socket
import shutil
from pathlib import Path
import platform
import secrets
import string
import urllib.parse
import base64
import binascii
import calendar
import datetime
# 'requests' kütüphanesi crypto_price için gereklidir.
# Eğer kurulu değilse: pip install requests
try:
    import requests
except ImportError:
    # requests yoksa crypto_price fonksiyonu çalışmayacak
    pass


# --- Güvenlik Uyarısı ---
# Hassas bilgileri (API Anahtarları, Mnemonic vb.) DOĞRUDAN KODA YAZMAYIN!
# Bu son derece güvensizdir. Bunun yerine bir .env dosyası kullanın
# (python-dotenv kütüphanesi ile) veya güvenli bir sır yönetim sistemi kullanın.
# Bu betikteki anahtarlar SADECE YER TUTUCUDUR.
#
# Örnek .env kullanımı:
# 1. `pip install python-dotenv` komutu ile kütüphaneyi kurun.
# 2. Betikle aynı dizinde `.env` adında bir dosya oluşturun.
# 3. Dosya içeriği şöyle olabilir:
#    ETHERSCAN_API_KEY=asdf1234asdf1234asdf1234
#    PROJE_API_KEY=gizli_proje_anahtari
# 4. Aşağıdaki import ve `load_dotenv()` satırlarının başındaki yorumu kaldırın.
#
# from dotenv import load_dotenv
# load_dotenv() # Betik başladığında .env dosyasındaki değişkenleri yükler

# === Ortam Değişkenleri (ÖRNEKLER - GERÇEK DEĞERLERİ .env'den okuyun!) ===
ENV_VARS = {
    # API Anahtarları (YER TUTUCU - .env dosyasından veya os.getenv ile alınmalı)
    "ETHERSCAN_API_KEY": os.getenv("ETHERSCAN_API_KEY", "YOUR_ETHERSCAN_API_KEY_HERE"),
    "GNOSISCHAIN_API_KEY": os.getenv("GNOSISCHAIN_API_KEY", "YOUR_GNOSISCHAIN_API_KEY_HERE"),
    "COINGECKO_API_KEY": os.getenv("COINGECKO_API_KEY", "YOUR_COINGECKO_API_KEY_HERE_OR_NONE"),
    "DUNE_API_KEY": os.getenv("DUNE_API_KEY", "YOUR_DUNE_API_KEY_HERE"),
    "BSCSCAN_API_KEY": os.getenv("BSCSCAN_API_KEY", "YOUR_BSCSCAN_API_KEY_HERE"),
    "PANCAKESWAP_API_KEY": os.getenv("PANCAKESWAP_API_KEY", "YOUR_PANCAKESWAP_API_KEY_HERE"),
    "PANCAKESWAP_SECRET_KEY": os.getenv("PANCAKESWAP_SECRET_KEY", "YOUR_PANCAKESWAP_SECRET_KEY_HERE"),
    # "MNEMONIC": os.getenv("MNEMONIC", "BU ALANA ASLA GERÇEK KELİMELERİNİZİ YAZMAYIN"), # !!! KESİNLİKLE KULLANMAYIN !!!

    # === PROJE Ayarları (Örnekler - .env veya os.getenv ile alınmalı) ===
    "PROJE_NAME": os.getenv("PROJE_NAME", "benim_harika_projem"),
    "PROJE_API_URL": os.getenv("PROJE_API_URL", "http://api.proje.test"),
    "PROJE_API_KEY": os.getenv("PROJE_API_KEY", "PROJE_API_ANAHTARINIZI_BURAYA_GIRIN"), # Güvenli yerden okuyun!
    "PROJE_DB_HOST": os.getenv("PROJE_DB_HOST", "localhost"),
    "PROJE_DB_PORT": os.getenv("PROJE_DB_PORT", "5432"),
    "PROJE_DB_NAME": os.getenv("PROJE_DB_NAME", "proje_db"),
    "PROJE_DEBUG_MODE": os.getenv("PROJE_DEBUG_MODE", "true"), # 'true' veya 'false'
}

# === Yardımcı Fonksiyonlar ===

def run_command(command, **kwargs):
    """Verilen komutu çalıştırır ve çıktıyı canlı olarak yazdırır."""
    try:
        process_env = os.environ.copy()
        # stdout ve stderr'i doğrudan sys.stdout ve sys.stderr'e yönlendirerek canlı çıktı
        # capture_output=True yerine bunu kullanıyoruz. check=True önemli.
        result = subprocess.run(command, shell=True, check=True, text=True, env=process_env, **kwargs)
        # Not: Canlı çıktı yukarıda verildiği için burada tekrar yazdırmaya gerek yok.
        # Ancak dönüş değeri olarak yine de yakalanmış olabilir (eğer capture_output eklenseydi).
        # Şimdiki haliyle stdout/stderr yakalanmıyor, sadece işlem durumu dönüyor.
        return True, "" # Başarılı olduğunu belirtelim
    except subprocess.CalledProcessError as e:
        print(f"Hata: Komut '{command}' hata kodu {e.returncode} ile başarısız oldu.", file=sys.stderr)
        # stderr zaten canlı olarak yazdırılmış olmalı (eğer varsa).
        return False, str(e) # Başarısız olduğunu ve hatayı belirtelim
    except FileNotFoundError:
        cmd_name = command.split()[0]
        print(f"Hata: Komut bulunamadı '{cmd_name}'. PATH ortam değişkeninizi kontrol edin.", file=sys.stderr)
        return False, f"Komut bulunamadı: {cmd_name}"
    except Exception as e:
        print(f"Komut çalıştırılırken beklenmedik hata: {e}", file=sys.stderr)
        return False, str(e)

def git_status_short():
    """Kısa git durumunu gösterir."""
    print("\n--- Git Durumu (Kısa) ---")
    run_command("git status -sb")

def git_prune_local():
    """Uzakta silinmiş dalları yerelden temizler (DEVRE DIŞI)."""
    print("\n--- Git Prune Local (Devre Dışı) ---")
    print("Bu fonksiyon normalde `git fetch -p` ve eski dalları silerdi.")
    print("İstek üzerine temizlik işlemi pasif hale getirildi.")
    print("Yapılacak adımlar normalde şunlar olurdu:")
    print("  1. `git fetch -p`")
    print("  2. `git branch -vv | grep ': gone]' | awk '{print $1}' | xargs --no-run-if-empty git branch -D`")
    # GERÇEK KOMUTLAR YORUM SATIRI HALİNDE:
    # run_command("git fetch -p")
    # run_command("git branch -vv | grep ': gone]' | awk '{print $1}' | xargs --no-run-if-empty git branch -D")

def docker_clean():
    """Durdurulmuş container'ları, kullanılmayan volume'leri vb. temizler (DEVRE DIŞI)."""
    print("\n--- Docker Temizliği (Devre Dışı) ---")
    print("Bu fonksiyon normalde durmuş container'ları, eski volume/network/image'ları silerdi.")
    print("İstek üzerine temizlik işlemi pasif hale getirildi.")
    print("Yapılacak adımlar normalde şunlar olurdu:")
    print("  1. Durdurulmuş container'ları sil: `docker ps -a -q -f status=exited | xargs --no-run-if-empty docker rm`")
    print("  2. Kullanılmayan volume'leri sil: `docker volume ls -q -f dangling=true | xargs --no-run-if-empty docker volume rm`")
    print("  3. Kullanılmayan network'leri sil: `docker network ls -q -f dangling=true | xargs --no-run-if-empty docker network rm`")
    print("  4. Eski (dangling) imajları sil: `docker images -q -f dangling=true | xargs --no-run-if-empty docker rmi`")
    # GERÇEK KOMUTLAR YORUM SATIRI HALİNDE:
    # print("Durdurulmuş Docker container'ları temizleniyor...")
    # run_command("docker ps -a -q -f status=exited | xargs --no-run-if-empty docker rm")
    # print("Kullanılmayan Docker volume'leri temizleniyor (dangling)...")
    # run_command("docker volume ls -q -f dangling=true | xargs --no-run-if-empty docker volume rm")
    # print("Kullanılmayan Docker network'leri temizleniyor...")
    # run_command("docker network ls -q -f dangling=true | xargs --no-run-if-empty docker network rm")
    # print("Eski (dangling) Docker imajları temizleniyor...")
    # run_command("docker images -q -f dangling=true | xargs --no-run-if-empty docker rmi")

def my_ips():
    """Yerel ve genel IP adreslerini gösterir."""
    print("\n--- IP Adresleri ---")
    try:
        hostname = socket.gethostname()
        # Tüm yerel IP'leri bulmaya çalışalım (daha kapsamlı)
        local_ips = socket.getaddrinfo(hostname, None)
        print(f"Yerel Host Adı: {hostname}")
        printed_ips = set()
        for item in local_ips:
            ip_addr = item[4][0]
            if ip_addr not in printed_ips and ':' not in ip_addr: # IPv4 adreslerini alalım
                 print(f"Yerel IP Adresi: {ip_addr}")
                 printed_ips.add(ip_addr)
        # Basit fallback
        if not printed_ips:
             local_ip = socket.gethostbyname(hostname)
             print(f"Yerel IP Adresi (Fallback): {local_ip}")

    except socket.gaierror:
        print("Yerel IP adresi alınamadı.")
    except Exception as e:
        print(f"Yerel IP alınırken hata: {e}")

    print("Genel IP Adresi alınıyor (curl ifconfig.me)...")
    # Genel IP için harici bir servis kullanmak gerekir
    success, _ = run_command("curl -s ifconfig.me || curl -s https://api.ipify.org")
    if not success:
        print("Genel IP adresi alınamadı. İnternet bağlantınızı veya curl komutunu kontrol edin.")

def mkcd(dir_name):
    """Yeni bir dizin oluşturur. DİKKAT: Shell'in dizinini DEĞİŞTİRMEZ."""
    print(f"\n--- Dizin Oluştur: {dir_name} ---")
    try:
        path = Path(dir_name)
        path.mkdir(parents=True, exist_ok=True)
        print(f"Dizin oluşturuldu veya zaten mevcut: {path.resolve()}")
        print("ÖNEMLİ: Bu komut shell'inizin çalışma dizinini DEĞİŞTİRMEZ.")
        print(f"Oluşturulan dizine gitmek için manuel olarak `cd {dir_name}` yazmalısınız.")
    except Exception as e:
        print(f"Hata: Dizin oluşturulamadı '{dir_name}': {e}", file=sys.stderr)

def fsearch(pattern, search_path="."):
    """Belirtilen dizinde dosya adı desenine göre arama yapar (find alternatifi)."""
    print(f"\n--- Dosya Ara: '{pattern}' deseni '{search_path}' içinde ---")
    search_path_obj = Path(search_path)
    if not search_path_obj.is_dir():
         print(f"Hata: Arama yolu bulunamadı veya bir dizin değil: '{search_path}'", file=sys.stderr)
         return
    try:
        found_count = 0
        for entry in search_path_obj.rglob(pattern):
            print(entry)
            found_count += 1
        if found_count == 0:
            print("Eşleşen dosya bulunamadı.")
        else:
            print(f"Toplam {found_count} dosya bulundu.")
    except Exception as e:
        print(f"Arama sırasında hata: {e}", file=sys.stderr)

def serve_here(port=8000):
    """Bulunulan dizini basit bir HTTP sunucusu ile yayınlar."""
    try:
        port = int(port)
        host = "0.0.0.0"
        print(f"\n--- HTTP Sunucu Başlatılıyor ---")
        print(f"Bulunulan dizin (`{Path.cwd()}`) şu adreste yayınlanacak:")
        print(f"  http://{host}:{port}")
        print(f"Ağdaki diğer cihazlardan erişim için yerel IP adresinizi kullanın (örn: http://YEREL_IP:{port})")
        print("Sunucuyu durdurmak için Ctrl+C basın.")
        # Python'un kendi http sunucusunu çalıştırır
        run_command(f"{sys.executable} -m http.server {port} --bind {host}")
    except ValueError:
        print("Hata: Geçersiz port numarası. Sayısal bir değer girin.", file=sys.stderr)
    except Exception as e:
        print(f"Sunucu başlatılırken hata: {e}", file=sys.stderr)

def top_procs(n=10):
    """CPU ve Belleği en çok kullanan N süreci gösterir."""
    try:
        n = int(n)
        if n <= 0:
            print("Hata: Süreç sayısı pozitif bir tam sayı olmalı.", file=sys.stderr)
            return
        print(f"\n--- En Çok Kaynak Kullanan {n} Süreç ---")
        print(f"\n== CPU Kullanımına Göre İlk {n} Süreç ==")
        # Platforma göre ps komutu farklılık gösterebilir ama aux genellikle çalışır
        run_command(f"ps aux --sort=-%cpu | head -n {n+1}") # +1 başlık satırı için
        print(f"\n== Bellek Kullanımına Göre İlk {n} Süreç ==")
        run_command(f"ps aux --sort=-%mem | head -n {n+1}") # +1 başlık satırı için
    except ValueError:
        print("Hata: Geçersiz süreç sayısı. Sayısal bir değer girin.", file=sys.stderr)

def crypto_price(symbol="bitcoin"):
    """CoinGecko API kullanarak kripto para fiyatını gösterir."""
    print(f"\n--- Kripto Fiyatı: {symbol.upper()} ---")
    try:
        # requests kütüphanesinin varlığını tekrar kontrol edelim
        requests
    except NameError:
        print("Hata: 'requests' kütüphanesi gerekli.", file=sys.stderr)
        print("Lütfen 'pip install requests' komutu ile kurun.", file=sys.stderr)
        return

    # CoinGecko API anahtarını ENV_VARS'tan al (os.getenv zaten yukarıda halletti)
    api_key = ENV_VARS.get("COINGECKO_API_KEY", "")
    headers = {}
    params = {
        'ids': symbol.lower(),
        'vs_currencies': 'usd'
    }
    # Ücretli CoinGecko API anahtarı için header gerekebilir, dokümantasyona bakın.
    # Ücretsiz API için genelde gerekmez. Anahtar varsa parametre olarak ekleyebiliriz.
    # if api_key and api_key != "YOUR_COINGECKO_API_KEY_HERE_OR_NONE":
    #     params['x_cg_demo_api_key'] = api_key # Ücretsiz demo anahtarı için parametre

    url = "https://api.coingecko.com/api/v3/simple/price"

    try:
        # Timeout eklemek iyi bir pratik
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status() # HTTP hatalarını kontrol et (4xx, 5xx)
        data = response.json()

        coin_id = symbol.lower()
        if coin_id in data and 'usd' in data[coin_id]:
            price = data[coin_id]['usd']
            print(f"{symbol.upper()} Fiyatı (USD): ${price:,.2f}")
        else:
            print(f"Hata: '{symbol}' için fiyat bilgisi bulunamadı. CoinGecko ID'sini doğru girdiğinizden emin olun.")
            print("Yanıt:", data)

    except requests.exceptions.Timeout:
        print("Hata: CoinGecko API isteği zaman aşımına uğradı.", file=sys.stderr)
    except requests.exceptions.RequestException as e:
        print(f"API isteği sırasında hata: {e}", file=sys.stderr)
    except json.JSONDecodeError:
        print("API'den geçersiz JSON yanıtı alındı.", file=sys.stderr)

def copy_pubkey(key_path="~/.ssh/id_rsa.pub"):
    """SSH public anahtarını panoya kopyalar."""
    print(f"\n--- SSH Public Key Kopyala: {key_path} ---")
    key_file = Path(key_path).expanduser().resolve()
    if not key_file.is_file():
        print(f"Hata: Public key dosyası bulunamadı: {key_file}", file=sys.stderr)
        return

    try:
        key_content = key_file.read_text().strip()
        # Platforma göre pano komutunu belirle
        current_os = platform.system()
        cmd = None
        if current_os == "Darwin": # macOS
            cmd = "pbcopy"
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, text=True)
            process.communicate(input=key_content)
        elif current_os == "Linux":
             if shutil.which("xclip"):
                 cmd = "xclip -selection clipboard -in"
                 process = subprocess.Popen(cmd.split(), stdin=subprocess.PIPE, text=True)
                 process.communicate(input=key_content)
             elif shutil.which("xsel"):
                 cmd = "xsel --clipboard --input"
                 process = subprocess.Popen(cmd.split(), stdin=subprocess.PIPE, text=True)
                 process.communicate(input=key_content)
             else:
                 print("Hata: Panoya kopyalama için 'xclip' veya 'xsel' kurulu olmalı.", file=sys.stderr)
                 print("Anahtar içeriği aşağıda gösteriliyor:")
                 print("-" * 20)
                 print(key_content)
                 print("-" * 20)
                 return
        elif current_os == "Windows":
            cmd = "clip"
            subprocess.run(cmd, input=key_content, text=True, check=True, shell=True) # Windows'ta shell=True gerekebilir
        else:
            print(f"Hata: Bu platform ({current_os}) için pano desteği eklenmedi.", file=sys.stderr)
            print("Anahtar içeriği aşağıda gösteriliyor:")
            print("-" * 20)
            print(key_content)
            print("-" * 20)
            return

        print(f"Public key ({key_file}) içeriği panoya kopyalandı.")

    except Exception as e:
        print(f"Anahtar panoya kopyalanırken hata: {e}", file=sys.stderr)
        print("Anahtar içeriği aşağıda gösteriliyor:")
        print("-" * 20)
        try:
             print(key_file.read_text().strip())
        except Exception as read_e:
             print(f"Anahtar dosyası tekrar okunamadı: {read_e}")
        print("-" * 20)


# === YENİ EKLENEN ÖRNEK FONKSİYONLAR ===

def generate_password(length=16):
    """Güvenli rastgele parola üretir."""
    try:
        length = int(length)
        if length < 8:
            print("Uyarı: Güvenlik için en az 8 karakterli parola önerilir.", file=sys.stderr)
            length = 8
        if length > 1024:
             print("Uyarı: Parola uzunluğu 1024 ile sınırlandırıldı.", file=sys.stderr)
             length = 1024

        alphabet = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(alphabet) for i in range(length))
        print(f"\n--- Güvenli Parola ({length} karakter) ---")
        print(password)
        # Güvenlik Notu: Üretilen parolayı panoya kopyalamak riskli olabilir.
        # copy_to_clipboard(password) # İstenirse eklenebilir ama dikkatli kullanılmalı.

    except ValueError:
        print("Hata: Parola uzunluğu sayısal bir değer olmalı.", file=sys.stderr)

def url_encode_decode(mode, text):
    """Verilen metni URL formatında kodlar veya çözer."""
    print(f"\n--- URL {mode.capitalize()} ---")
    if mode == "encode":
        encoded_text = urllib.parse.quote(text)
        print(f"Orijinal: {text}")
        print(f"Kodlanmış: {encoded_text}")
    elif mode == "decode":
        try:
            decoded_text = urllib.parse.unquote(text)
            print(f"Orijinal: {text}")
            print(f"Çözülmüş: {decoded_text}")
        except Exception as e:
             print(f"URL çözülürken hata: {e}", file=sys.stderr)
    else:
        print("Hata: Mod 'encode' veya 'decode' olmalıdır.", file=sys.stderr)

def base64_encode_decode(mode, text):
    """Verilen metni Base64 formatında kodlar veya çözer."""
    print(f"\n--- Base64 {mode.capitalize()} ---")
    if mode == "encode":
        try:
            encoded_bytes = base64.b64encode(text.encode('utf-8'))
            encoded_text = encoded_bytes.decode('utf-8')
            print(f"Orijinal Metin: {text}")
            print(f"Base64 Kodlanmış: {encoded_text}")
        except Exception as e:
            print(f"Base64 kodlama sırasında hata: {e}", file=sys.stderr)
    elif mode == "decode":
        try:
            decoded_bytes = base64.b64decode(text.encode('utf-8'))
            decoded_text = decoded_bytes.decode('utf-8')
            print(f"Base64 Metin: {text}")
            print(f"Çözülmüş Metin: {decoded_text}")
        except (binascii.Error, UnicodeDecodeError) as e:
            print(f"Base64 çözme sırasında hata: {e}", file=sys.stderr)
            print("Girdi geçerli bir Base64 veya UTF-8 formatında olmayabilir.")
        except Exception as e:
            print(f"Base64 çözme sırasında beklenmedik hata: {e}", file=sys.stderr)

    else:
        print("Hata: Mod 'encode' veya 'decode' olmalıdır.", file=sys.stderr)

def show_calendar(year_str=None, month_str=None):
    """Belirtilen ayın veya geçerli ayın takvimini gösterir."""
    print("\n--- Takvim ---")
    try:
        now = datetime.date.today()
        year = int(year_str) if year_str else now.year
        month = int(month_str) if month_str else now.month

        if not (1 <= month <= 12):
             print("
