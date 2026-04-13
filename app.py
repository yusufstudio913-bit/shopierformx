import os
import uuid
import sqlite3
from flask import Flask, request, send_file, redirect, url_for
from functools import wraps

app = Flask(__name__)
DB_PATH = '/data/database.db'  # Fly.io Volume yolu

# --- GÜVENLİK AYARLARI ---
ADMIN_USER = "admin" 
ADMIN_PASS = "formx123" # Burayı kendine göre değiştir!

def check_auth(username, password):
    return username == ADMIN_USER and password == ADMIN_PASS

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return ('Yetkisiz Giriş!', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
        return f(*args, **kwargs)
    return decorated

# --- VERİTABANI BAŞLATMA ---
def init_db():
    if not os.path.exists('/data'): os.makedirs('/data')
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS forms 
                   (id TEXT PRIMARY KEY, api_key TEXT, product_name TEXT, 
                    price TEXT, seller_id TEXT)''')
    conn.close()

init_db()

# --- YOLLAR (ROUTES) ---

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        f_id = str(uuid.uuid4().hex)[:8]
        data = (f_id, request.form['api_key'], request.form['product_name'], 
                request.form['price'], request.form['seller_id'])
        
        conn = sqlite3.connect(DB_PATH)
        conn.execute('INSERT INTO forms VALUES (?,?,?,?,?)', data)
        conn.commit()
        conn.close()
        return f"<h3>Form Başarıyla Oluşturuldu!</h3> Müşteri Linki: <a href='/form/{f_id}'>{request.host_url}form/{f_id}</a>"
    
    return '''
        <h2>ShopierFormX - Yeni Form</h2>
        <form method="post">
            <input name="api_key" placeholder="API Key" required><br><br>
            <input name="product_name" placeholder="Ürün Adı" required><br><br>
            <input name="price" placeholder="Fiyat (Örn: 50.00)" required><br><br>
            <input name="seller_id" placeholder="Satıcı ID (Opsiyonel)"><br><br>
            <button type="submit">Oluştur</button>
        </form>
    '''

@app.route('/form/<f_id>', methods=['GET', 'POST'])
def show_form(f_id):
    conn = sqlite3.connect(DB_PATH)
    form = conn.execute('SELECT * FROM forms WHERE id = ?', (f_id,)).fetchone()
    conn.close()
    
    if not form: return "Form bulunamadı!", 404

    if request.method == 'POST':
        # Burada Shopier'e yönlendirme mantığı (API isteği) çalışacak
        return f"Ödeme sayfasına yönlendiriliyorsunuz... (Ürün: {form[2]})"

    return f'''
        <h1>{form[2]}</h1>
        <p>Tutar: <b>{form[3]} TL</b></p>
        <hr>
        <form method="post">
            <input name="c_name" placeholder="Adınız Soyadınız" required><br><br>
            <input name="c_email" placeholder="E-posta Adresiniz" required><br><br>
            <button type="submit">Güvenli Ödeme Yap</button>
        </form>
    '''

# --- ADMIN PANELİ (Korumalı) ---

@app.route('/admin/backup')
@requires_auth
def backup_db():
    return send_file(DB_PATH, as_attachment=True)

@app.route('/admin/restore', methods=['GET', 'POST'])
@requires_auth
def restore_db():
    if request.method == 'POST':
        file = request.files['database']
        if file:
            file.save(DB_PATH)
            return "Veritabanı başarıyla güncellendi!"
    return '''
        <h3>Veritabanı Geri Yükle</h3>
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="database">
            <button type="submit">Yükle</button>
        </form>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)