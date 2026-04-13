import os
import uuid
import sqlite3
from flask import Flask, request, send_file, redirect, url_for, render_template_string
from functools import wraps

app = Flask(__name__)
DB_PATH = '/data/database.db'

# --- GÜVENLİK ---
ADMIN_USER = "admin" 
ADMIN_PASS = "formx123"

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not (auth.username == ADMIN_USER and auth.password == ADMIN_PASS):
            return ('Yetkisiz Giriş!', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
        return f(*args, **kwargs)
    return decorated

def init_db():
    if not os.path.exists('/data'): os.makedirs('/data')
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS forms 
                   (id TEXT PRIMARY KEY, api_key TEXT, product_name TEXT, 
                    price TEXT, seller_id TEXT)''')
    conn.close()

init_db()

@app.route('/')
def home():
    return redirect(url_for('create'))

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        f_id = str(uuid.uuid4().hex)[:8]
        data = (f_id, request.form['api_key'], request.form['product_name'], 
                request.form['price'], request.form['seller_id'])
        
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute('INSERT INTO forms VALUES (?,?,?,?,?)', data)
            conn.commit()
            conn.close()
            return f"<h3>Form Oluşturuldu!</h3> Link: <a href='/form/{f_id}'>{request.host_url}form/{f_id}</a>"
        except Exception as e:
            return f"Hata: {str(e)}"
    
    return '''
        <h2>ShopierFormX - Yeni Form</h2>
        <form method="post">
            <input name="api_key" placeholder="API Key" required><br><br>
            <input name="product_name" placeholder="Ürün Adı" required><br><br>
            <input name="price" placeholder="Fiyat (Örn: 50.00)" required><br><br>
            <input name="seller_id" placeholder="Satıcı ID"><br><br>
            <button type="submit">Oluştur</button>
        </form>
    '''

@app.route('/form/<f_id>', methods=['GET', 'POST'])
def show_form(f_id):
    conn = sqlite3.connect(DB_PATH)
    form = conn.execute('SELECT * FROM forms WHERE id = ?', (f_id,)).fetchone()
    conn.close()
    
    if not form:
        return "<h3>Hata 404: Form bulunamadı!</h3>", 404

    if request.method == 'POST':
        return f"Ödeme sayfasına yönlendiriliyorsunuz... (Ürün: {form[2]})"

    return f'''
        <h1>{form[2]}</h1>
        <p>Tutar: <b>{form[3]} TL</b></p>
        <form method="post">
            <input name="c_name" placeholder="Ad Soyad" required><br><br>
            <button type="submit">Güvenli Ödeme Yap</button>
        </form>
    '''

if __name__ == '__main__':
    # Termux veya Fly.io fark etmeksizin 0.0.0.0 üzerinden dinler
    app.run(host='0.0.0.0', port=8080)
