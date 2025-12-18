# Finance Management Application

## 1. Introduction

The Finance Management Application is a Python-based desktop application designed to help users record and manage their personal finances. The system allows users to log in, add income and expense transactions, calculate total balances, and store data locally.

This project was developed as a learning exercise to practice Python programming, graphical user interface (GUI) development, and basic data management techniques.

---

## 2. Objectives

The objectives of this project are:
- To design a user-friendly financial management system
- To practice GUI development using Tkinter
- To implement modular programming using multiple Python files
- To store and retrieve data using JSON files
- To integrate sound effects using pygame

---

## 3. Technologies Used

- **Python 3**
- **Tkinter** – Graphical User Interface (GUI)
- **pygame** – Sound effects
- **JSON** – Data storage
- **Pillow (PIL)** – Image handling

---

## 4. System Features

- User login and authentication
- Add income transactions
- Add expense transactions
- Automatic calculation of total balance
- Data persistence using JSON files
- Sound effects for user interactions

---

## 5. Use of pygame

The pygame library is used exclusively for **sound effects**, including:
- Button click sounds
- Confirmation sounds
- Page and tab switching feedback

The graphical interface is built using Tkinter, while pygame handles audio playback.

---

## 6. Project Structure

```
project/
│
├─ images/
├─ sound_effect/
│
├─ main.py
├─ finance_app.py
├─ login_manager.py
├─ splash.py
├─ pages.py
├─ tabs.py
├─ add_trans.py
├─ data.py
├─ utils.py
│
├─ users.json
├─ user_avatars.json
├─ transactions.json
│
└─ README.md
```

---

## 7. How to Run the Application

### Step 1: Install Required Libraries

```bash
pip install pygame pillow
```

### Step 2: Run the Application

```bash
python main.py
```

---

## 8. Data Storage

Data is stored locally using JSON files to maintain user accounts and transaction records.

---

## 9. Learning Outcomes

- GUI development with Tkinter
- Modular Python programming
- JSON data handling
- Integrating pygame for sound effects
- Project structure organization

---

## 10. Conclusion

This project demonstrates a functional finance management system using Python, Tkinter, and pygame. It serves as a solid foundation for future expansion.

---

## 11. Future Improvements

- Database integration
- Financial charts and reports
- Enhanced security features
