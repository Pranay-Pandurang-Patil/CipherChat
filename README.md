# CipherChat

CipherChat is a simple real-time chat application built to learn and demonstrate Python socket programming, TCP client-server communication, SQLite database management, authentication, Flask API development, and frontend web development.

## Project Status

🚧 Backend and frontend integration is currently in progress.

## Completed

### Backend
- Python TCP socket server
- TCP client-server communication
- Multi-client support using threading
- Persistent messaging loop
- Newline-based message framing
- Receive buffer handling
- Clean client disconnect handling
- 1-to-1 private messaging logic
- Chat room messaging logic
- Six-digit room codes
- Maximum 10 members per room
- Room owner/member roles

### Authentication
- User registration
- User login
- Username validation
- Email validation
- Password validation
- Password hashing using PBKDF2-HMAC-SHA256
- Random password salt
- Duplicate username/email protection
- Duplicate online-user protection

### SQLite Database
- Users table
- Rooms table
- Room members table
- Messages table
- User registration storage
- Authentication data storage
- Private message storage
- Room message storage
- Room message history
- Private conversation history
- Room creation
- Room joining
- Room member management

### Flask API
- Flask API bridge created
- Health check endpoint
- Registration endpoint
- Login endpoint
- User listing endpoint
- Private message history endpoint
- Private message sending endpoint

Current endpoints:

GET /api/health
POST /api/register
POST /api/login
GET /api/users
GET /api/private-messages
POST /api/private-messages

### Frontend
- HTML frontend
- CSS styling
- JavaScript application logic
- Login interface
- Registration interface
- Home dashboard
- User search
- 1-to-1 chat interface
- Chat room interface
- Create room interface
- Join room interface
- Room members modal
- Message bubbles
- Responsive layout
- Navigation
- Logout
- Frontend registration connected to Flask API
- Frontend login connected to Flask API
- Frontend user search connected to Flask API
- Private chat history connected to Flask API
- Private message sending connected to Flask API

## Current Architecture

Frontend:
HTML + CSS + JavaScript

Backend Bridge:
Flask

Core Backend:
Python TCP Socket Server

Database:
SQLite

Architecture:

Frontend
    ↓
Flask API
    ↓
Python Backend
    ↓
SQLite

## Project Structure

CipherChat/
│
├── api/
│   └── app.py
│
├── client/
│   └── client.py
│
├── server/
│   ├── server.py
│   └── auth.py
│
├── database/
│   ├── database.py
│   └── cipherchat.db
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── docs/
│
├── tests/
│
├── requirements.txt
├── .gitignore
└── README.md

## Technology Stack

- Python
- Socket Programming
- TCP
- Threading
- Flask
- SQLite
- HTML5
- CSS3
- JavaScript
- Git
- GitHub

## Remaining Work

### Backend Integration
- Connect browser clients to the real-time Python TCP socket backend
- Implement real-time message delivery to the web frontend
- Connect room creation to the backend
- Connect room joining to the backend
- Load real rooms from SQLite
- Load real room members from SQLite
- Connect room messaging to the backend
- Handle browser connection and disconnection

### Frontend Cleanup
- Remove remaining demo users
- Remove remaining demo rooms
- Remove remaining demo message storage
- Add loading states
- Add connection/error states
- Final UI polishing

### Testing
- Registration testing
- Login testing
- Invalid login testing
- Duplicate registration testing
- User search testing
- Private messaging testing
- Private message persistence testing
- Room creation testing
- Room joining testing
- Room capacity testing
- Multiple-client testing
- Room message persistence testing
- Disconnect/reconnect testing

### Finalization
- Final README update
- API documentation
- Database documentation
- Architecture documentation
- Add screenshots
- Final code cleanup
- Final testing
- Final GitHub cleanup
- Final GitHub push

## Project Goal

CipherChat is intentionally designed as a practical learning and portfolio project.

The main learning goals are:

1. Python socket programming
2. TCP client-server communication
3. Multi-client communication
4. Threading and Multi threading
5. Message framing
6. SQLite database management
7. Authentication
8. Flask API development
9. HTML/CSS/JavaScript frontend integration
10. Git and GitHub

The project will be completed after the remaining backend integration, testing, frontend cleanup and documentation are finished.

## Author

Pranay Patil

CSE Student
KLS Gogte Institute of Technology, Belagavi
