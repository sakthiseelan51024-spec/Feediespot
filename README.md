# 🍔 FOODIE SPOT — College Canteen System

## Setup (4 Steps)

### 1. MySQL — Run schema
```sql
source backend/schema.sql
```

### 2. Change DB password
Open `backend/app.py` line 18:
```python
'password': 'your_mysql_password',  ← PUT YOUR PASSWORD
```

### 3. Install Python packages
```bash
cd backend
pip install -r requirements.txt
```

### 4. Start server
```bash
python app.py
```

---

## URLs
- **Students** → http://localhost:5000  (no login needed)
- **Admin**    → http://localhost:5000/admin/login.html
- **Login**    → admin / admin123

---

## Features
- ✅ Same design on all pages (green theme)
- ✅ Student orders → Token Number + QR Code generated
- ✅ QR code contains token + item summary → scannable at counter
- ✅ Admin sees each order's QR code (click "View Student QR")
- ✅ Admin manages menu — add/edit/delete/toggle/set price
- ✅ Admin updates order status: Pending → Preparing → Ready → Collected
- ✅ Today's revenue stats
- ✅ Entrance QR code (students scan to open order page)
