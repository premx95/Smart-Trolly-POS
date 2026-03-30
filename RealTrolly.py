import cv2 # OpenCV for camera access
from pyzbar.pyzbar import decode # pyzbar for barcode decoding
import sqlite3 # SQLite for database access
import tkinter as tk # Tkinter for GUI
from tkinter import ttk, messagebox # Additional Tkinter components
import threading  # Threading for running camera in a separate thread

# ─────────────────────────────────────────────────────────────────────────────
# THEME / STYLE CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
BG_DARK      = "#0D0F14"
BG_CARD      = "#141720"
BG_ROW_ALT  = "#1A1E2A"
ACCENT       = "#00C896"          # emerald-green accent
ACCENT_DIM   = "#00915F"
TEXT_PRIMARY = "#F0F2F8"
TEXT_SEC     = "#8A91A8"
TEXT_DIM     = "#4A5068"
RED          = "#FF4B6E"
BORDER       = "#252A3A"
FONT_HEAD    = ("Segoe UI", 10, "bold")
FONT_BODY    = ("Segoe UI", 10)
FONT_SMALL   = ("Segoe UI", 8)
FONT_TITLE   = ("Segoe UI Semibold", 16, "bold")
FONT_TOTAL   = ("Segoe UI", 22, "bold")
FONT_BTN     = ("Segoe UI", 10, "bold")

