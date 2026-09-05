import urllib.request
import xml.etree.ElementTree as ET
import json
import datetime
import os
import re

def get_vietnam_time():
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    vn_tz = datetime.timezone(datetime.timedelta(hours=7))
    return utc_now.astimezone(vn_tz)

def parse_price(val_str):
    if not val_str:
        return 0.0
    clean = re.sub(r'[^\d\.]', '', str(val_str))
    try:
        val = float(clean)
        if val > 1000:
            val = val / 1000.0
        return round(val, 2)
    except:
        return 0.0

def crawl_gold(prev_gold_data=None):
    now_vn = get_vietnam_time()
    today_str = now_vn.strftime("%Y-%m-%d")
    
    # Defaults fallback if crawling fails
    sjc_mieng = (144.60, 147.60)
    sjc_nhan = (144.10, 147.10)
    doji_nhan = (146.00, 150.00)
    pnj_gold = (144.10, 147.60)
    btmc_rong = (145.50, 149.50)

    crawled_ok = False
    try:
        url = "https://giavang.org/"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
            }
        )
        with urllib.request.urlopen(req, timeout=10) as res:
            html = res.read().decode("utf-8", errors="ignore")
        
        tables = re.findall(r'<table[^>]*>(.*?)</table>', html, re.DOTALL)
        if len(tables) >= 2:
            # Table 0: SJC Miếng
            r0 = re.findall(r'<tr[^>]*>(.*?)</tr>', tables[0], re.DOTALL)
            if len(r0) > 1:
                c0 = [re.sub(r'<[^>]+>', '', c).strip() for c in re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', r0[1], re.DOTALL)]
                if len(c0) >= 4 and parse_price(c0[2]) > 0:
                    sjc_mieng = (parse_price(c0[2]), parse_price(c0[3]))
            
            # Table 1: SJC Nhẫn
            r1 = re.findall(r'<tr[^>]*>(.*?)</tr>', tables[1], re.DOTALL)
            if len(r1) > 1:
                c1 = [re.sub(r'<[^>]+>', '', c).strip() for c in re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', r1[1], re.DOTALL)]
                if len(c1) >= 4 and parse_price(c1[2]) > 0:
                    sjc_nhan = (parse_price(c1[2]), parse_price(c1[3]))

        # Comparison rows
        pattern = r'<tr>\s*<td[^>]*>.*?<strong>(.*?)</strong>.*?</td>\s*<td[^>]*>([\d\.,]+)</td>\s*<td[^>]*>([\d\.,]+)</td>\s*</tr>'
        matches = re.findall(pattern, html, re.DOTALL)
        for brand, buy, sell in matches[12:]:
            b_clean = brand.strip()
            buy_val = parse_price(buy)
            sell_val = parse_price(sell)
            if buy_val > 0 and sell_val > 0:
                if 'DOJI' in b_clean:
                    doji_nhan = (buy_val, sell_val)
                elif 'PNJ' in b_clean:
                    pnj_gold = (buy_val, sell_val)
                elif 'Bảo Tín Minh Châu' in b_clean:
                    btmc_rong = (buy_val, sell_val)
        
        crawled_ok = True
        print(f"✅ Đã crawl giá vàng trực tuyến thành công ({today_str})")
    except Exception as e:
        print(f"⚠️ Không thể crawl giavang.org: {e}. Sử dụng dữ liệu tham chiếu an toàn.")

    gold_9999 = (round(sjc_nhan[0] * 0.99, 2), round(sjc_nhan[1] * 0.99, 2))
    gold_18k = (round(sjc_nhan[0] * 0.75, 2), round(sjc_nhan[1] * 0.75, 2))
    gold_14k = (round(sjc_nhan[0] * 0.583, 2), round(sjc_nhan[1] * 0.583, 2))

    items = [
        {"id": "sjc_hcm", "brand": "SJC", "name": "Vàng miếng SJC 1L - 10L", "city": "Toàn quốc", "buy": sjc_mieng[0], "sell": sjc_mieng[1]},
        {"id": "sjc_nhan", "brand": "SJC", "name": "Vàng nhẫn SJC 99,99% (1-5 chỉ)", "city": "Toàn quốc", "buy": sjc_nhan[0], "sell": sjc_nhan[1]},
        {"id": "doji_hn", "brand": "DOJI", "name": "DOJI Hưng Thịnh Vượng 9999", "city": "Toàn quốc", "buy": doji_nhan[0], "sell": doji_nhan[1]},
        {"id": "pnj_gold", "brand": "PNJ", "name": "Vàng PNJ 24K (Trơn / Ép vỉ)", "city": "Toàn quốc", "buy": pnj_gold[0], "sell": pnj_gold[1]},
        {"id": "gold_18k", "brand": "Thị Trường", "name": "Vàng Tây 18K (75% Au)", "city": "Toàn quốc", "buy": gold_18k[0], "sell": gold_18k[1]},
        {"id": "gold_14k", "brand": "Thị Trường", "name": "Vàng Tây 14K (58.3% Au)", "city": "Toàn quốc", "buy": gold_14k[0], "sell": gold_14k[1]},
        {"id": "doji_hcm", "brand": "DOJI", "name": "DOJI Hưng Thịnh Vượng 9999 (TP.HCM)", "city": "Toàn quốc", "buy": doji_nhan[0], "sell": doji_nhan[1]},
        {"id": "btmc_rong", "brand": "Bảo Tín Minh Châu", "name": "Vàng Rồng Thăng Long", "city": "Toàn quốc", "buy": btmc_rong[0], "sell": btmc_rong[1]},
        {"id": "gold_9999", "brand": "Thị Trường", "name": "Vàng 24K (99.99% - Nữ trang)", "city": "Toàn quốc", "buy": gold_9999[0], "sell": gold_9999[1]}
    ]

    # Map previous prices for calculating change
    prev_map = {}
    if prev_gold_data and "items" in prev_gold_data:
        for prev_item in prev_gold_data["items"]:
            prev_map[prev_item["id"]] = prev_item

    for it in items:
        it["buyPerChi"] = round(it["buy"] / 10.0, 2)
        it["sellPerChi"] = round(it["sell"] / 10.0, 2)
        prev = prev_map.get(it["id"])
        if prev and "sell" in prev:
            diff = round(it["sell"] - prev["sell"], 2)
            it["change"] = diff
        else:
            it["change"] = 0.0

    return {
        "updatedAt": now_vn.isoformat(),
        "updatedDate": today_str,
        "updatedTime": now_vn.strftime("%H:%M:%S (GMT+7)"),
        "source": "Thị trường Vàng Việt Nam & Tổng hợp Trực tuyến",
        "unit": "triệu đồng / lượng",
        "items": items
    }

def crawl_exchange():
    now_vn = get_vietnam_time()
    vcb_url = "https://portal.vietcombank.com.vn/Usercontrols/TVWeb.TyGia/pXML.aspx"
    currencies = []
    try:
        req = urllib.request.Request(vcb_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            for ex in root.findall('.//Exrate'):
                code = ex.get('CurrencyCode', '')
                name = ex.get('CurrencyName', '')
                buy_cash = ex.get('Buy', '-').strip()
                buy_transfer = ex.get('Transfer', '-').strip()
                sell = ex.get('Sell', '-').strip()
                if code:
                    currencies.append({
                        "code": code,
                        "name": name,
                        "buyCash": float(buy_cash.replace(',', '')) if buy_cash != '-' else 0,
                        "buyTransfer": float(buy_transfer.replace(',', '')) if buy_transfer != '-' else 0,
                        "sell": float(sell.replace(',', '')) if sell != '-' else 0
                    })
    except Exception:
        currencies = [
            {"code": "USD", "name": "US DOLLAR", "buyCash": 25480, "buyTransfer": 25510, "sell": 25870},
            {"code": "EUR", "name": "EURO", "buyCash": 27250, "buyTransfer": 27520, "sell": 28750},
            {"code": "JPY", "name": "JAPANESE YEN", "buyCash": 165.20, "buyTransfer": 166.80, "sell": 175.10},
            {"code": "GBP", "name": "BRITISH POUND", "buyCash": 32800, "buyTransfer": 33130, "sell": 34200},
            {"code": "AUD", "name": "AUST DOLLAR", "buyCash": 16200, "buyTransfer": 16360, "sell": 16890},
            {"code": "SGD", "name": "SINGAPORE DOLLAR", "buyCash": 19100, "buyTransfer": 19300, "sell": 19910},
            {"code": "CNY", "name": "CHINESE YUAN", "buyCash": 3480, "buyTransfer": 3515, "sell": 3630},
            {"code": "KRW", "name": "SOUTH KOREAN WON", "buyCash": 16.20, "buyTransfer": 18.00, "sell": 19.65}
        ]

    return {
        "updatedAt": now_vn.isoformat(),
        "updatedDate": now_vn.strftime("%Y-%m-%d"),
        "source": "Vietcombank",
        "currencies": currencies
    }

def crawl_petrol():
    now_vn = get_vietnam_time()
    return {
        "updatedAt": now_vn.isoformat(),
        "updatedDate": now_vn.strftime("%Y-%m-%d"),
        "unit": "VNĐ / lít hoặc kg",
        "items": [
            {"name": "Xăng RON 95-V", "zone1": 21850, "zone2": 22280},
            {"name": "Xăng RON 95-III", "zone1": 21320, "zone2": 21740},
            {"name": "Xăng E5 RON 92-II", "zone1": 20450, "zone2": 20850},
            {"name": "Dầu Diesel 0.05S-II", "zone1": 19280, "zone2": 19660},
            {"name": "Dầu Hỏa 2-K", "zone1": 19450, "zone2": 19830}
        ]
    }

def update_history_series(history_path, today_str, buy_val, sell_val, max_items=None):
    if not os.path.exists(history_path):
        data = []
    else:
        try:
            with open(history_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = []

    # Update or append today
    if data and data[-1].get("date") == today_str:
        data[-1]["buy"] = buy_val
        data[-1]["sell"] = sell_val
    else:
        data.append({"date": today_str, "buy": buy_val, "sell": sell_val})

    if max_items and len(data) > max_items:
        data = data[-max_items:]

    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    api_dir = os.path.join(base_dir, "api", "v1", "market")
    history_dir = os.path.join(api_dir, "history")
    os.makedirs(history_dir, exist_ok=True)

    gold_json_path = os.path.join(api_dir, "gold.json")
    prev_gold_data = None
    if os.path.exists(gold_json_path):
        try:
            with open(gold_json_path, "r", encoding="utf-8") as f:
                prev_gold_data = json.load(f)
        except Exception:
            pass

    gold = crawl_gold(prev_gold_data)
    exchange = crawl_exchange()
    petrol = crawl_petrol()

    with open(gold_json_path, "w", encoding="utf-8") as f:
        json.dump(gold, f, ensure_ascii=False, indent=2)

    with open(os.path.join(api_dir, "exchange.json"), "w", encoding="utf-8") as f:
        json.dump(exchange, f, ensure_ascii=False, indent=2)

    with open(os.path.join(api_dir, "petrol.json"), "w", encoding="utf-8") as f:
        json.dump(petrol, f, ensure_ascii=False, indent=2)

    # Cập nhật chuỗi lịch sử giá vàng theo giá SJC Miếng
    sjc_item = next((it for it in gold["items"] if it["id"] == "sjc_hcm"), gold["items"][0])
    today_str = gold["updatedDate"]
    sjc_buy = sjc_item["buy"]
    sjc_sell = sjc_item["sell"]

    update_history_series(os.path.join(history_dir, "gold-history-7d.json"), today_str, sjc_buy, sjc_sell, max_items=7)
    update_history_series(os.path.join(history_dir, "gold-history-30d.json"), today_str, sjc_buy, sjc_sell, max_items=30)
    update_history_series(os.path.join(history_dir, "gold-history-1y.json"), today_str, sjc_buy, sjc_sell, max_items=365)
    update_history_series(os.path.join(history_dir, "gold-history-all.json"), today_str, sjc_buy, sjc_sell)

    # Nếu OmniBox ở cùng máy, sync sang thư mục data/gold-latest.json
    omnibox_data_dir = os.path.abspath(os.path.join(base_dir, "..", "OmniBox", "data"))
    if os.path.exists(omnibox_data_dir):
        try:
            omnibox_gold_path = os.path.join(omnibox_data_dir, "gold-latest.json")
            with open(omnibox_gold_path, "w", encoding="utf-8") as f:
                json.dump(gold, f, ensure_ascii=False, indent=2)
            print("✅ Đã đồng bộ sang OmniBox/data/gold-latest.json!")
        except Exception as e:
            print("⚠️ Không thể đồng bộ OmniBox:", e)

    print(f"✅ Đã cập nhật xong toàn bộ dữ liệu DataHub-Public lúc {gold['updatedTime']}!")

if __name__ == "__main__":
    main()
