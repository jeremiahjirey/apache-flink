
# 🐦 Tweet Dashboard with Cognito Authentication

A secure, real-time tweet dashboard built with **Flask**, **AWS API Gateway**, **Lambda**, **DynamoDB**, **Kinesis**, and **Amazon Cognito**.  
Supports **signup, login, confirmation, and JWT-based session**.

---

## ✅ Features
- User authentication with **Amazon Cognito**
- Secure session handling with **AUTH_SECRET**
- Tweet posting (secured by Cognito Authorizer)
- Real-time dashboard (tweets + charts)
- Light/Dark mode UI toggle
- Password strength checker with live validation
- Confirm account via Cognito confirmation code
- Responsive design

---

## 🏗 Architecture
```
Frontend (Flask Templates)
        ↓
Flask Application (application.py)
        ↓
API Gateway (Cognito Authorizer)
        ↓
AWS Lambda → DynamoDB
        ↓
Kinesis Data Stream → Apache Flink (real-time processing)
```

---

## 📂 Project Structure
```
├── application.py        # Flask backend
├── requirements.txt      # Python dependencies
├── templates/
│   ├── base.html
│   ├── index.html        # Main dashboard
│   ├── login.html
│   ├── signup.html
│   └── confirm.html
├── static/
│   └── style.css         # Unified CSS (Light/Dark mode)
└── README.md
```

---

## ⚙️ Environment Variables
Create these in **Elastic Beanstalk** or your `.env` file:
```
TWEET_API_URL=https://<api-gateway-id>.execute-api.us-east-1.amazonaws.com/dev/tweets
COGNITO_CLIENT_ID=<your-cognito-app-client-id>
USER_POOL_ID=<your-user-pool-id>
AUTH_SECRET=<openssl rand -base64 16>
COGNITO_ID_TOKEN_EXPIRED=3600   # optional (seconds)
```

---

## 🔐 Authentication Flow
1. **Signup**  
   - User enters name, email, password.
   - Flask calls `cognito.sign_up()` → user created in Cognito.

2. **Confirm Account**  
   - User receives confirmation code via email.
   - Flask calls `cognito.confirm_sign_up()`.

3. **Login**  
   - Flask calls `cognito.initiate_auth()` → gets `id_token`.
   - Verifies token → creates `session_token` signed with `AUTH_SECRET`.
   - Stores `session_token` in **HTTP-only cookie**.

4. **Access Secured Pages**  
   - Flask validates `session_token` on each request.
   - When calling **API Gateway**, sends:
     ```
     Authorization: Bearer <id_token>
     ```

---

## ▶ How to Run Locally
```bash
# 1. Clone repo
git clone https://github.com/yourusername/tweet-dashboard.git
cd tweet-dashboard

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run app
export FLASK_APP=application.py
flask run
```

---

## ✅ API Gateway Authorizer Setup
1. Go to API Gateway → **Authorizers** → Create Cognito Authorizer.
2. Select **User Pool** and App Client.
3. Set **Token Source**: `Authorization`
4. Apply Authorizer to:
   - `POST /tweets`
   - (Optional) `GET /tweets`

---

## 🔑 How to Get `id_token` for Testing
- **Option 1 (Browser DevTools)**  
  Login → Check cookies → Copy `id_token`.

- **Option 2 (Postman)**  
  Login via `/login` (POST email & password) → Copy `id_token` from response cookies.

---

## 🛠 Tech Stack
- **Backend**: Flask, boto3, jwt
- **AWS Services**: Lambda, API Gateway, DynamoDB, Cognito, Kinesis, Apache Flink
- **Frontend**: HTML, CSS, JS, Chart.js

---

## 📌 Roadmap
- ✅ Add signup + confirmation flow
- ✅ Secure Lambda with Cognito Authorizer
- ✅ Session tokens with `AUTH_SECRET`
- 🔜 Refresh token & silent login
- 🔜 Deploy with CI/CD

---

### 👨‍💻 Author
Built by Imannuel Jeremi 
