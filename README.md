# NextWBC Backend API

FastAPI backend สำหรับ NextWBC project ที่ใช้ YOLO model สำหรับการตรวจจับ WBC

## 🚀 การ Deploy

### Railway (แนะนำ)

1. **สร้าง account ที่ [Railway](https://railway.app/)**
2. **Connect GitHub repository**
3. **Deploy จาก GitHub:**
   ```bash
   # Railway จะ auto-detect Python project
   # และใช้ requirements.txt
   ```

4. **ตั้งค่า Environment Variables:**
   - `FRONTEND_URL`: URL ของ frontend (เช่น https://nextwbc.vercel.app)
   - `DATABASE_URL`: PostgreSQL connection string (ถ้าใช้ database)

### Render

1. **สร้าง account ที่ [Render](https://render.com/)**
2. **สร้าง Web Service**
3. **Connect GitHub repository**
4. **ตั้งค่า:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Heroku

1. **สร้าง account ที่ [Heroku](https://heroku.com/)**
2. **ติดตั้ง Heroku CLI**
3. **Deploy:**
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

## 🔧 Environment Variables

```env
FRONTEND_URL=https://nextwbc.vercel.app
PORT=8000
```

## 📡 API Endpoints

- `GET /` - Health check
- `GET /health` - Detailed health check
- `POST /predict/` - Predict single image
- `POST /predict-batch/` - Predict multiple images

## 🐳 Docker (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📝 Notes

- Model จะถูกดาวน์โหลดจาก Hugging Face ครั้งแรกที่ deploy
- ใช้ YOLO model สำหรับการตรวจจับ WBC
- รองรับ CORS สำหรับ frontend 