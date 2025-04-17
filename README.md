# Effect CRM

A modern Customer Relationship Management system built with Flask, featuring AI-powered interaction analysis. Developed by [Kien Ventures](https://kien.vc).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0%2B-green)](https://flask.palletsprojects.com/)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](CONTRIBUTING.md)

## 🌟 Features

- **User Authentication & Authorization**
  - Secure login and registration
  - Role-based access control
  - Password recovery functionality

- **Customer Management**
  - Create, Read, Update, Delete (CRUD) operations
  - Contact information tracking
  - Status management
  - Notes and interaction history
  - Custom fields support

- **AI-Powered Interaction Analysis**
  - Integration with Claude and OpenAI
  - Sentiment analysis
  - Action item extraction
  - Summary generation
  - Customizable analysis templates

- **Modern UI with Bootstrap 5**
  - Responsive design
  - Dark/light mode
  - Interactive dashboards
  - Data visualization

- **Secure Data Handling**
  - Data encryption
  - GDPR compliance
  - Regular backups
  - Audit logging

- **RESTful API Design**
  - Comprehensive API documentation
  - OAuth2 authentication
  - Rate limiting
  - Webhook support

## 🛠️ Tech Stack

- **Backend**: Flask, Python 3.8+
- **Database**: SQLAlchemy with SQLite (PostgreSQL support coming soon)
- **Frontend**: Bootstrap 5, JavaScript, jQuery
- **Authentication**: Flask-Login, JWT
- **AI Integration**: Anthropic Claude & OpenAI GPT
- **Other**: Python-dotenv, Flask-Migrate, Flask-WTF

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/kientranasia/effect-crm.git
cd effect-crm
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory:
```
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///crm.db
ANTHROPIC_API_KEY=your-anthropic-api-key
OPENAI_API_KEY=your-openai-api-key
```

5. Initialize the database:
```bash
flask db upgrade
```

6. Run the development server:
```bash
python run.py
```

The application will be available at `http://127.0.0.1:5000`.

## 📁 Project Structure

```
effect-crm/
├── app/
│   ├── __init__.py          # Application factory
│   ├── models.py             # Database models
│   ├── routes.py             # Main routes
│   ├── modules/              # Feature modules
│   │   ├── auth/             # Authentication module
│   │   └── customers/        # Customer management module
│   ├── static/               # Static files (CSS, JS, images)
│   └── templates/            # HTML templates
├── instance/                 # Instance-specific files
├── migrations/               # Database migrations
├── tests/                    # Test suite
├── venv/                     # Virtual environment
├── .env                      # Environment variables
├── .gitignore                # Git ignore file
├── requirements.txt          # Python dependencies
├── run.py                    # Application entry point
└── README.md                 # Project documentation
```

## 🤝 Contributing

We welcome contributions from the community! Whether you're fixing a bug, adding a feature, or improving documentation, your help is greatly appreciated.

### How to Contribute

1. **Fork the repository** on GitHub
2. **Create a new branch** for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** and commit them:
   ```bash
   git add .
   git commit -m "Add your feature description"
   ```
4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
5. **Create a Pull Request** on GitHub

### Development Guidelines

- Follow PEP 8 style guide for Python code
- Write tests for new features
- Update documentation as needed
- Keep commits focused and atomic
- Use meaningful commit messages

### Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing to this project.

## 📝 Roadmap

- [ ] Multi-tenant support
- [ ] Advanced reporting and analytics
- [ ] Mobile application
- [ ] Integration with popular CRM platforms
- [ ] Enhanced AI capabilities
- [ ] API rate limiting and monitoring
- [ ] User activity dashboard
- [ ] Automated backup system

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💬 Support

For support, please:
- Visit [kien.vc](https://kien.vc)
- Open an issue in the GitHub repository
- Join our [Discord community](https://discord.gg/effect-crm)

## 🙏 Acknowledgments

- Flask documentation and community
- Bootstrap team for the amazing UI framework
- Anthropic and OpenAI for AI capabilities
- All contributors who have helped shape this project

## 📊 Project Status

![GitHub Stars](https://img.shields.io/github/stars/kientranasia/effect-crm)
![GitHub Forks](https://img.shields.io/github/forks/kientranasia/effect-crm)
![GitHub Issues](https://img.shields.io/github/issues/kientranasia/effect-crm)
![GitHub Pull Requests](https://img.shields.io/github/issues-pr/kientranasia/effect-crm) 