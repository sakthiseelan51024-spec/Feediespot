"""
FOODIE SPOT — College Canteen System
Backend: Python Flask + MySQL
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector
import jwt
import qrcode
import io
import base64
import datetime
import random
from functools import wraps

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# ─── CONFIG ────────────────────────────────────────────
DB_CONFIG = {
    'host':     'localhost',
    'user':     'root',
    'password': 'Seelan@2004',  # ← Change this!
    'database': 'canteen_db',
}
JWT_SECRET = 'foodiespot_secret_2024'

# ─── DB ────────────────────────────────────────────────
def get_db():
    return mysql.connector.connect(**DB_CONFIG)

# ─── JWT ───────────────────────────────────────────────
def make_jwt(payload):
    payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(hours=12)
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '').strip()
        if not token:
            return jsonify({'message': 'Unauthorized'}), 401
        try:
            request.admin = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        except Exception:
            return jsonify({'message': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated

# ─── HELPERS ───────────────────────────────────────────
def gen_token():
    now = datetime.datetime.now()
    return f"F{now.strftime('%H%M')}{random.randint(100,999)}"

def current_slot():
    h = datetime.datetime.now().hour
    if 7 <= h < 10:  return 'morning'
    if 10 <= h < 13: return 'break'
    return 'lunch'

def make_qr(data: str) -> str:
    """Generate QR code and return as base64 data URL"""
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1a1a1a", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()

# ══════════════════════════════════════════════════════
#  SERVE PAGES
# ══════════════════════════════════════════════════════
@app.route('/')
def root():
    return send_from_directory('../frontend/customer', 'index.html')

@app.route('/customer')
@app.route('/customer/')
def customer_root():
    return send_from_directory('../frontend/customer', 'index.html')

@app.route('/customer/<path:p>')
def customer_files(p):
    return send_from_directory('../frontend/customer', p)

@app.route('/admin')
@app.route('/admin/')
def admin_root():
    return send_from_directory('../frontend/admin', 'login.html')

@app.route('/admin/<path:p>')
def admin_files(p):
    return send_from_directory('../frontend/admin', p)

# ══════════════════════════════════════════════════════
#  AUTH
# ══════════════════════════════════════════════════════
@app.route('/api/auth/login', methods=['POST'])
def login():
    d = request.get_json()
    username = d.get('username', '').strip()
    password = d.get('password', '').strip()
    if not username or not password:
        return jsonify({'message': 'Enter username and password'}), 400
    db = get_db()
    cur = db.cursor(dictionary=True)
    try:
        cur.execute('SELECT * FROM admins WHERE username=%s AND password=%s', (username, password))
        admin = cur.fetchone()
        if not admin:
            return jsonify({'message': 'Invalid credentials'}), 400
        token = make_jwt({'id': admin['id'], 'username': admin['username']})
        return jsonify({'token': token, 'username': admin['username']})
    finally:
        cur.close(); db.close()

# ══════════════════════════════════════════════════════
#  MENU
# ══════════════════════════════════════════════════════
@app.route('/api/menu', methods=['GET'])
def menu_public():
    category = request.args.get('category')
    db = get_db()
    cur = db.cursor(dictionary=True)
    try:
        if category:
            cur.execute('SELECT * FROM menu_items WHERE is_available=1 AND category=%s ORDER BY name', (category,))
        else:
            cur.execute('SELECT * FROM menu_items WHERE is_available=1 ORDER BY category, name')
        rows = cur.fetchall()
        for r in rows:
            r['price'] = float(r['price'])
        return jsonify(rows)
    finally:
        cur.close(); db.close()

@app.route('/api/menu/all', methods=['GET'])
@require_admin
def menu_all():
    db = get_db()
    cur = db.cursor(dictionary=True)
    try:
        cur.execute('SELECT * FROM menu_items ORDER BY category, name')
        rows = cur.fetchall()
        for r in rows:
            r['price'] = float(r['price'])
        return jsonify(rows)
    finally:
        cur.close(); db.close()

@app.route('/api/menu', methods=['POST'])
@require_admin
def menu_add():
    d = request.get_json()
    name = d.get('name','').strip()
    price = float(d.get('price', 0))
    category = d.get('category','')
    description = d.get('description','').strip()
    if not name or not price or not category:
        return jsonify({'message': 'name, price, category required'}), 400
    db = get_db()
    cur = db.cursor()
    try:
        cur.execute(
            'INSERT INTO menu_items (name,price,category,description) VALUES (%s,%s,%s,%s)',
            (name, price, category, description)
        )
        db.commit()
        return jsonify({'message': 'Added', 'id': cur.lastrowid})
    finally:
        cur.close(); db.close()

@app.route('/api/menu/<int:iid>', methods=['PUT'])
@require_admin
def menu_update(iid):
    d = request.get_json()
    db = get_db()
    cur = db.cursor()
    try:
        cur.execute(
            'UPDATE menu_items SET name=%s,price=%s,category=%s,description=%s,is_available=%s WHERE id=%s',
            (d['name'], float(d['price']), d['category'], d.get('description',''), int(d.get('is_available',1)), iid)
        )
        db.commit()
        return jsonify({'message': 'Updated'})
    finally:
        cur.close(); db.close()

@app.route('/api/menu/<int:iid>', methods=['DELETE'])
@require_admin
def menu_delete(iid):
    db = get_db()
    cur = db.cursor()
    try:
        cur.execute('DELETE FROM menu_items WHERE id=%s', (iid,))
        db.commit()
        return jsonify({'message': 'Deleted'})
    finally:
        cur.close(); db.close()

@app.route('/api/menu/<int:iid>/toggle', methods=['PATCH'])
@require_admin
def menu_toggle(iid):
    db = get_db()
    cur = db.cursor()
    try:
        cur.execute('UPDATE menu_items SET is_available = NOT is_available WHERE id=%s', (iid,))
        db.commit()
        return jsonify({'message': 'Toggled'})
    finally:
        cur.close(); db.close()

# ══════════════════════════════════════════════════════
#  ORDERS
# ══════════════════════════════════════════════════════
@app.route('/api/orders', methods=['POST'])
def order_place():
    """Customer places order → token + QR code returned"""
    d = request.get_json()
    items         = d.get('items', [])
    customer_name = (d.get('customer_name') or 'Guest').strip()

    if not items:
        return jsonify({'message': 'No items'}), 400

    token_number = gen_token()
    slot         = current_slot()
    total        = sum(float(i['price']) * int(i['quantity']) for i in items)

    db = get_db()
    cur = db.cursor()
    try:
        cur.execute(
            'INSERT INTO orders (token_number,customer_name,total_amount,time_slot) VALUES (%s,%s,%s,%s)',
            (token_number, customer_name, total, slot)
        )
        order_id = cur.lastrowid

        for item in items:
            cur.execute(
                'INSERT INTO order_items (order_id,menu_item_id,item_name,quantity,unit_price) VALUES (%s,%s,%s,%s,%s)',
                (order_id, item['menu_item_id'], item['name'], int(item['quantity']), float(item['price']))
            )

        db.commit()

        # Build a rich QR payload: token + order summary
        qr_text = f"FOODIESPOT\nToken: {token_number}\nTotal: Rs.{total:.0f}\nItems: {', '.join(i['name']+' x'+str(i['quantity']) for i in items)}"
        qr_data_url = make_qr(qr_text)

        return jsonify({
            'token_number': token_number,
            'order_id':     order_id,
            'total_amount': total,
            'qr_code':      qr_data_url
        })
    except Exception as e:
        db.rollback()
        return jsonify({'message': str(e)}), 500
    finally:
        cur.close(); db.close()


@app.route('/api/orders', methods=['GET'])
@require_admin
def orders_list():
    status = request.args.get('status', 'all')
    db = get_db()
    cur = db.cursor(dictionary=True)
    try:
        sql = """
            SELECT o.*,
              GROUP_CONCAT(CONCAT(oi.item_name,' x',oi.quantity) SEPARATOR ' | ') AS items_list
            FROM orders o
            LEFT JOIN order_items oi ON oi.order_id = o.id
            WHERE DATE(o.created_at) = CURDATE()
        """
        params = []
        if status and status != 'all':
            sql += ' AND o.status=%s'
            params.append(status)
        sql += ' GROUP BY o.id ORDER BY o.created_at DESC'
        cur.execute(sql, params)
        rows = cur.fetchall()
        for r in rows:
            r['total_amount'] = float(r['total_amount'])
            if r.get('created_at'):
                r['created_at'] = r['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        return jsonify(rows)
    finally:
        cur.close(); db.close()


@app.route('/api/orders/<int:oid>/status', methods=['PATCH'])
@require_admin
def order_status(oid):
    status = request.get_json().get('status')
    db = get_db()
    cur = db.cursor()
    try:
        cur.execute('UPDATE orders SET status=%s WHERE id=%s', (status, oid))
        db.commit()
        return jsonify({'message': 'Updated'})
    finally:
        cur.close(); db.close()


@app.route('/api/orders/stats/today', methods=['GET'])
@require_admin
def order_stats():
    db = get_db()
    cur = db.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT COUNT(*) total, IFNULL(SUM(total_amount),0) revenue,
              SUM(status='pending') pending, SUM(status='preparing') preparing,
              SUM(status='ready') ready, SUM(status='completed') completed
            FROM orders WHERE DATE(created_at)=CURDATE()
        """)
        row = cur.fetchone()
        row['revenue'] = float(row['revenue'])
        return jsonify(row)
    finally:
        cur.close(); db.close()


