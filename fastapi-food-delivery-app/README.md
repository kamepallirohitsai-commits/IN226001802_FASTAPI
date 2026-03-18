# FastAPI Food Delivery App (Final Project)

This is the final project for the FastAPI internship training at Innomatics Research Labs.

## Project Overview

A comprehensive backend API for a **Food Delivery App** built with FastAPI. The application implements all concepts learned during the 6-day training, including GET/POST endpoints, Pydantic validation, helper functions, CRUD operations, multi-step workflows, and advanced features like search, sorting, and pagination.

## Features Implemented

### Day 1: GET APIs
- Home route (`/`)
- List all menu items (`/menu`)
- Get menu item by ID (`/menu/{item_id}`)
- Menu summary endpoint (`/menu/summary`)

### Day 2: POST + Pydantic Validation
- Create menu items with validation (`POST /menu`)
- Field constraints (min_length, max_length, gt, le)
- Error handling for invalid inputs

### Day 3: Helper Functions & Filtering
- Helper functions: `find_menu_item()`, `calculate_order_total()`, `filter_menu_items()`
- Advanced filtering endpoint (`/menu/search`) with query parameters

### Day 4: CRUD Operations
- Create menu items (`POST /menu`) - returns 201 Created
- Update menu items (`PUT /menu/{item_id}`)
- Delete menu items (`DELETE /menu/{item_id}`) - with business rules (404/400 handling)

### Day 5: Multi-Step Workflow (Cart → Order → Status)
- Add items to cart (`POST /cart/add`)
- Place orders (`POST /orders`) - clears cart, creates order
- List orders (`GET /orders`)
- Get order by ID (`GET /orders/{order_id}`)
- Update order status (`POST /orders/{order_id}/status`)

### Day 6: Advanced APIs (Search, Sort, Pagination)
- Sort menu items (`GET /menu/sort`)
- Paginate menu items (`GET /menu/paginate`)
- Browse orders with search/sort/pagination (`GET /orders/browse`)
- Combined browsing endpoint (`GET /browse`) - all params optional

## Project Structure

- `main.py` - Main FastAPI application with all endpoints and models
- `requirements.txt` - Python dependencies
- `screenshots/` - Screenshots of all 20 API endpoints tested in Swagger UI (Q1_Output.png to Q18_Output.png)

## Installation & Setup

1. **Clone or navigate to the project directory:**
   ```bash
   cd Food_Delivery_App
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   uvicorn main:app --reload
   ```

4. **Access the API:**
   - Swagger UI: http://127.0.0.1:8000/docs
   - ReDoc: http://127.0.0.1:8000/redoc

## Sample Data

The app loads sample menu items on startup for testing:
- Margherita Pizza
- Veggie Burger
- French Fries
- Cold Soda

## API Testing

All endpoints have been tested and screenshots captured for submission. The app follows FastAPI route order rules (fixed routes before variable routes).

## Technologies Used

- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for running the app
- **Python 3.8+**: Programming language

## Submission Details

This project implements 20 tasks covering all 6 days of FastAPI training. Ready for GitHub upload and LinkedIn sharing.

**GitHub Repository Name Suggestion:** `fastapi-food-delivery-app`

**LinkedIn Post Example:**
🚀 FastAPI Final Project Completed!

I built a complete backend system using FastAPI as part of my internship training at @Innomatics Research Labs.

Project: Food Delivery App

Key Features:
• REST APIs with FastAPI
• Pydantic data validation
• CRUD operations
• Multi-step workflows (Cart → Order → Delivery)
• Search, sorting, and pagination
• API testing using Swagger UI

GitHub Repository: [Your Repo Link]

#FastAPI #Python #BackendDevelopment #APIDevelopment #InnomaticsResearchLabs
