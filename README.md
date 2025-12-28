# Advanced Expense Tracker

A modern, user-friendly expense tracking application built with Python using **CustomTkinter** for the GUI, **SQLite** for data storage, and **Matplotlib** for visualizations.

## Features

- **User Authentication**: Secure login system with username and password.
- **Role-Based Access**:
  - **Admin**: Can add and delete expenses.
  - **Regular User**: Can only add and view their own expenses.
- **Expense Management**:
  - Add expenses with date, category, amount, and notes.
  - View all expenses in a scrollable list.
  - See total expenses in real-time.
  - Delete selected expenses (admin only).
- **Data Visualization**: Pie chart showing expense distribution by category.
- **Dark Mode UI**: Clean and modern interface using CustomTkinter.

## Default Login Credentials

The application comes with two pre-configured users:

| Username   | Password | Role  |
|------------|----------|-------|
| Himanshu   | 0055     | admin |
| user       | user123  | user  |

## Requirements

- Python 3.6 or higher
- Required Python packages:
  - `customtkinter`
  - `matplotlib`

## Installation

1. Clone or download this project.
2. Install the required packages:
   ```bash
   pip install customtkinter matplotlib