@app.route('/api/orders/<int:oid>/qr', methods=['GET'])
@require_admin
def order_qr(oid):
    db = get_db()
    cur = db.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT o.token_number, o.customer_name, o.total_amount,
              GROUP_CONCAT(CONCAT(oi.item_name,' x',oi.quantity) SEPARATOR ', ') AS items_list
            FROM orders o
            LEFT JOIN order_items oi ON oi.order_id=o.id
            WHERE o.id=%s GROUP BY o.id
        """, (oid,))
        row = cur.fetchone()
        if not row:
            return jsonify({'message': 'Not found'}), 404
        qr_text = f"FOODIESPOT\nToken: {row['token_number']}\nTotal: Rs.{float(row['total_amount']):.0f}\nItems: {row['items_list']}"
        return jsonify({'qr_code': make_qr(qr_text), 'token': row['token_number']})
    finally:
        cur.close(); db.close()


# ── Entrance QR (scan to open order page)
@app.route('/api/qr/generate', methods=['GET'])
@require_admin
def qr_generate():
    url = request.args.get('url', 'http://localhost:5000')
    return jsonify({'qr': make_qr(url), 'url': url})


# ══════════════════════════════════════════════════════
if __name__ == '__main__':
    print('\n🍔 FOODIE SPOT — Server starting...')
    print('📱 Customer  → http://localhost:5000')
    print('🔐 Admin     → http://localhost:5000/admin/login.html\n')
    app.run(host='0.0.0.0', port=5000, debug=True)
