# 🌐 DataHub-Public
> **Trung tâm dữ liệu thị trường mở (Open Public Market Data Hub)**  
> Dữ liệu được cập nhật tự động 24/7 qua GitHub Actions. Miễn phí 100% không giới hạn.

---

## 📡 Danh Sách Public REST JSON Endpoints

| Dữ liệu | URL Endpoint (Raw CDN) | Tần suất cập nhật |
| :--- | :--- | :--- |
| **🥇 Giá Vàng Mới Nhất** | `https://raw.githubusercontent.com/FatKen13/DataHub-Public/main/api/v1/market/gold.json` | 08:30 & 14:30 GMT+7 |
| **📈 Lịch Sử Giá Vàng** | `https://raw.githubusercontent.com/FatKen13/DataHub-Public/main/api/v1/market/history/gold-history.json` | Hàng ngày |
| **💵 Tỷ Giá Vietcombank** | `https://raw.githubusercontent.com/FatKen13/DataHub-Public/main/api/v1/market/exchange.json` | 08:30 & 14:30 GMT+7 |
| **⛽ Giá Xăng Dầu Petrolimex** | `https://raw.githubusercontent.com/FatKen13/DataHub-Public/main/api/v1/market/petrol.json` | Theo kỳ điều chỉnh |

---

## 💻 Hướng Dẫn Sử Dụng Trong JavaScript

```javascript
// Lấy giá vàng mới nhất
fetch('https://raw.githubusercontent.com/FatKen13/DataHub-Public/main/api/v1/market/gold.json')
  .then(res => res.json())
  .then(data => console.log('Giá vàng:', data));
```
