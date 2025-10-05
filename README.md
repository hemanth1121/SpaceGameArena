# 🚀 Space Game Arena

**Space Game Arena** is an interactive financial modeling dashboard for analyzing the economic viability of a suborbital entertainment station. It provides real-time visualization of CAPEX, OPEX, revenue projections, and profitability over a 10-year horizon.

---

## 📋 Core Concept

- Model economics of operating a suborbital gaming station
- Configure crew, contestants, spectators, and operational parameters
- Track multiple revenue streams (sponsorships, broadcasting, tickets, merchandise)
- Analyze CAPEX, OPEX, and profitability with flexible amortization options
- Visualize 10-year financial projections with adjustable growth rates

---

## 🛠️ Setup

```bash
# Clone repository
git clone https://github.com/hemanth1121/SpaceGameArena.git
cd SpaceGameArena

# Install dependencies
pip install dash dash-bootstrap-components plotly pandas

# Run the application
python financial_model.py
```

Dashboard available at `http://localhost:8050`

---

## 🎮 How to Use

### Configure Parameters (Left Sidebar)
- **Crew & Contestants**: Adjust operational personnel and participant counts
- **Spectators**: Enable Phase 2 and set spectator capacity and ticket pricing
- **CAPEX Scaling**: Enable dynamic capacity scaling
- **Amortization**: Configure CAPEX spreading over time (auto or manual)

### Monitor Dashboard
- **Key Metrics**: View CAPEX, OPEX, and revenue cards
- **10-Year Chart**: Track revenue growth and net profit trends
- **Projection Table**: Review detailed year-by-year breakdown
- **Concept Summary** (Right Sidebar): Learn about station design and assumptions

---

## 📊 Financial Model

### Baseline Configuration
- Crew: 15 | Contestants: 12 | Spectators: 0-200
- Station: 300-400 tons, ~9,500 sq ft
- Base CAPEX: $5.7B (without spectators), $7.2B (with spectators)

### Key Costs
- Transport: $65M (crew/contestant), $55M (spectator)
- Annual Salaries: $317K per crew
- Prize Pool: $1.667M per contestant
- Recurring OPEX: ~$902M/year

### Revenue Streams
- Sponsorship: $600M | Broadcasting: $550M
- VR/AR: $100M | Merchandise: $200M
- Annual Growth: 10%

---

## 🔧 Technical Stack

Python | Dash | Plotly | Dash Bootstrap Components | Pandas

---

## 🎯 Use Cases

Business planning • Investor presentations • Educational tool • Research • Scenario analysis

---
**⭐ Star this repository if you find it useful!**
