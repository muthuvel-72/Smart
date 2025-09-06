import json
import os
import time
import requests
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# ------------------- API CONFIG -------------------
API_KEY = "ac4e8bf831259a3ff89ed6f5"
BASE_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest"

CACHE_FILE = "rates_cache.json"
FAV_FILE = "favorites.json"

# ------------------- I18N / TRANSLATIONS -------------------
I18N = {
    "en": {
        "title": "🌍 Smart Currency Converter",
        "enter_amount": "Enter Amount:",
        "from_currency": "From Currency:",
        "to_currency": "To Currency:",
        "convert": "Convert",
        "history": "Conversion History",
        "favorites": "Favorites",
        "add_fav": "⭐ Add Favorite",
        "remove_fav": "🗑 Remove Favorite",
        "language": "Language:",
        "powered": "✨ Powered by ExchangeRate-API ✨",
        "ai_suggestion": "AI Suggestion",
        "suggest_convert_now": "Rate improved since last time — better to convert now.",
        "suggest_wait": "Rate worsened since last time — consider waiting.",
        "suggest_no_data": "Not enough data yet for suggestions.",
        "input_error": "Please enter a valid number.",
        "conn_error_fetch_list": "Unable to fetch currency data:\n{}",
        "conn_error_fetch_rates": "Failed to retrieve exchange rates:\n{}",
        "no_rate_for": "Conversion rate not available for {}",
        "fav_added": "Added to favorites.",
        "fav_exists": "This pair is already in favorites.",
        "fav_removed": "Removed selected favorite(s).",
        "nothing_selected": "Please select an item first.",
        "search": "Search:",
    },
    "ta": {  # Tamil (UI labels concise)
        "title": "🌍 ஸ்மார்ட் கரன்சி கன்வெர்டர்",
        "enter_amount": "தொகையை உள்ளிடுக:",
        "from_currency": "இருந்து நாணயம்:",
        "to_currency": "எதிர் நாணயம்:",
        "convert": "மாற்று",
        "history": "மாற்று வரலாறு",
        "favorites": "பிடித்தவை",
        "add_fav": "⭐ பிடித்ததில் சேர்",
        "remove_fav": "🗑 நீக்கு",
        "language": "மொழி:",
        "powered": "✨ எக்ஸ்சேஞ்ச் ரேட் API மூலம் ✨",
        "ai_suggestion": "AI பரிந்துரை",
        "suggest_convert_now": "முந்தையதை விட விகிதம் மேம்பட்டது — இப்போது மாற்றுவது நல்லது.",
        "suggest_wait": "விகிதம் குறைந்துள்ளது — சில நேரம் காத்திருக்கவும்.",
        "suggest_no_data": "பரிந்துரைக்கு போதிய தரவு இல்லை.",
        "input_error": "சரியான எண்ணை உள்ளிடவும்.",
        "conn_error_fetch_list": "நாணய தரவைப் பெற முடியவில்லை:\n{}",
        "conn_error_fetch_rates": "விகிதங்களை பெறத் தவறியது:\n{}",
        "no_rate_for": "{} கான விகிதம் இல்லை",
        "fav_added": "பிடித்தவைகளில் சேர்க்கப்பட்டது.",
        "fav_exists": "இந்த ஜோடி ஏற்கனவே உள்ளது.",
        "fav_removed": "தேர்ந்த பிடித்தவை நீக்கப்பட்டது.",
        "nothing_selected": "முதலில் ஒன்றைத் தேர்ந்தெடுக்கவும்.",
        "search": "தேடல்:",
    },
    "hi": {  # Hindi
        "title": "🌍 स्मार्ट करेंसी कन्वर्टर",
        "enter_amount": "राशि दर्ज करें:",
        "from_currency": "से मुद्रा:",
        "to_currency": "में मुद्रा:",
        "convert": "परिवर्तित करें",
        "history": "परिवर्तन इतिहास",
        "favorites": "पसंदीदा",
        "add_fav": "⭐ पसंदीदा में जोड़ें",
        "remove_fav": "🗑 हटाएँ",
        "language": "भाषा:",
        "powered": "✨ ExchangeRate-API द्वारा संचालित ✨",
        "ai_suggestion": "AI सुझाव",
        "suggest_convert_now": "पिछली बार से दर बेहतर है — अभी बदलना बेहतर है।",
        "suggest_wait": "दर खराब हुई है — प्रतीक्षा करने पर विचार करें।",
        "suggest_no_data": "सुझाव के लिए पर्याप्त डेटा नहीं है।",
        "input_error": "कृपया मान्य संख्या दर्ज करें।",
        "conn_error_fetch_list": "मुद्रा डेटा प्राप्त करने में असमर्थ:\n{}",
        "conn_error_fetch_rates": "विनिमय दर प्राप्त करने में विफल:\n{}",
        "no_rate_for": "{} के लिए दर उपलब्ध नहीं",
        "fav_added": "पसंदीदा में जोड़ा गया।",
        "fav_exists": "यह जोड़ी पहले से ही पसंदीदा में है।",
        "fav_removed": "चयनित पसंदीदा हटाए गए।",
        "nothing_selected": "कृपया पहले एक आइटम चुनें।",
        "search": "खोज:",
    },
}

