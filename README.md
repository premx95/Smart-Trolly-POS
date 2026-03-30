# 🛒 SmartTrolley POS

> **A barcode-scanning Point-of-Sale system built into a smart shopping trolley — scan as you shop, pay before you leave.**

---

## 📸 Real-Life Images

<img width="778" height="590" alt="image" src="https://github.com/user-attachments/assets/66c247bb-5ec2-4067-b128-63b2018176cd" />

<img width="1080" height="1046" alt="image" src="https://github.com/user-attachments/assets/c716e2cd-3ff2-49cb-8494-84a23cb83ff0" />


---

## 🏆 Pitched At

We pitched **SmartTrolley** as a business idea at a competition organized by **Zindgi Pakistan**. While we didn't take home the win, the concept stood strong — and we decided to bring it to life in code.

---

## 💡 The Idea

Imagine walking into a supermarket with a trolley that already knows what you've put in it.

**SmartTrolley** is an embedded Point-of-Sale system for smart shopping trolleys. A camera mounted on the trolley continuously scans barcodes as you drop items in. Each product is instantly looked up, added to your running bill, and displayed on a screen right in front of you — so by the time you reach the exit, you're already done.

No queues. No checkout counters. Just scan, pay, and go.

---

## 🔄 How It Works — The Flow

```
Customer picks item
        ↓
Camera detects barcode (OpenCV + pyzbar)
        ↓
Barcode matched against product database (SQLite)
        ↓
Customer confirms quantity via on-screen prompt
        ↓
Item added to live cart (name, price, quantity, total)
        ↓
Running total updated in real time
        ↓
Customer taps "Proceed to Payment"
        ↓
Chooses: Easypaisa / JazzCash / Debit Card
        ↓
✅ Payment confirmed — ready to exit
```

---

## 🖥️ Software Features

| Feature | Description |
|---|---|
| 📷 Live Barcode Scanning | Webcam / camera feed decoded in real time using OpenCV and pyzbar |
| 🗄️ Product Database | SQLite-backed product lookup by barcode (name + price) |
| 🛒 Live Cart | Items added with quantity — duplicates auto-accumulate |
| 💰 Order Summary | Subtotal and total update instantly after every scan |
| 🗑️ Remove Items | Select any cart item and remove it before checkout |
| 💳 Payment Methods | Easypaisa, JazzCash, Debit Card — all supported |
| 🌑 Dark UI | Sleek dark-themed desktop GUI built with Tkinter + ttk |
| 🔒 Thread-Safe | Camera runs in a background thread — GUI stays responsive |

---

## 🧰 Tech Stack

- **Python 3** — core language
- **OpenCV (`cv2`)** — camera access and live video feed
- **pyzbar** — barcode / QR code decoding
- **SQLite3** — lightweight local product database
- **Tkinter + ttk** — desktop GUI (dark-themed, custom-styled)
- **Threading** — non-blocking camera loop

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/premx95/SmartTrolley-POS.git
cd SmartTrolley-POS
```

### 2. Install dependencies
```bash
pip install opencv-python pyzbar
```

> **Note:** `sqlite3` and `tkinter` come built-in with Python — no extra install needed.

### 3. Prepare the database

Before running, make sure a `products.db` SQLite database exists in the same folder with this table structure:

```sql
CREATE TABLE products (
    barcode TEXT PRIMARY KEY,
    name    TEXT NOT NULL,
    price   REAL NOT NULL
);
```

You can insert products manually or build a seeding script.

### 4. Run the app
```bash
python RealTrolly.py
```

> A camera window will open for scanning. Press **Q** in the camera window to stop scanning manually.

---

## 🗂️ Project Structure

```
SmartTrolley-POS/
│
├── RealTrolly.py            # Main application (GUI + scanning + billing logic)
├── products.db     # SQLite product database (create before running)
└── README.md       # You are here
```

---

## 🌟 The Story

This project started as a **theory** — an idea we walked into a competition with, armed with nothing but a concept and the belief that shopping could be smarter. We presented it at a business idea pitching competition organized by **Zindgi Pakistan**.

We didn't win.

But the idea never left. So instead of letting it stay on a slide deck, we built it. This repository is proof that a good idea deserves to be more than a pitch.

---

## 📌 Future Improvements

- [ ] Weight sensor integration for produce items
- [ ] Admin panel to manage the product database
- [ ] Receipt printing / digital receipt via SMS or email
- [ ] Cloud-synced inventory
- [ ] Anti-theft detection (item removed without scan)
- [ ] Mobile companion app for customers

---

## ⚖️ License

**All Rights Reserved.**

This project and all its contents (code, design, concept) are the intellectual property of the creators. No part of this project may be copied, modified, distributed, or reused in any form without explicit written permission from the authors.

© 2025 SmartTrolley All rights reserved.
