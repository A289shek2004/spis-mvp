# 📊 Database Schema – Smart Pharma Inventory System (SPIS)

## 1. products
| Field | Type | Description |
|--------|------|--------------|
| id | integer | Primary Key |
| name | varchar | Product name |
| generic_name | varchar | Generic/chemical name |
| unit | varchar | e.g. strip, bottle, tablet |
| category | varchar | Product category (optional) |

---

## 2. batches
| Field | Type | Description |
|--------|------|--------------|
| id | integer | Primary Key |
| product_id | FK → products.id | Linked product |
| batch_no | varchar | Batch number |
| expiry_date | date | Expiration date |
| qty | integer | Quantity available |
| purchase_price | decimal | Cost price per unit |
| supplier_id | FK → suppliers.id | Linked supplier |

---

## 3. sales
| Field | Type | Description |
|--------|------|--------------|
| id | integer | Primary Key |
| batch_id | FK → batches.id | Sold batch |
| date | date | Date of sale |
| qty_sold | integer | Quantity sold |
| price | decimal | Sale price per unit |
| pharmacist_id | varchar | User ID or name (simplified) |

---

## 4. suppliers
| Field | Type | Description |
|--------|------|--------------|
| id | integer | Primary Key |
| name | varchar | Supplier name |
| lead_time_days | integer | Delivery lead time in days |