# ------------------- FLAGS + NAMES -------------------
# (Add more as you like; unknowns will still work without emoji.)
currency_info = {
    "USD": ("🇺🇸", "US Dollar"),
    "INR": ("🇮🇳", "Indian Rupee"),
    "EUR": ("🇪🇺", "Euro"),
    "GBP": ("🇬🇧", "British Pound"),
    "JPY": ("🇯🇵", "Japanese Yen"),
    "AUD": ("🇦🇺", "Australian Dollar"),
    "CAD": ("🇨🇦", "Canadian Dollar"),
    "CNY": ("🇨🇳", "Chinese Yuan"),
    "SGD": ("🇸🇬", "Singapore Dollar"),
    "AED": ("🇦🇪", "UAE Dirham"),
    "ZAR": ("🇿🇦", "South African Rand"),
    "BRL": ("🇧🇷", "Brazilian Real"),
    "MXN": ("🇲🇽", "Mexican Peso"),
    "RUB": ("🇷🇺", "Russian Ruble"),
    "KRW": ("🇰🇷", "South Korean Won"),
    "CHF": ("🇨🇭", "Swiss Franc"),
    "SEK": ("🇸🇪", "Swedish Krona"),
    "NZD": ("🇳🇿", "New Zealand Dollar"),
    "TRY": ("🇹🇷", "Turkish Lira"),
    "SAR": ("🇸🇦", "Saudi Riyal"),
    "PKR": ("🇵🇰", "Pakistani Rupee"),
    "EGP": ("🇪🇬", "Egyptian Pound"),
    "THB": ("🇹🇭", "Thai Baht"),
    "NGN": ("🇳🇬", "Nigerian Naira"),
    "BDT": ("🇧🇩", "Bangladeshi Taka"),
    "LKR": ("🇱🇰", "Sri Lankan Rupee"),
    "MYR": ("🇲🇾", "Malaysian Ringgit"),
    "IDR": ("🇮🇩", "Indonesian Rupiah"),
    "VND": ("🇻🇳", "Vietnamese Dong"),
    "KWD": ("🇰🇼", "Kuwaiti Dinar"),
    "QAR": ("🇶🇦", "Qatari Riyal"),
    "HKD": ("🇭🇰", "Hong Kong Dollar"),
    "PLN": ("🇵🇱", "Polish Zloty"),
    "NOK": ("🇳🇴", "Norwegian Krone"),
    "DKK": ("🇩🇰", "Danish Krone"),
    "CZK": ("🇨🇿", "Czech Koruna"),
    "HUF": ("🇭🇺", "Hungarian Forint"),
    "ILS": ("🇮🇱", "Israeli Shekel"),
    "MAD": ("🇲🇦", "Moroccan Dirham"),
    "COP": ("🇨🇴", "Colombian Peso"),
    "ARS": ("🇦🇷", "Argentine Peso"),
    "CLP": ("🇨🇱", "Chilean Peso"),
    "PEN": ("🇵🇪", "Peruvian Sol"),
    "UAH": ("🇺🇦", "Ukrainian Hryvnia"),
    "XAF": ("🌍", "Central African CFA Franc"),
    "XOF": ("🌍", "West African CFA Franc"),
    "KES": ("🇰🇪", "Kenyan Shilling"),
    "TZS": ("🇹🇿", "Tanzanian Shilling"),
    "UGX": ("🇺🇬", "Ugandan Shilling"),
    "ETB": ("🇪🇹", "Ethiopian Birr"),
    "ZMW": ("🇿🇲", "Zambian Kwacha"),
    "GHS": ("🇬🇭", "Ghanaian Cedi"),
    "DZD": ("🇩🇿", "Algerian Dinar"),
    "TND": ("🇹🇳", "Tunisian Dinar"),
    "LYD": ("🇱🇾", "Libyan Dinar"),
    "SDG": ("🇸🇩", "Sudanese Pound"),
    "XCD": ("🌍", "East Caribbean Dollar"),
    "JMD": ("🇯🇲", "Jamaican Dollar"),
}