# ─────────────────────────────────────────────────────────────────────────────
# GUI Class  (all logic identical to original)
# ─────────────────────────────────────────────────────────────────────────────
class SmartTrolleyApp:
    def __init__(self, root):
        self.conn = sqlite3.connect("products.db")
        self.cursor = self.conn.cursor()

        self.root = root
        self.root.title("SmartTrolley  •  Point of Sale")
        self.root.geometry("780x560")
        self.root.configure(bg=BG_DARK)
        self.root.resizable(True, True)
        self.root.minsize(680, 480)

        self.billing_data = {}
        self._build_ui()

        # Start scanning thread (same as original)
        self.scanning = True
        self.last_scanned_barcode = None
        self.thread = threading.Thread(target=self.scan_barcode, daemon=True)
        self.thread.start()

    # ── UI Construction ───────────────────────────────────────────────────────
    def _build_ui(self):
        self._style_ttk()

        # ── Top Header Bar ────────────────────────────────────────────────────
        header = tk.Frame(self.root, bg=BG_CARD, height=60)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        # Logo / brand
        brand = tk.Frame(header, bg=BG_CARD)
        brand.pack(side=tk.LEFT, padx=20, pady=0, fill=tk.Y)

        dot = tk.Label(brand, text="●", fg=ACCENT, bg=BG_CARD,
                       font=("Segoe UI", 20))
        dot.pack(side=tk.LEFT, pady=10, padx=(0, 8))

        title_lbl = tk.Label(brand, text="SmartTrolley", fg=TEXT_PRIMARY,
                             bg=BG_CARD, font=FONT_TITLE)
        title_lbl.pack(side=tk.LEFT, pady=10)

        sub_lbl = tk.Label(brand, text="POS", fg=TEXT_DIM,
                           bg=BG_CARD, font=("Segoe UI", 10))
        sub_lbl.pack(side=tk.LEFT, pady=14, padx=6)

        # Status indicator (right side of header)
        self.status_frame = tk.Frame(header, bg=BG_CARD)
        self.status_frame.pack(side=tk.RIGHT, padx=20, pady=0, fill=tk.Y)

        self.status_dot = tk.Label(self.status_frame, text="◉",
                                   fg=ACCENT, bg=BG_CARD,
                                   font=("Segoe UI", 11))
        self.status_dot.pack(side=tk.LEFT, pady=10)

        self.status_lbl = tk.Label(self.status_frame, text="  SCANNER ACTIVE",
                                   fg=ACCENT, bg=BG_CARD,
                                   font=("Segoe UI", 9, "bold"))
        self.status_lbl.pack(side=tk.LEFT, pady=10)

        # Thin accent divider
        div = tk.Frame(self.root, bg=ACCENT, height=2)
        div.pack(fill=tk.X, side=tk.TOP)

        # ── Main Body ─────────────────────────────────────────────────────────
        body = tk.Frame(self.root, bg=BG_DARK)
        body.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Left: cart table
        left = tk.Frame(body, bg=BG_DARK)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=18, pady=16)

        cart_header = tk.Frame(left, bg=BG_DARK)
        cart_header.pack(fill=tk.X, pady=(0, 8))

        tk.Label(cart_header, text="Cart Items", fg=TEXT_SEC,
                 bg=BG_DARK, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)

        self.item_count_lbl = tk.Label(cart_header, text="0 items",
                                       fg=TEXT_DIM, bg=BG_DARK,
                                       font=FONT_SMALL)
        self.item_count_lbl.pack(side=tk.RIGHT)

        # Treeview container with rounded look via frame border
        tree_frame = tk.Frame(left, bg=BORDER, bd=0)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(tree_frame,
                                 columns=('Product', 'Price', 'Qty', 'Total'),
                                 show='headings',
                                 style="Cart.Treeview",
                                 selectmode='browse')

        # Column config
        col_cfg = [
            ('Product', 220, tk.W),
            ('Price',    90, tk.CENTER),
            ('Qty',      60, tk.CENTER),
            ('Total',    90, tk.CENTER),
        ]
        for col, w, anchor in col_cfg:
            self.tree.heading(col, text=col.upper(), anchor=anchor)
            self.tree.column(col, width=w, anchor=anchor, minwidth=50)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                             command=self.tree.yview,
                             style="Cart.Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Right: summary panel
        right = tk.Frame(body, bg=BG_CARD, width=210)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 18), pady=16)
        right.pack_propagate(False)

        # Summary card content
        tk.Label(right, text="ORDER SUMMARY", fg=TEXT_DIM,
                 bg=BG_CARD,
                 font=("Segoe UI", 8, "bold")).pack(anchor=tk.W,
                                                     padx=18, pady=(22, 6))

        sep1 = tk.Frame(right, bg=BORDER, height=1)
        sep1.pack(fill=tk.X, padx=14)

        # Subtotal / tax rows
        sub_row = tk.Frame(right, bg=BG_CARD)
        sub_row.pack(fill=tk.X, padx=18, pady=(14, 4))
        tk.Label(sub_row, text="Subtotal", fg=TEXT_SEC,
                 bg=BG_CARD, font=FONT_BODY).pack(side=tk.LEFT)
        self.subtotal_lbl = tk.Label(sub_row, text="Rs 0",
                                     fg=TEXT_PRIMARY, bg=BG_CARD,
                                     font=FONT_BODY)
        self.subtotal_lbl.pack(side=tk.RIGHT)

        tax_row = tk.Frame(right, bg=BG_CARD)
        tax_row.pack(fill=tk.X, padx=18, pady=4)
        tk.Label(tax_row, text="Tax (0%)", fg=TEXT_SEC,
                 bg=BG_CARD, font=FONT_BODY).pack(side=tk.LEFT)
        tk.Label(tax_row, text="Rs 0", fg=TEXT_PRIMARY,
                 bg=BG_CARD, font=FONT_BODY).pack(side=tk.RIGHT)

        sep2 = tk.Frame(right, bg=BORDER, height=1)
        sep2.pack(fill=tk.X, padx=14, pady=10)

        # Total
        total_row = tk.Frame(right, bg=BG_CARD)
        total_row.pack(fill=tk.X, padx=18, pady=(0, 4))
        tk.Label(total_row, text="TOTAL", fg=TEXT_SEC,
                 bg=BG_CARD, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT,
                                                                  anchor=tk.S)

        self.total_label = tk.Label(right, text="Rs 0",
                                    fg=TEXT_PRIMARY, bg=BG_CARD,
                                    font=FONT_TOTAL)
        self.total_label.pack(anchor=tk.E, padx=18, pady=(0, 6))

        sep3 = tk.Frame(right, bg=BORDER, height=1)
        sep3.pack(fill=tk.X, padx=14, pady=8)

        # Scanner tip
        tip = tk.Label(right,
                       text="📷  Point camera at\n    barcode to scan",
                       fg=TEXT_DIM, bg=BG_CARD,
                       font=("Segoe UI", 8),
                       justify=tk.LEFT)
        tip.pack(anchor=tk.W, padx=18, pady=(4, 0))

        # Spacer
        tk.Frame(right, bg=BG_CARD).pack(fill=tk.BOTH, expand=True)

        # Delete button
        self.delete_btn = self._make_btn(right, "🗑  Remove Item",
                                          self.delete_product,
                                          bg=BG_ROW_ALT, fg=TEXT_SEC,
                                          active_bg=RED)
        self.delete_btn.pack(fill=tk.X, padx=14, pady=(0, 8))

        # Pay button
        self.payment_btn = self._make_btn(right, "Proceed to Payment  →",
                                           self.proceed_to_payment,
                                           bg=ACCENT, fg=BG_DARK,
                                           active_bg=ACCENT_DIM,
                                           state=tk.NORMAL)
        self.payment_btn.pack(fill=tk.X, padx=14, pady=(0, 18))

        # ── Bottom Status Bar ─────────────────────────────────────────────────
        statusbar = tk.Frame(self.root, bg=BG_CARD, height=26)
        statusbar.pack(fill=tk.X, side=tk.BOTTOM)
        statusbar.pack_propagate(False)

        self.sb_lbl = tk.Label(statusbar,
                               text="  Waiting for scan…",
                               fg=TEXT_DIM, bg=BG_CARD,
                               font=("Segoe UI", 8))
        self.sb_lbl.pack(side=tk.LEFT, padx=8, pady=4)

        tk.Label(statusbar,
                 text="Press  Q  in camera window to stop  •  SmartTrolley v2.0  ",
                 fg=TEXT_DIM, bg=BG_CARD,
                 font=("Segoe UI", 8)).pack(side=tk.RIGHT, pady=4)

    # ── TTK Style ─────────────────────────────────────────────────────────────
    def _style_ttk(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")

        style.configure("Cart.Treeview",
                        background=BG_CARD,
                        foreground=TEXT_PRIMARY,
                        fieldbackground=BG_CARD,
                        borderwidth=0,
                        relief="flat",
                        rowheight=34,
                        font=FONT_BODY)

        style.configure("Cart.Treeview.Heading",
                        background=BG_DARK,
                        foreground=TEXT_DIM,
                        font=("Segoe UI", 8, "bold"),
                        relief="flat",
                        borderwidth=0)

        style.map("Cart.Treeview",
                  background=[("selected", ACCENT_DIM)],
                  foreground=[("selected", TEXT_PRIMARY)])

        style.map("Cart.Treeview.Heading",
                  background=[("active", BG_DARK)],
                  relief=[("active", "flat")])

        style.configure("Cart.Vertical.TScrollbar",
                        troughcolor=BG_CARD,
                        background=BORDER,
                        borderwidth=0,
                        arrowsize=0,
                        relief="flat")

    # ── Button factory ────────────────────────────────────────────────────────
    def _make_btn(self, parent, text, command,
                  bg=ACCENT, fg=BG_DARK, active_bg=ACCENT_DIM,
                  state=tk.NORMAL):
        btn = tk.Button(parent, text=text, command=command,
                        bg=bg, fg=fg,
                        activebackground=active_bg,
                        activeforeground=fg,
                        font=FONT_BTN,
                        relief="flat",
                        bd=0,
                        cursor="hand2",
                        padx=10, pady=10,
                        state=state)
        btn.bind("<Enter>", lambda e: btn.config(bg=active_bg))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))
        return btn

    # ── Custom dialog (styled) ────────────────────────────────────────────────
    def _styled_askinteger(self, title, prompt):
        """A dark-themed replacement for simpledialog.askinteger."""
        result = [None]

        win = tk.Toplevel(self.root)
        win.title(title)
        win.configure(bg=BG_CARD)
        win.resizable(False, False)
        win.grab_set()
        win.transient(self.root)

        # Center on root
        self.root.update_idletasks()
        rx = self.root.winfo_x() + self.root.winfo_width()  // 2
        ry = self.root.winfo_y() + self.root.winfo_height() // 2
        win.geometry(f"320x180+{rx-160}+{ry-90}")

        tk.Label(win, text=prompt, fg=TEXT_PRIMARY, bg=BG_CARD,
                 font=FONT_BODY, wraplength=290).pack(padx=24, pady=(24, 8))

        entry_frame = tk.Frame(win, bg=BORDER, bd=0)
        entry_frame.pack(padx=24, fill=tk.X)
        entry = tk.Entry(entry_frame, fg=TEXT_PRIMARY, bg=BG_ROW_ALT,
                         insertbackground=ACCENT,
                         font=("Segoe UI", 13),
                         relief="flat", bd=8,
                         justify=tk.CENTER)
        entry.pack(fill=tk.X)
        entry.insert(0, "1")
        entry.select_range(0, tk.END)
        entry.focus()

        def confirm(event=None):
            try:
                val = int(entry.get())
                if val >= 1:
                    result[0] = val
                    win.destroy()
            except ValueError:
                entry.config(bg=RED)
                entry.after(300, lambda: entry.config(bg=BG_ROW_ALT))

        def cancel():
            win.destroy()

        btn_row = tk.Frame(win, bg=BG_CARD)
        btn_row.pack(pady=14, padx=24, fill=tk.X)

        ok_btn = tk.Button(btn_row, text="Confirm", command=confirm,
                           bg=ACCENT, fg=BG_DARK, relief="flat",
                           font=FONT_BTN, cursor="hand2", padx=14, pady=7)
        ok_btn.pack(side=tk.RIGHT, padx=(6, 0))
        ok_btn.bind("<Enter>", lambda e: ok_btn.config(bg=ACCENT_DIM))
        ok_btn.bind("<Leave>", lambda e: ok_btn.config(bg=ACCENT))

        cn_btn = tk.Button(btn_row, text="Cancel", command=cancel,
                           bg=BG_ROW_ALT, fg=TEXT_SEC, relief="flat",
                           font=FONT_BTN, cursor="hand2", padx=14, pady=7)
        cn_btn.pack(side=tk.RIGHT)

        entry.bind("<Return>", confirm)
        win.wait_window()
        return result[0]

    def _styled_askstring(self, title, prompt):
        """A dark-themed replacement for simpledialog.askstring."""
        result = [None]

        win = tk.Toplevel(self.root)
        win.title(title)
        win.configure(bg=BG_CARD)
        win.resizable(False, False)
        win.grab_set()
        win.transient(self.root)

        self.root.update_idletasks()
        rx = self.root.winfo_x() + self.root.winfo_width()  // 2
        ry = self.root.winfo_y() + self.root.winfo_height() // 2
        win.geometry(f"340x190+{rx-170}+{ry-95}")

        tk.Label(win, text=prompt, fg=TEXT_PRIMARY, bg=BG_CARD,
                 font=FONT_BODY, wraplength=300).pack(padx=24, pady=(24, 8))

        entry_frame = tk.Frame(win, bg=BORDER)
        entry_frame.pack(padx=24, fill=tk.X)
        entry = tk.Entry(entry_frame, fg=TEXT_PRIMARY, bg=BG_ROW_ALT,
                         insertbackground=ACCENT,
                         font=("Segoe UI", 12),
                         relief="flat", bd=8)
        entry.pack(fill=tk.X)
        entry.focus()

        def confirm(event=None):
            val = entry.get().strip()
            if val:
                result[0] = val
                win.destroy()

        def cancel():
            win.destroy()

        btn_row = tk.Frame(win, bg=BG_CARD)
        btn_row.pack(pady=14, padx=24, fill=tk.X)

        ok_btn = tk.Button(btn_row, text="Confirm", command=confirm,
                           bg=ACCENT, fg=BG_DARK, relief="flat",
                           font=FONT_BTN, cursor="hand2", padx=14, pady=7)
        ok_btn.pack(side=tk.RIGHT, padx=(6, 0))
        ok_btn.bind("<Enter>", lambda e: ok_btn.config(bg=ACCENT_DIM))
        ok_btn.bind("<Leave>", lambda e: ok_btn.config(bg=ACCENT))

        cn_btn = tk.Button(btn_row, text="Cancel", command=cancel,
                           bg=BG_ROW_ALT, fg=TEXT_SEC, relief="flat",
                           font=FONT_BTN, cursor="hand2", padx=14, pady=7)
        cn_btn.pack(side=tk.RIGHT)

        entry.bind("<Return>", confirm)
        win.wait_window()
        return result[0]

    # ─── ALL ORIGINAL LOGIC BELOW ────────────────────────────────

    def update_billing(self, barcode):
        print(f"Scanned Barcode: '{barcode}'")
        self.cursor.execute(
            "SELECT name, price FROM products WHERE barcode=?",
            (barcode,)
        )
        result = self.cursor.fetchone()

        if result:
            name, price = result
            self.root.after(0, self.ask_for_quantity, name, barcode, price)
        else:
            self.root.after(0, self.product_not_found, barcode)

    def ask_for_quantity(self, name, barcode, price):
        quantity = self._styled_askinteger("Quantity",
                                           f"Enter quantity for\n{name}:")
        if quantity:
            if barcode in self.billing_data:
                old_quantity = self.billing_data[barcode]['quantity']
                total_quantity = old_quantity + quantity
                messagebox.showinfo("Product Added",
                    f"Previous Quantity: {old_quantity}\n"
                    f"Added {quantity} more of {name}.\n"
                    f"Total quantity: {total_quantity}")
                self.billing_data[barcode]['quantity'] = total_quantity
            else:
                messagebox.showinfo("Product Added",
                                    f"Added {quantity} of {name}.")
                self.billing_data[barcode] = {
                    'name': name, 'price': price, 'quantity': quantity
                }
            self.refresh_table()
            self.payment_btn.config(state=tk.NORMAL)
        else:
            messagebox.showwarning("Invalid Input",
                                   "Please enter a valid quantity.")

    def product_not_found(self, barcode):
        messagebox.showerror(
            "Product Not Found",
            f"Barcode '{barcode}' is not registered.\n"
            "Please contact customer support."
        )

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        total_bill = 0
        for i, item in enumerate(self.billing_data.values()):
            total = item['price'] * item['quantity']
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.insert('', tk.END, tags=(tag,),
                             values=(item['name'],
                                     f"Rs {item['price']:,}",
                                     item['quantity'],
                                     f"Rs {total:,}"))
            total_bill += total

        # Zebra rows
        self.tree.tag_configure("even", background=BG_CARD)
        self.tree.tag_configure("odd",  background=BG_ROW_ALT)

        # Update summary panel
        self.total_label.config(text=f"Rs {total_bill:,}")
        self.subtotal_lbl.config(text=f"Rs {total_bill:,}")
        count = len(self.billing_data)
        self.item_count_lbl.config(
            text=f"{count} item{'s' if count != 1 else ''}"
        )
        self.sb_lbl.config(
            text=f"  Last scan added — {count} item(s) in cart"
        )

    def delete_product(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Select Product",
                                   "Please select a product to delete.")
            return

        item_values = self.tree.item(selected_item, 'values')
        product_name = item_values[0]
        barcode_to_delete = None

        for barcode, info in self.billing_data.items():
            if info['name'] == product_name:
                barcode_to_delete = barcode
                break

        if barcode_to_delete:
            confirm = messagebox.askyesno("Confirm Delete",
                                          f"Remove {product_name} from bill?")
            if confirm:
                del self.billing_data[barcode_to_delete]
                self.refresh_table()
                messagebox.showinfo("Removed",
                                    f"{product_name} removed from the bill.")

    def open_payment_window(self):
        if hasattr(self, "payment_window") and self.payment_window.winfo_exists():
            return

        self.payment_window = tk.Toplevel(self.root)
        self.payment_window.title("Payment")
        self.payment_window.configure(bg=BG_CARD)
        self.payment_window.resizable(False, False)
        self.payment_window.grab_set()
        self.payment_window.transient(self.root)

        # Center
        self.root.update_idletasks()
        rx = self.root.winfo_x() + self.root.winfo_width()  // 2
        ry = self.root.winfo_y() + self.root.winfo_height() // 2
        self.payment_window.geometry(f"360x420+{rx-180}+{ry-210}")

        # Header stripe
        hdr = tk.Frame(self.payment_window, bg=ACCENT, height=4)
        hdr.pack(fill=tk.X)

        tk.Label(self.payment_window, text="Choose Payment Method",
                 fg=TEXT_PRIMARY, bg=BG_CARD,
                 font=("Segoe UI Semibold", 14, "bold")).pack(pady=(22, 4))

        tk.Label(self.payment_window,
                 text=f"Amount Due: {self.total_label.cget('text')}",
                 fg=ACCENT, bg=BG_CARD,
                 font=("Segoe UI", 12, "bold")).pack(pady=(0, 18))

        sep = tk.Frame(self.payment_window, bg=BORDER, height=1)
        sep.pack(fill=tk.X, padx=24)

        methods = [
            ("📱  Easypaisa",  "Easypaisa"),
            ("💳  JazzCash",   "JazzCash"),
            ("🏦  Debit Card", "DebitCard"),
        ]

        for label, method in methods:
            frm = tk.Frame(self.payment_window, bg=BG_ROW_ALT,
                           cursor="hand2")
            frm.pack(fill=tk.X, padx=24, pady=6)

            btn = tk.Button(frm, text=label,
                            command=lambda m=method: self.process_payment(m),
                            bg=BG_ROW_ALT, fg=TEXT_PRIMARY,
                            activebackground=ACCENT_DIM,
                            activeforeground=BG_DARK,
                            font=("Segoe UI", 11),
                            relief="flat", bd=0,
                            cursor="hand2",
                            padx=20, pady=14,
                            anchor=tk.W)
            btn.pack(fill=tk.X)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#1E2535"))
            btn.bind("<Leave>", lambda e, b=btn, f=frm: b.config(
                bg=BG_ROW_ALT))

        tk.Label(self.payment_window, text="Secured by SmartTrolley™",
                 fg=TEXT_DIM, bg=BG_CARD,
                 font=("Segoe UI", 8)).pack(side=tk.BOTTOM, pady=14)

    def proceed_to_payment(self):
        self.scanning = False
        if self.thread and self.thread.is_alive():
            self.thread.join()
        cv2.destroyAllWindows()
        self.status_lbl.config(text="  SCANNER STOPPED", fg=TEXT_DIM)
        self.status_dot.config(fg=TEXT_DIM)
        self.open_payment_window()

    def process_payment(self, method):
        if method in ["Easypaisa", "JazzCash"]:
            phone = self._styled_askstring("Phone Number",
                                           f"Enter your {method} number:")
            if phone:
                messagebox.showinfo("Payment Successful",
                                    f"✅  Paid via {method}\nNumber: {phone}")
        elif method == "DebitCard":
            card = self._styled_askstring("Debit Card",
                                          "Enter your card number:")
            if card:
                messagebox.showinfo("Payment Successful",
                                    f"✅  Paid via Debit Card\nCard: {card}")

        self.payment_btn.config(state=tk.DISABLED)
        self.payment_window.destroy()

    def ask_phone_number(self, payment_method):
        phone_number = self._styled_askstring(
            "Phone Number", f"Enter your {payment_method} number:")
        if phone_number:
            messagebox.showinfo("Payment Information",
                f"Payment Method: {payment_method}\nPhone: {phone_number}")
            self.payment_btn.config(state=tk.DISABLED)
        else:
            messagebox.showwarning("Invalid Input",
                                   "Please enter a valid phone number.")

    def ask_debitcard_info(self):
        card_choice = self._styled_askstring(
            "Debit Card",
            "Enter your Debit Card Account Number or scan your card:")
        if card_choice:
            messagebox.showinfo("Payment Information",
                f"Payment Method: DebitCard\nAccount: {card_choice}")
            self.payment_btn.config(state=tk.DISABLED)
        else:
            messagebox.showwarning("Invalid Input",
                                   "Please enter a valid account number.")

    def scan_barcode(self):
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        if not cap.isOpened():
            self.root.after(0, lambda: messagebox.showerror(
                "Camera Error", "Could not open camera"))
            return

        while self.scanning:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture image")
                break

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            barcodes = decode(gray_frame)

            if barcodes:
                for barcode in barcodes:
                    barcode_data = barcode.data.decode('utf-8')
                    barcode_type = barcode.type
                    print(f"Decoded {barcode_type} barcode: {barcode_data}")
                    if barcode_data != self.last_scanned_barcode:
                        self.last_scanned_barcode = barcode_data
                        self.update_billing(barcode_data)

            cv2.imshow("Scanning...", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def on_closing(self):
        self.scanning = False
        if self.thread and self.thread.is_alive():
            self.thread.join()
        self.conn.close()
        cv2.destroyAllWindows()
        self.root.destroy()


# ─────────────────────────────────────────────────────────────────────────────
# Run
# ─────────────────────────────────────────────────────────────────────────────
root = tk.Tk()
app = SmartTrolleyApp(root)
root.protocol("WM_DELETE_WINDOW", app.on_closing)
root.mainloop()