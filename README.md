# Fantasy Trading Platform

A backend API for a fantasy-world trading platform where users (elves, wizards, dwarves) can trade weapons. The system includes user inventory, trade offers, and trade history.

---
## 📌 Features
- **Users**: Elves, Wizards, and Dwarves (no functional difference).
- **Weapons**: Swords, Staffs, Axes, with **variants** (Red, Blue, Green, etc.).
- **Trade Offers**: Users can offer a trade, accept/reject offers.
- **Inventory Management**: Users have an inventory that updates with trade execution.
- **Trade History**: View sent/received offers, filter by status and date range.

---
## 🏗️ Design Overview

### **1️⃣ Architecture**
The backend follows a **modular and extendable** architecture using **Django and Django REST Framework (DRF)**. The system is built to support future enhancements like offer limits, trade analytics, and a ledger system.

### **2️⃣ Database Schema**
- **User Model**: Represents users in the system (Elves, Wizards, Dwarves).
- **Weapon Model**: Represents different weapon types (Sword, Staff, Axe).
- **WeaponVariant Model**: Tracks color variations of weapons (Red, Blue, Green).
- **Inventory Model**: Stores user inventory details.
- **TradeOffer Model**: Captures trade offers between users.
- **TradeItem Model**: Stores items involved in a trade.

### **3️⃣ Business Logic**
- **Trade Validation**: Ensures a user has sufficient inventory before making an offer.
- **Transaction Handling**: Uses database transactions for atomic trade execution.
- **Offer Processing**: Allows users to accept or reject trade offers.
- **Historical Data**: Users can view trade history with filters.

---
## 🚀 Setup & Installation

### 1️⃣ **Clone the Repository**
```sh
git clone https://github.com/your-repo/fantasy-trading.git
cd fantasy-trading
```

### 2️⃣ **Create & Activate Virtual Environment**
```sh
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 3️⃣ **Install Dependencies**
```sh
pip install -r requirements.txt
```

### 4️⃣ **Apply Migrations**
```sh
python manage.py migrate
```

### 5️⃣ **Seed Sample Data**
```sh
python manage.py seed_data
```

### 6️⃣ **Run the Server**
```sh
python manage.py runserver
```

The API will be available at **http://127.0.0.1:8000/**

---
## 🔑 Environment Variables

Create a `.env` file in the root directory with the following structure:

```
# Database configuration
DB_NAME=fantasy_world
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Django secret key
SECRET_KEY=your_secret_key

# Debug mode (set to False in production)
DEBUG=True
```

Ensure the `.env` file is not committed to version control by adding it to `.gitignore`.

---
## 📡 API Endpoints & Sample Requests

### **1️⃣ View User Inventory**
**Endpoint:** `GET /inventory/<user_id>/`
```sh
curl -X GET "http://127.0.0.1:8000/inventory/1/"
```

---
### **2️⃣ Create a Trade Offer**
**Endpoint:** `POST /trade-offer/`
```sh
curl -X POST "http://127.0.0.1:8000/trade-offer/" \
     -H "Content-Type: application/json" \
     -d '{
           "sender_id": 1,
           "receiver_id": 2,
           "offered_items": [
               {"weapon_id": 1, "variant_id": 1, "quantity": 2}
           ],
           "requested_items": [
               {"weapon_id": 2, "variant_id": 2, "quantity": 1}
           ]
        }'
```

---
### **3️⃣ Accept/Reject a Trade Offer**
**Endpoint:** `PATCH /trade-offer/<trade_offer_id>/`
```sh
curl -X PATCH "http://127.0.0.1:8000/trade-offer/1/" \
     -H "Content-Type: application/json" \
     -d '{"receiver_id": 2, "action": "ACCEPT"}'
```
To **reject** the offer, change `"action": "ACCEPT"` to `"action": "REJECT"`.

---
### **4️⃣ View Trade History**
**Endpoint:** `GET /trade-offer/history/?user_id=<user_id>`
```sh
curl -X GET "http://127.0.0.1:8000/trade-offer/history/?user_id=2"
```

Optional filters:
- `?type=sent` → Sent trade offers
- `?type=received` → Received trade offers
- `?status=2` → Accepted offers
- `?start_date=2025-03-01&end_date=2025-03-10` → Offers within date range

---
## ✅ Running Tests
To ensure everything works correctly, run:
```sh
python manage.py test
```