# ------------------- HELPERS: CACHE & FAVORITES -------------------
def load_json(path, default):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default

def save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

rates_cache = load_json(CACHE_FILE, {})  # { base: {"timestamp":..., "conversion_rates": {...}} }
favorites = load_json(FAV_FILE, [])      # list of "USD→INR" strings

# ------------------- FETCH RATES -------------------
def fetch_base_rates(base):
    try:
        url = f"{BASE_URL}/{base}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # cache
        rates_cache[base] = {
            "timestamp": int(time.time()),
            "conversion_rates": data.get("conversion_rates", {})
        }
        save_json(CACHE_FILE, rates_cache)
        return rates_cache[base]["conversion_rates"]
    except Exception as e:
        messagebox.showerror(t("conn_error_fetch_rates"), str(e))
        # fallback to cache if available
        cached = rates_cache.get(base, {}).get("conversion_rates")
        return cached or {}

# ------------------- INITIAL CODES -------------------
def get_currency_codes():
    # Try API list from USD; fallback to keys we know
    try:
        url = f"{BASE_URL}/USD"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return sorted(list(data["conversion_rates"].keys()))
    except Exception as e:
        messagebox.showerror(t("conn_error_fetch_list"), str(e))
        return sorted(list(currency_info.keys()))

# ------------------- I18N UTIL -------------------
current_lang = "en"
def t(key):
    return I18N.get(current_lang, I18N["en"]).get(key, I18N["en"].get(key, key))

def refresh_texts():
    root.title(t("title"))
    lbl_title.config(text=t("title"))
    lbl_amount.config(text=t("enter_amount"))
    lbl_from.config(text=t("from_currency"))
    lbl_to.config(text=t("to_currency"))
    btn_convert.config(text=t("convert"))
    lbl_history.config(text=t("history"))
    lbl_fav.config(text=t("favorites"))
    btn_add_fav.config(text=t("add_fav"))
    btn_remove_fav.config(text=t("remove_fav"))
    lbl_lang.config(text=t("language"))
    lbl_ai.config(text=t("ai_suggestion"))
    lbl_powered.config(text=t("powered"))
    lbl_search.config(text=t("search"))

def on_lang_change(_evt=None):
    global current_lang
    current_lang = lang_var.get()
    refresh_texts()

# ------------------- UI HELPERS -------------------
def display_label_for(code):
    flag, name = currency_info.get(code, ("", code))
    return f"{flag} {code} — {name}"

