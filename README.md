# GigBoard

A web platform connecting performers and venue owners. Performers can browse gig listings, apply to shows, book lessons, and build their network. Venue owners can post gigs, review applications, manage their venues, and discover talent.

---

## Features

### For Performers
- Browse and apply to open gig listings with a cover message
- View application status (pending / accepted / declined)
- Calendar view of upcoming and past accepted gigs
- Browse venues and view open listings directly on the venue page
- Book lessons with other performers
- Offer lessons with available time slots
- Performer-to-performer networking with collaboration requests
- Public profile page with bio, music style, social links, and gig history

### For Venue Owners & Managers
- Create and manage venues
- Post gig listings with date, time, pay, and preferred style
- Review performer applications and accept or decline
- Calendar view of all upcoming events
- Browse and search performers by name, location, and style

### General
- Role-based accounts: Venue Owner, Manager, Performer, Fan
- Shared cloud database (Neon PostgreSQL) — live updates across all team members
- Demo seed data included

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, Django 6.0.3 |
| Database | PostgreSQL via [Neon](https://neon.tech) |
| Frontend | Bootstrap 5.3, Bootstrap Icons, FullCalendar.js |
| Auth | Django built-in authentication |

---

## Local Setup

### Prerequisites
- Python 3.10+
- Git
- A Neon account (free) — or ask a teammate for the shared `DATABASE_URL`

### 1. Clone the repo

```bash
git clone https://github.com/bhulse72/GigBoard.git
cd GigBoard
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install django psycopg2-binary dj-database-url python-dotenv Pillow whitenoise
```

### 4. Set up environment variables

Create a `.env` file in the project root (same level as `manage.py`):

```
DATABASE_URL=postgresql://your_user:your_password@your_host/neondb?sslmode=require
```

Get the `DATABASE_URL` from a teammate — never commit this file.

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. (Optional) Seed demo data

```bash
python manage.py seed_demo
```

This creates 6 demo accounts, 3 venues, 6 gig listings, and sample applications.

| Username | Password | Role |
|---|---|---|
| `nova_venue` | `demo1234` | Venue Owner |
| `thatch_club` | `demo1234` | Venue Owner |
| `djsolara` | `demo1234` | Performer |
| `marcwave` | `demo1234` | Performer |
| `lunasound` | `demo1234` | Performer |
| `gigfan_alex` | `demo1234` | Fan |

> Safe to run multiple times — skips existing records.

### 7. Start the development server

```bash
python manage.py runserver
```

Visit [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## Project Structure

```
GigBoard/
├── accounts/       # Custom user model, login, profile
├── venues/         # Venue management, browsing, public detail
├── gigs/           # Gig listings, applications, calendar
├── performers/     # Directory, profiles, collaboration requests
├── lessons/        # Lesson listings, time slots, bookings
├── fans/           # Fan role (in progress)
├── core/           # Home page
├── templates/      # All HTML templates
├── static/css/     # main.css
└── GigBoard/       # Django project settings and URLs
```

---

## Team Workflow

- Everyone connects to the **same Neon database** — no need to sync local data
- Share the `DATABASE_URL` directly with teammates (Slack, Discord, etc.) — never via git
- Each person creates their own `.env` file locally
- Run `python manage.py migrate` after pulling changes that include new migrations
- Use feature branches and pull requests — coordinate schema changes before running migrations

---

## Contributing

1. Pull latest `main` before starting work
2. Create a feature branch: `git checkout -b your-name/feature-name`
3. Make changes, commit, and push
4. Open a pull request into `main`
5. Resolve any merge conflicts before merging (especially in `migrations/`)
