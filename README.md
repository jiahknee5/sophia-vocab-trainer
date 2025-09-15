# 📚 Sophia's PSAT/SHSAT Vocabulary Trainer

A fun and interactive web application to help students learn vocabulary words for the PSAT and SHSAT exams. Built with a focus on daily learning habits - one word per day!

🌐 **Live Demo**: [home.johnnycchung.com](https://home.johnnycchung.com)

## 🌟 Features

- **Daily Vocabulary Learning**: Add one new word per day with definitions
- **Interactive Quizzes**: Test knowledge with multiple-choice questions
- **Progress Tracking**: Visual progress bars and achievement badges
- **Milestone Goals**: Track progress toward key exam dates
- **Mobile Optimized**: Perfect for iPhone and iPad use
- **Gamification**: Confetti animations and mastery levels

## 🎯 Learning Goals

The app tracks progress toward three key milestones:
- **Winter Goal**: December 31, 2025 (365 words)
- **Spring Goal**: March 31, 2026 (455 words)
- **Summer Goal**: June 30, 2026 (545 words)

## 🚀 Quick Start

### Local Development

1. Clone the repository
```bash
git clone https://github.com/jiahknee5/sophia-vocab-trainer.git
cd sophia-vocab-trainer
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run the application
```bash
python src/app.py
```

4. Open your browser to `http://localhost:5005`

### Deployment

This app is configured for easy deployment on Vercel:

1. Fork this repository
2. Connect your GitHub account to Vercel
3. Import this project
4. Add environment variables (if using external database)
5. Deploy!

## 📱 Mobile Features

- Optimized for iPhone with proper viewport scaling
- Touch-friendly buttons (minimum 44px tap targets)
- Collapsible navigation menu
- Native iOS font support
- Add to Home Screen capability
- Offline support for viewed pages

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite (local) / PostgreSQL (production)
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: Vercel
- **Domain**: Custom subdomain configuration

## 📊 Features Overview

### Add Words
Simple form to add new vocabulary with word and definition fields.

### Quiz Mode
- Multiple choice questions
- Instant feedback
- Confetti animation for correct answers
- Tracks mastery level per word

### Progress Tracking
- Total words learned
- Daily progress toward goals
- Achievement badges
- Accuracy statistics

## 🎨 Design

- Colorful, kid-friendly interface
- Large, easy-to-read fonts
- Engaging animations
- Progress visualization
- Responsive design for all devices

## 📝 Environment Variables

For production deployment, you can set:
- `DATABASE_URL`: PostgreSQL connection string (optional)
- `SECRET_KEY`: Flask secret key for sessions

## 🤝 Contributing

This is a personal project for educational purposes, but suggestions are welcome!

## 📄 License

MIT License - feel free to use this code for your own vocabulary learning apps!

---

Made with ❤️ for Sophia's test preparation journey