# FastAPI E-Ticaret Backend API

Bu proje, JWT tabanlı kimlik doğrulama içeren, MongoDB ile çalışan RESTful bir e-ticaret backend servisidir.

Sistem; kullanıcı yönetimi, ürün yönetimi ve stok kontrollü sipariş yönetimi modüllerini içermektedir.

---

## Kullanılan Teknolojiler

* FastAPI
* MongoDB
* MongoDB Atlas
* Uvicorn
* Passlib
* python-jose
* Pydantic

---

## Proje Dizini

```
orderflow-fastapi-mongodb/
│
├── app/
│   ├── main.py        # Uygulama başlangıç noktası
│   ├── database.py    # MongoDB bağlantı yönetimi
│   ├── auth.py        # JWT ve şifre hash işlemleri
│   ├── models.py      # MongoDB veri yapıları
│   ├── schemas.py     # Pydantic request/response modelleri
│   └── routes.py      # Tüm API endpoint tanımları
│
├── .env               # Ortam değişkenleri
├── requirements.txt   # Python bağımlılıkları
└── README.md
```

---

## Sistem Mimarisi

Uygulama modüler ancak tek paket (`app`) altında toplanmış bir yapı kullanmaktadır.
<img width="1825" height="553" alt="Ekran görüntüsü 2026-02-19 204659" src="https://github.com/user-attachments/assets/41e14de9-a2d5-457d-814a-bd6c2513c831" />


### 1. Kimlik Doğrulama (Authentication)

* Kullanıcı kayıt işlemi
* Şifrelerin hashlenmesi (bcrypt)
* Login sonrası JWT access token üretimi
* Protected endpoint erişimi (Bearer Token)

JWT doğrulama dependency üzerinden sağlanmaktadır.
<img width="1801" height="615" alt="Ekran görüntüsü 2026-02-19 205959" src="https://github.com/user-attachments/assets/495d0bf4-97d1-4b84-b43e-8522dfe34021" />

<img width="1759" height="203" alt="Ekran görüntüsü 2026-02-19 210016" src="https://github.com/user-attachments/assets/cd79232b-85a2-4540-bc57-2777f28323d8" />


<img width="1786" height="610" alt="Ekran görüntüsü 2026-02-19 210059" src="https://github.com/user-attachments/assets/dca2abaa-05d4-4197-9334-e3526a306c48" />

<img width="1750" height="333" alt="Ekran görüntüsü 2026-02-19 210127" src="https://github.com/user-attachments/assets/10acdf21-b67a-4c40-9e41-f163834e87b1" />

---

### 2. Ürün Yönetimi (Product Management)

* Ürün oluşturma
* Ürün listeleme
* Ürün güncelleme
* Ürün silme
* Stok takibi
* Ürünü oluşturan kullanıcı bilgisi (owner_id)
<img width="1796" height="625" alt="Ekran görüntüsü 2026-02-19 210402" src="https://github.com/user-attachments/assets/d4df693a-4574-497d-9a32-9898c55d48d6" />
<img width="1769" height="317" alt="Ekran görüntüsü 2026-02-19 210427" src="https://github.com/user-attachments/assets/6b4fa00c-fe22-46b3-82ce-b9d3cb499648" />

<img width="1799" height="694" alt="Ekran görüntüsü 2026-02-19 211033" src="https://github.com/user-attachments/assets/c0119330-c82c-4927-bf41-c7ee9a9b6189" />

<img width="1763" height="216" alt="Ekran görüntüsü 2026-02-19 211133" src="https://github.com/user-attachments/assets/60432282-3343-4d18-8cc8-de98d3b0da98" />


---

### 3. Sipariş Yönetimi (Order Management)

* Çoklu ürün destekli sipariş oluşturma
* Stok yeterlilik kontrolü
* Toplam fiyat hesaplama
* Sipariş durum güncelleme
* Kullanıcıya ait siparişleri listeleme

Sipariş oluşturulurken:

* Ürün varlığı kontrol edilir
* Stok yeterliliği doğrulanır
* Stok düşülür
* Toplam fiyat hesaplanır
* Sipariş kaydı oluşturulur
<img width="1788" height="728" alt="Ekran görüntüsü 2026-02-19 211342" src="https://github.com/user-attachments/assets/ca2363db-5221-41b8-a434-0ee97ab9cf66" />

<img width="1768" height="399" alt="Ekran görüntüsü 2026-02-19 211400" src="https://github.com/user-attachments/assets/eaf2dc39-e63e-4cd4-8d77-435cf11ea6a4" />

---

## Veritabanı Yapısı

### Users Collection

```json
{
  "_id": ObjectId,
  "name": "string",
  "email": "string (unique)",
  "password": "hashed_password"
}
```

### Products Collection

```json
{
  "_id": ObjectId,
  "name": "string",
  "description": "string",
  "price": number,
  "stock": number,
  "owner_id": "user_id"
}
```

### Orders Collection

```json
{
  "_id": ObjectId,
  "user_id": "user_id",
  "products": [
    {
      "product_id": "product_id",
      "quantity": number
    }
  ],
  "total_price": number,
  "status": "pending",
  "created_at": datetime
}
```

---

## Kurulum

### 1. Sanal Ortam

```bash
conda create -n orderflow_env python=3.10
conda activate orderflow_env
```

### 2. Bağımlılıkların Yüklenmesi

```bash
pip install -r requirements.txt
```

### 3. .env Dosyası

Proje kök dizininde `.env` dosyası oluşturulmalıdır:

```
MONGO_URL=your_mongodb_atlas_connection_string
SECRET_KEY=your_secret_key
```

### 4. Uygulamayı Çalıştırma

```bash
uvicorn app.main:app --reload
```

Swagger arayüzü:

```
http://127.0.0.1:8000/docs
```

---

## API Test Akışı

1. Kullanıcı kaydı oluşturulur.
2. Login yapılır ve access token alınır.
3. Authorize butonu ile token girilir.
4. Ürün oluşturulur.
5. Sipariş oluşturulur.
6. Siparişler listelenir.
7. Sipariş durumu güncellenir.
8. Güncelleme doğrulanır.