def parse_code_from_label(label):
    # expects "🇺🇸 USD — US Dollar" or "USD — US Dollar"
    return label.strip().split()[1] if label and label[0] != label[1] else label.split(" ")[0]

# ------------------- CONVERSION & AI SUGGESTION -------------------
def convert_action():
    try:
        amt_str = entry_amount.get().strip()
        if not amt_str:
            raise ValueError()
        amount = float(amt_str)

        from_label = combo_from.get().strip()
        to_label = combo_to.get().strip()
        from_code = parse_code_from_label(from_label)
        to_code = parse_code_from_label(to_label)

        # fetch latest base rates
        rates = fetch_base_rates(from_code)
        if not rates or to_code not in rates:
            messagebox.showerror(t("no_rate_for").format(to_code), t("no_rate_for").format(to_code))
            return

        rate_now = rates[to_code]
        converted = amount * rate_now

        # result line
        f_flag = currency_info.get(from_code, ("", ""))[0]
        t_flag = currency_info.get(to_code, ("", ""))[0]
        result_line = f"{f_flag} {amount:.2f} {from_code} = {t_flag} {converted:.2f} {to_code}"
        result_var.set(result_line)

        # history
        history_box.insert(tk.END, result_line + "\n")
        history_box.see(tk.END)

        # AI suggestion: compare with last cached rate_snapshot_before (if exists)
        suggestion = t("suggest_no_data")
        prev_rate = last_cached_rate(from_code, to_code, exclude_current=True)
        if prev_rate is not None:
            if rate_now > prev_rate:
                suggestion = t("suggest_convert_now")
            elif rate_now < prev_rate:
                suggestion = t("suggest_wait")
            else:
                suggestion = t("suggest_no_data")
        ai_var.set(suggestion)

    except ValueError:
        messagebox.showerror("Error", t("input_error"))

def last_cached_rate(base, to_code, exclude_current=True):
    """
    Look into cache history for previous rate of base→to_code.
    Our cache stores only the latest snapshot per base, so we keep
    one previous copy under key f"{base}__prev".
    """
    # move current to prev when we fetch again (done inside fetch_base_rates by rotation below)
    entry = rates_cache.get(base)
    if not entry:
        return None
    return entry.get("prev_rates", {}).get(to_code)

# Monkey-patch fetch_base_rates to rotate prev snapshot
_old_fetch = fetch_base_rates
def fetch_base_rates(base):
    try:
        url = f"{BASE_URL}/{base}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        new_rates = data.get("conversion_rates", {})
        # rotate: save current as prev, store new as current
        prev_rates = rates_cache.get(base, {}).get("conversion_rates", {})
        rates_cache[base] = {
            "timestamp": int(time.time()),
            "conversion_rates": new_rates,
            "prev_rates": prev_rates or {}
        }
        save_json(CACHE_FILE, rates_cache)
        return new_rates
    except Exception as e:
        messagebox.showerror(t("conn_error_fetch_rates"), str(e))
        # fallback to current cached
        cached = rates_cache.get(base, {}).get("conversion_rates")
        return cached or {}

# ------------------- FAVORITES -------------------
def add_favorite():
    from_code = parse_code_from_label(combo_from.get().strip())
    to_code = parse_code_from_label(combo_to.get().strip())
    pair = f"{from_code}→{to_code}"
    if pair in favorites:
        messagebox.showinfo("Info", t("fav_exists"))
        return
    favorites.append(pair)
    save_json(FAV_FILE, favorites)
    fav_list.insert(tk.END, pair)
    messagebox.showinfo("Info", t("fav_added"))

def remove_favorite():
    sel = list(fav_list.curselection())
    if not sel:
        messagebox.showwarning("Info", t("nothing_selected"))
        return
    # remove from bottom to top to keep indices valid
    for idx in reversed(sel):
        pair = fav_list.get(idx)
        fav_list.delete(idx)
        if pair in favorites:
            favorites.remove(pair)
    save_json(FAV_FILE, favorites)
    messagebox.showinfo("Info", t("fav_removed"))

