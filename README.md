
SQL Injection Login Bypass Aracı Yardım:
------------------------------------

1. **Login URL'si Girişi**:
   - Script başlarken, kullanıcıdan login formunun URL'sini girmesi istenir.
   - URL girdikten sonra, script formu inceleyerek input alanlarını otomatik tespit eder.

2. **Otomatik Input Tespiti**:
   - Formda yer alan `username` (veya `email`), `password`, ve `csrf_token` alanları otomatik olarak tespit edilir.
   - Eğer bu alanlar otomatik bulunamazsa, kullanıcıdan manuel olarak bu bilgilerin girmesi istenir.

3. **Payload Denemeleri**:
   - Bir dizi SQL Injection payload'ı (örneğin `' OR 1=1 --`) otomatik olarak denenir.
   - Payload'lar, **threading** kullanılarak paralel bir şekilde denenir ve işlem süresi hızlandırılır.

4. **CSRF Token Desteği**:
   - Eğer formda **CSRF token** varsa, bu token otomatik olarak çekilir ve post isteği ile gönderilir.
   - CSRF token yoksa, bu adım atlanır ve normal giriş yapılır.

5. **Başarı Kontrolü**:
   - Form gönderildikten sonra, sayfa içeriği kontrol edilerek başarılı bir giriş olup olmadığı belirlenir.
   - **Anahtar kelimeler** (örneğin `dashboard`, `admin`) sayfada varsa, girişin başarılı olduğu kabul edilir.

6. **Burp Suite Proxy Desteği**:
   - Burp Suite kullanarak, aracın tüm istekleri proxy üzerinden yönlendirilir. Burp Suite'in 127.0.0.1:8080 adresi varsayılan olarak ayarlanmıştır.

7. **Çoklu Thread Desteği**:
   - Payload'lar paralel şekilde çalıştırılır, böylece test süresi hızlandırılır. **thread_count** ile thread sayısı ayarlanabilir.

8. **Hata ve İstisna Yönetimi**:
   - Script her adımda kullanıcıyı bilgilendirir ve hata oluştuğunda düzgün hata mesajları gösterilir.

9. **Manuel Giriş İmkanı**:
   - Otomatik tespit edilemeyen form alanları için kullanıcıdan manuel giriş istenir.
