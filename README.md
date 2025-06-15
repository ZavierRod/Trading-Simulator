# Trading Simulation Game

A full-stack trading simulation platform with order matching, trade persistence, positions/P\&L, and a live dashboard. Users can place buy/sell orders, view executed trades, see their net positions and unrealized profit/loss, and compete on a leaderboard in the future.

---

## 🚀 Features Implemented

### Backend

* **Order matching engine** (`POST /api/orders`)

  * Creates orders, matches buy/sell automatically, persists `Trade` records.
* **Trade blotter** (`GET /api/trades?limit=&cursor=`)

  * Cursor‐based pagination of executed trades.
* **Positions & P/L** (`GET /api/positions`)

  * Aggregates net quantity, average cost, last market price, and unrealized P/L per user.
* **User authentication** (in progress)

  * User sign-up & login endpoints issuing JWTs.
* **Unit & integration tests**

  * Pytest suite covering matcher logic and P/L calculations.

### Frontend

* **React + Vite scaffold**
* **Dashboard component**

  * Polls backend every 5s to display:

    * Open orders
    * Recent trades
    * Positions & P/L
* **Tailwind CSS via CDN**
* **Basic UI layout** with responsive cards

---

## 📦 Setup & Running

### Prerequisites

* Python 3.10+
* Node.js 18+ and npm
* Docker & Docker Compose (for Postgres DB)

### Backend

1. **Install Python deps**

   ```bash
   cd backend
   pip install -r requirements.txt
   ```
2. **Configure `.env`** (at repo root):

   ```ini
   DATABASE_URL=postgresql://postgres:password@localhost:5432/trading_sim
   SECRET_KEY=your-secret-key
   ```
3. **Run migrations**

   ```bash
   alembic upgrade head
   ```
4. **Start services**

   ```bash
   docker compose up --build
   ```

   FastAPI will run on [http://localhost:8000](http://localhost:8000)

### Frontend

1. **Install npm deps**

   ```bash
   cd frontend
   npm install
   ```
2. **Run dev server**

   ```bash
   npm run dev
   ```

   Vite will serve at [http://localhost:5173](http://localhost:5173)

---

## ✅ Completed Milestones

1. Order matching & trade persistence
2. Cursor-based pagination for trades
3. Positions & P/L aggregation
4. Unit tests for matching and P/L helper
5. Basic React dashboard with polling
6. User signup & login (JWT)

---

## 🛠 Next Steps

1. **Protect API routes** with JWT (add `Depends(get_current_user)`)
2. **Strategy upload & sandbox**

   * Allow users to upload Python strategy scripts
   * Execute in an isolated environment and auto-place orders
3. **Real market data ingestion**

   * Integrate a market-data API (IEX, Polygon, etc.)
   * Replace “last trade price” with live quotes
4. **Leaderboard**

   * Aggregate user performance (realized + unrealized P/L)
   * Expose `GET /api/leaderboard` and display on frontend
5. **Frontend enhancements**

   * Login/signup forms
   * Strategy editor/upload page
   * WebSocket for real‐time updates
   * Routing & polished UI

---

## 📣 Contributions

Feel free to open issues or pull requests for new features, bug fixes, or improvements. Your feedback and contributions are welcome!