def on_favorite_double_click(_evt=None):
    try:
        idx = fav_list.curselection()[0]
        pair = fav_list.get(idx)
        from_code, to_code = pair.split("→")
        # set dropdowns & convert
        set_combo_to_code(combo_from, from_code)
        set_combo_to_code(combo_to, to_code)
        convert_action()
    except Exception:
        pass

# ------------------- SEARCH IN DROPDOWNS -------------------
def filter_codes(_evt=None):
    term = search_var.get().strip().lower()
    if not term:
        update_combos(all_labels)
        return
    filtered = [lbl for lbl in all_labels if term in lbl.lower()]
    update_combos(filtered)

def update_combos(labels):
    combo_from["values"] = labels
    combo_to["values"] = labels

def set_combo_to_code(combo, code):
    # find matching label
    for lbl in combo["values"]:
        if lbl.startswith(currency_info.get(code, ("", ""))[0]):
            # emoji path
            if f" {code} " in lbl:
                combo.set(lbl)
                return
        if lbl.startswith(code) or f" {code} " in lbl:
            combo.set(lbl)
            return
    # fallback to just code if not found
    combo.set(code)

# ------------------- BUILD UI -------------------
root = tk.Tk()
root.title(I18N["en"]["title"])
root.geometry("860x640")
root.config(bg="#0f172a")

# Top row: Title + Language
top = tk.Frame(root, bg="#0f172a")
top.pack(fill="x", pady=8)

lbl_title = tk.Label(top, text=I18N["en"]["title"], font=("Arial", 18, "bold"),
                     fg="#38bdf8", bg="#0f172a")
lbl_title.pack(side="left", padx=12)

lang_wrap = tk.Frame(top, bg="#0f172a")
lang_wrap.pack(side="right", padx=12)
lbl_lang = tk.Label(lang_wrap, text=I18N["en"]["language"], font=("Arial", 11, "bold"),
                    fg="#a3e635", bg="#0f172a")
lbl_lang.pack(side="left", padx=(0,6))
lang_var = tk.StringVar(value="en")
lang_menu = ttk.Combobox(lang_wrap, values=["en","ta","hi"], textvariable=lang_var, width=6, state="readonly")
lang_menu.pack(side="left")
lang_menu.bind("<<ComboboxSelected>>", on_lang_change)

# Amount
lbl_amount = tk.Label(root, text=I18N["en"]["enter_amount"], font=("Arial", 12, "bold"),
                      fg="#facc15", bg="#0f172a")
lbl_amount.pack()
entry_amount = tk.Entry(root, font=("Arial", 12), bg="#f1f5f9", fg="black")
entry_amount.pack(pady=5)

# Search
search_row = tk.Frame(root, bg="#0f172a")
search_row.pack(pady=4)
lbl_search = tk.Label(search_row, text=I18N["en"]["search"], font=("Arial", 11, "bold"),
                      fg="#93c5fd", bg="#0f172a")
lbl_search.pack(side="left", padx=6)
search_var = tk.StringVar()
search_entry = tk.Entry(search_row, textvariable=search_var, font=("Arial", 11), bg="#e2e8f0")
search_entry.pack(side="left", padx=6, ipady=2)
search_entry.bind("<KeyRelease>", filter_codes)

# From
lbl_from = tk.Label(root, text=I18N["en"]["from_currency"], font=("Arial", 12, "bold"),
                    fg="#fb923c", bg="#0f172a")
lbl_from.pack()
# populate codes
codes = get_currency_codes()
def build_label(code):
    flag, name = currency_info.get(code, ("", code))
    return f"{flag} {code} — {name}" if flag else f"{code} — {name}"
all_labels = [build_label(c) for c in sorted(set(codes))]
combo_from = ttk.Combobox(root, values=all_labels, font=("Arial", 12), width=44)
combo_from.set(build_label("USD"))
combo_from.pack(pady=5)

