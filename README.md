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

## Deploy บน AWS Lambda (FastAPI + YOLO Model)

1. ติดตั้ง dependencies ลงในโฟลเดอร์ package:
   ```bash
   pip install -r requirements.txt -t package/
   cp main.py lambda_function.py tune_best_1733.pt package/
   cd package
   zip -r ../deployment.zip .
   cd ..
   ```
2. อัพโหลด deployment.zip ไปที่ AWS Lambda (Python 3.11)
   - Handler: `lambda_function.handler`
   - Memory: 2048MB+ (แนะนำ)
   - Timeout: 30-60s
3. เชื่อมต่อ API Gateway (HTTP API)
4. ทดสอบ endpoint `/predict/`

**หมายเหตุ:**
- ถ้าโมเดลใหญ่กว่า 250MB (zip) ให้ใช้ Lambda Layer หรือโหลดจาก S3/HuggingFace
- ตั้งค่า CORS ให้ตรงกับ frontend

## Deploy ไป AWS Lambda (รองรับ ARM64)

### 1. เตรียมไฟล์ในโฟลเดอร์นี้ให้มี:
- main.py (โหลดโมเดลจากไฟล์ local)
- lambda_function.py (handler)
- requirements.txt (มี mangum)
- tune_best_1733.pt (ไฟล์โมเดล)

### 2. สร้าง deployment package (แนะนำ build บน ARM64 environment)

#### ถ้าใช้ Docker (แนะนำสำหรับ ARM64):
```bash
# รัน Docker container ของ AWS Lambda Python ARM64
# (บน Windows ให้เปลี่ยน %cd% เป็น path ที่เหมาะสม)
docker run --rm -it -v $PWD:/var/task public.ecr.aws/lambda/python:3.11-arm64 bash
# ใน container:
pip install -r requirements.txt -t package/
cp main.py lambda_function.py tune_best_1733.pt package/
cd package
zip -r ../deployment.zip .
exit
```

#### หรือบนเครื่อง local (ถ้า dependencies รองรับ ARM64):
```bash
pip install -r requirements.txt -t package/
cp main.py lambda_function.py tune_best_1733.pt package/
cd package
zip -r ../deployment.zip .
cd ..
```

### 3. สร้าง Lambda Function
- Runtime: Python 3.11
- Architecture: arm64 (หรือ x86_64 ถ้าไม่ได้ build บน ARM)
- Handler: lambda_function.handler
- Memory: 2048MB+ (แนะนำ)
- Timeout: 30-60s

### 4. อัพโหลด deployment.zip ไป Lambda
- ใน AWS Console > Lambda > Upload deployment package

### 5. เชื่อมต่อ API Gateway
- สร้าง HTTP API Gateway
- เชื่อมกับ Lambda function
- ตั้งค่า CORS ให้ตรงกับ frontend

### 6. ทดสอบ
- เรียก endpoint `/predict/` ผ่าน API Gateway

---

**หมายเหตุ:**
- ถ้า dependencies มี C extension (เช่น numpy, torch ฯลฯ) ควร build บน ARM64 environment
- ถ้า package ใหญ่เกิน 250MB (zip) ให้ใช้ Lambda Layer หรือโหลดโมเดลจาก S3/HuggingFace แทน

## Deploy แบบ Docker Container (AWS Lambda Container Image)

### 1. สร้าง Docker image
```bash
cd nextwbc_backend
# สร้าง image (เปลี่ยน <your-image-name> ตามต้องการ)
docker build -t nextwbc-lambda .
```

### 2. ทดสอบรัน local (optional)
```bash
docker run -p 9000:8080 nextwbc-lambda
# เรียก http://localhost:9000/2015-03-31/functions/function/invocations
```

### 3. Push ขึ้น Amazon ECR
- สร้าง ECR repository ใน AWS Console
- Tag และ push image:
```bash
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.<region>.amazonaws.com

docker tag nextwbc-lambda:latest <aws_account_id>.dkr.ecr.<region>.amazonaws.com/<your-repo>:latest
docker push <aws_account_id>.dkr.ecr.<region>.amazonaws.com/<your-repo>:latest
```

### 4. สร้าง Lambda function แบบ Container Image
- เลือก image จาก ECR
- Memory: 2048MB+ (แนะนำ)
- Timeout: 30-60s

### 5. เชื่อมต่อ API Gateway
- สร้าง HTTP API Gateway
- เชื่อมกับ Lambda function
- ตั้งค่า CORS ให้ตรงกับ frontend

---

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