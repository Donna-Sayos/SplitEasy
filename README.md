<div align="center">

```text                                                             
   ███████╗██████╗ ██╗     ██╗████████╗███████╗ █████╗ ███████╗██╗   ██╗ 
   ██╔════╝██╔══██╗██║     ██║╚══██╔══╝██╔════╝██╔══██╗██╔════╝╚██╗ ██╔╝ 
   ███████╗██████╔╝██║     ██║   ██║   █████╗  ███████║███████╗ ╚████╔╝  
   ╚════██║██╔═══╝ ██║     ██║   ██║   ██╔══╝  ██╔══██║╚════██║  ╚██╔╝   
   ███████║██║     ███████╗██║   ██║   ███████╗██║  ██║███████║   ██║    
   ╚══════╝╚═╝     ╚══════╝╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚══════╝   ╚═╝    
```

# SplitEasy 🧾

**A full-stack group bill and meal splitter with automatic US state sales tax, Equal & Per-Meal itemized splitting, Guest Mode, and timestamped receipt history.**

<p align="center">
  <img src="https://img.shields.io/badge/Coming_Soon-019999">
  <!-- Once deployed on PythonAnywhere, delete the line above and uncomment the block below:
  <a href="https://YOUR_://pythonanywhere.com" target="_blank" rel="noopener noreferrer">
    <img src="https://shields.io" alt="Live Demo">
  </a>
  -->
</p>

</div>

---

## **✨ Core Features**

- **⚡ Instant Guest Mode:** Jump straight into calculating splits without creating an account, with selectable US state sales tax rates.
- **🔐 Account Creation & Saved Dashboard:** Register with a home state to auto-apply local sales tax, save calculated bills, and filter past receipts by exact date and time of entry.
- **🍽️ Equal & Per-Meal Splitting:** Split bills evenly across participants or switch to **Split Per Meal** (`+ Foods/Drinks`) so each person pays for their exact items plus an even share of tax and tip.
- **🧮 Custom Tax & Tip Controls:** Automatically pulls sales tax rates across all 50 US states + DC and supports `15%`, `18%`, `20%`, or `Custom` tip percentages.
- **👥 Frictionless Participant Entry:** Only the user saving a receipt needs an account—split participants are entered by name without requiring sign-ups.

---

## **🛠️ Tech Stack**

<p>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white">
  <img src="https://img.shields.io/badge/SQL-336791?style=for-the-badge&logo=postgresql&logoColor=white">
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black">
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white">
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white">
</p>

---

## **🗄️ Database Architecture (3NF)**

Designed in **Third Normal Form (3NF)** across five relational SQLite tables to eliminate transitive dependencies and repeating groups:

| Table Name | Primary Key | Foreign Key(s) | Purpose |
| :--- | :--- | :--- | :--- |
| **`StateTaxes`** | `state_code` | — | Stores US state codes, names, and sales tax rates |
| **`Users`** | `user_id` | `state_code` → `StateTaxes` | Stores registered user profiles and home state |
| **`Bills`** | `bill_id` | `user_id` → `Users` | Stores bill totals, split mode, tax, tip, and entry timestamp |
| **`BillParticipants`** | `participant_id` | `bill_id` → `Bills` | Stores participant names and calculated owed amounts |
| **`ParticipantItems`** | `item_id` | `participant_id` → `BillParticipants` | Stores individual food/drink items for Per-Meal splits |

---

## **🔌 RESTful API Endpoints**

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/states` | Fetches all US states and sales tax rates |
| `POST` | `/api/register` | Creates a new user account and starts a session |
| `POST` | `/api/login` | Authenticates an existing user |
| `GET` | `/api/bills` | Retrieves saved bills (supports `?date=YYYY-MM-DD` and `?time=HH:MM`) |
| `POST` | `/api/bills` | Saves an Equal or Per-Meal bill and its participant breakdown |

---

<div align="center">
  <sub>Built by <a href="https://linkedin.com">Donna Sayos</a> • Hunter College Computer Science</sub>
</div>