# To
lbl_to = tk.Label(root, text=I18N["en"]["to_currency"], font=("Arial", 12, "bold"),
                  fg="#34d399", bg="#0f172a")
lbl_to.pack()
combo_to = ttk.Combobox(root, values=all_labels, font=("Arial", 12), width=44)
combo_to.set(build_label("INR"))
combo_to.pack(pady=5)

# Convert button
btn_convert = tk.Button(root, text=I18N["en"]["convert"], command=convert_action,
                        font=("Arial", 12, "bold"), bg="#2563eb", fg="white",
                        activebackground="#16a34a", relief="raised", bd=4)
btn_convert.pack(pady=10)

# Result + AI Suggestion
result_var = tk.StringVar()
lbl_result = tk.Label(root, textvariable=result_var, font=("Arial", 14, "bold"),
                      fg="#f472b6", bg="#0f172a", wraplength=800, justify="center")
lbl_result.pack(pady=(6,2))

lbl_ai = tk.Label(root, text=I18N["en"]["ai_suggestion"], font=("Arial", 12, "bold"),
                  fg="#a78bfa", bg="#0f172a")
lbl_ai.pack()
ai_var = tk.StringVar(value=I18N["en"]["suggest_no_data"])
lbl_ai_text = tk.Label(root, textvariable=ai_var, font=("Arial", 11),
                       fg="#e5e7eb", bg="#0f172a", wraplength=800, justify="center")
lbl_ai_text.pack(pady=(0,10))

# Mid: Favorites + History side-by-side
mid = tk.Frame(root, bg="#0f172a")
mid.pack(fill="both", expand=True, padx=10)

# Favorites panel
fav_frame = tk.Frame(mid, bg="#0f172a", bd=0)
fav_frame.pack(side="left", fill="y", padx=(0,10))
lbl_fav = tk.Label(fav_frame, text=I18N["en"]["favorites"], font=("Arial", 12, "bold"),
                   fg="#f87171", bg="#0f172a")
lbl_fav.pack()
fav_list = tk.Listbox(fav_frame, height=12, width=22, bg="#1e293b", fg="white",
                      selectbackground="#4b5563", activestyle="none")
fav_list.pack(pady=4, fill="y")
fav_list.bind("<Double-Button-1>", on_favorite_double_click)

btns = tk.Frame(fav_frame, bg="#0f172a")
btns.pack(pady=6)
btn_add_fav = tk.Button(btns, text=I18N["en"]["add_fav"], font=("Arial", 10, "bold"),
                        bg="#374151", fg="white", command=add_favorite)
btn_add_fav.pack(side="left", padx=4)
btn_remove_fav = tk.Button(btns, text=I18N["en"]["remove_fav"], font=("Arial", 10, "bold"),
                           bg="#7f1d1d", fg="white", command=remove_favorite)
btn_remove_fav.pack(side="left", padx=4)

# Seed favorites listbox
for p in favorites:
    fav_list.insert(tk.END, p)

# History
hist_frame = tk.Frame(mid, bg="#0f172a")
hist_frame.pack(side="left", fill="both", expand=True)
lbl_history = tk.Label(hist_frame, text=I18N["en"]["history"], font=("Arial", 12, "bold"),
                       fg="#f59e0b", bg="#0f172a")
lbl_history.pack()
history_box = scrolledtext.ScrolledText(hist_frame, font=("Arial", 11), bg="#1e293b",
                                        fg="white", wrap=tk.WORD, height=12)
history_box.pack(fill="both", expand=True, pady=4)

# Footer
lbl_powered = tk.Label(root, text=I18N["en"]["powered"], font=("Arial", 9),
                       fg="#a78bfa", bg="#0f172a")
lbl_powered.pack(side="bottom", pady=6)

# Apply initial language
refresh_texts()

root.mainloop()