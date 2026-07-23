#!/usr/bin/env python3
"""
Intelligent Analysis and Optimization System for Restaurant Supply Chains
Main entry point - CLI application
"""
import sys
import os
import csv
from datetime import datetime
from collections import defaultdict

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")


# ============================================================================
# Data Models
# ============================================================================

class Dish:
    def __init__(self, dish_id, name, category, price, cooking_time):
        self.dish_id = int(dish_id)
        self.name = name
        self.category = category
        self.price = float(price)
        self.cooking_time = int(cooking_time)


class Ingredient:
    def __init__(self, dish_id, ingredient_name, quantity, unit, cost_per_unit, allergen=""):
        self.dish_id = int(dish_id)
        self.ingredient_name = ingredient_name
        self.quantity = float(quantity)
        self.unit = unit
        self.cost_per_unit = float(cost_per_unit)
        self.allergen = allergen.strip() if allergen else ""

    @property
    def total_cost(self):
        return self.quantity * self.cost_per_unit


class Order:
    def __init__(self, order_id, dish_id, quantity, sale_time, settlement_price):
        self.order_id = int(order_id)
        self.dish_id = int(dish_id)
        self.quantity = int(quantity)
        self.sale_time = datetime.strptime(sale_time, "%Y-%m-%d %H:%M:%S")
        self.settlement_price = float(settlement_price)


# ============================================================================
# Data Store
# ============================================================================

class DataStore:
    def __init__(self):
        self.dishes = {}
        self.ingredients = {}
        self.orders = []
        self._next_dish_id = 1
        self.load_initial_data()

    def load_initial_data(self):
        dishes_file = os.path.join(DATA_DIR, "dishes.csv")
        if os.path.exists(dishes_file):
            with open(dishes_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    dish = Dish(
                        dish_id=int(row['dish_id']),
                        name=row['name'],
                        category=row['category'],
                        price=row['price'],
                        cooking_time=row['cooking_time']
                    )
                    self.dishes[dish.dish_id] = dish
                    if dish.dish_id >= self._next_dish_id:
                        self._next_dish_id = dish.dish_id + 1

        ingredients_file = os.path.join(DATA_DIR, "ingredients.csv")
        if os.path.exists(ingredients_file):
            self._load_ingredients_file(ingredients_file)

        orders_file = os.path.join(DATA_DIR, "orders.csv")
        if os.path.exists(orders_file):
            with open(orders_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    order = Order(
                        order_id=row['order_id'],
                        dish_id=row['dish_id'],
                        quantity=row['quantity'],
                        sale_time=row['sale_time'],
                        settlement_price=row['settlement_price']
                    )
                    self.orders.append(order)

    def _load_ingredients_file(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                ingredient = Ingredient(
                    dish_id=row['dish_id'],
                    ingredient_name=row['ingredient_name'],
                    quantity=row['quantity'],
                    unit=row['unit'],
                    cost_per_unit=row['cost_per_unit'],
                    allergen=row.get('allergen', '')
                )
                dish_id = ingredient.dish_id
                if dish_id not in self.ingredients:
                    self.ingredients[dish_id] = []
                self.ingredients[dish_id].append(ingredient)

    def add_dish(self, name, category, price, cooking_time):
        dish_id = self._next_dish_id
        self._next_dish_id += 1
        dish = Dish(dish_id, name, category, price, cooking_time)
        self.dishes[dish_id] = dish
        return dish

    def delete_dish(self, dish_id):
        if dish_id in self.dishes:
            name = self.dishes[dish_id].name
            del self.dishes[dish_id]
            if dish_id in self.ingredients:
                del self.ingredients[dish_id]
            return True, name
        return False, None

    def update_dish(self, dish_id, name=None, category=None, price=None, cooking_time=None):
        if dish_id not in self.dishes:
            return None
        dish = self.dishes[dish_id]
        if name is not None:
            dish.name = name
        if category is not None:
            dish.category = category
        if price is not None:
            dish.price = float(price)
        if cooking_time is not None:
            dish.cooking_time = int(cooking_time)
        return dish

    def search_dishes(self, term, search_type="both"):
        results = []
        term_lower = term.lower().strip()
        for dish in self.dishes.values():
            name_match = term_lower in dish.name.lower()
            category_match = term_lower in dish.category.lower()
            if search_type == "name" and name_match:
                results.append(dish)
            elif search_type == "category" and category_match:
                results.append(dish)
            elif search_type == "both" and (name_match or category_match):
                results.append(dish)
        return results

    def get_dish_ingredients(self, dish_id):
        return self.ingredients.get(dish_id, [])

    def import_ingredients_from_file(self, filepath):
        new_ingredients = {}
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                ingredient = Ingredient(
                    dish_id=row['dish_id'],
                    ingredient_name=row['ingredient_name'],
                    quantity=row['quantity'],
                    unit=row['unit'],
                    cost_per_unit=row['cost_per_unit'],
                    allergen=row.get('allergen', '')
                )
                dish_id = ingredient.dish_id
                if dish_id not in new_ingredients:
                    new_ingredients[dish_id] = []
                new_ingredients[dish_id].append(ingredient)

        for dish_id, ingredients_list in new_ingredients.items():
            if dish_id in self.ingredients:
                self.ingredients[dish_id].extend(ingredients_list)
            else:
                self.ingredients[dish_id] = ingredients_list

        return sum(len(v) for v in new_ingredients.values())

    def import_dishes_from_file(self, filepath, progress_callback=None):
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        total = len(rows)
        imported = 0
        for i, row in enumerate(rows):
            self.add_dish(
                name=row['name'],
                category=row['category'],
                price=row['price'],
                cooking_time=row['cooking_time']
            )
            imported += 1
            if progress_callback:
                progress_callback(i + 1, total)

        return imported

    def get_allergen_dishes(self):
        ALLERGEN_CATEGORIES = {
            'Crustacean': ['shrimp', 'prawn', 'crab', 'lobster', 'crustacean'],
            'Nut': ['peanut', 'tree nut', 'walnut', 'almond', 'cashew', 'pecan', 'nut'],
            'Egg': ['egg', 'egg white', 'egg yolk'],
            'Soybean': ['soybean', 'soy', 'tofu', 'doubanjiang', 'soy sauce'],
            'Milk': ['milk', 'cheese', 'cream', 'butter', 'dairy'],
            'Wheat': ['wheat', 'flour', 'gluten', 'bread'],
            'Fish': ['fish', 'salmon', 'tuna', 'cod'],
            'Sesame': ['sesame', 'sesame oil']
        }

        allergen_dishes = []
        for dish_id, ingredients_list in self.ingredients.items():
            if dish_id not in self.dishes:
                continue
            dish = self.dishes[dish_id]
            detected_allergens = set()
            for ing in ingredients_list:
                if ing.allergen:
                    allergen_name = ing.allergen.strip()
                    if allergen_name:
                        mapped = self._map_allergen(allergen_name, ALLERGEN_CATEGORIES)
                        detected_allergens.add(mapped if mapped else allergen_name)
            if detected_allergens:
                allergen_dishes.append((dish, detected_allergens))
        return allergen_dishes

    def _map_allergen(self, allergen_name, categories):
        allergen_lower = allergen_name.lower()
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in allergen_lower:
                    return category
        return allergen_name

    def get_sales_analysis(self, dimension="day"):
        if not self.orders:
            return []

        results = {}
        for order in self.orders:
            if dimension == "day":
                key = order.sale_time.strftime("%Y-%m-%d")
            elif dimension == "week":
                iso = order.sale_time.isocalendar()
                key = f"{iso[0]}-W{iso[1]:02d}"
            elif dimension == "month":
                key = order.sale_time.strftime("%Y-%m")
            else:
                key = order.sale_time.strftime("%Y-%m-%d")

            if key not in results:
                results[key] = {"period": key, "total_quantity": 0, "total_revenue": 0.0}
            results[key]["total_quantity"] += order.quantity
            results[key]["total_revenue"] += order.quantity * order.settlement_price

        return sorted(results.values(), key=lambda x: x["period"])


# ============================================================================
# UI Helpers
# ============================================================================

def print_separator(char="=", length=60):
    print(char * length)


def print_table(headers, rows, col_widths=None):
    if not col_widths:
        col_widths = []
        for i, header in enumerate(headers):
            max_width = len(header)
            for row in rows:
                if i < len(row):
                    max_width = max(max_width, len(str(row[i])))
            col_widths.append(max_width + 2)

    separator_line = "+"
    header_line = "|"
    for i, header in enumerate(headers):
        w = col_widths[i] if i < len(col_widths) else 10
        separator_line += "-" * (w + 2) + "+"
        header_line += f" {header:<{w}} |"
    print(separator_line)
    print(header_line)
    print(separator_line)

    for row in rows:
        row_line = "|"
        for i, cell in enumerate(row):
            w = col_widths[i] if i < len(col_widths) else 10
            row_line += f" {str(cell):<{w}} |"
        print(row_line)

    print(separator_line)


def print_progress_bar(current, total, width=50):
    if total == 0:
        return
    percent = current / total
    filled = int(width * percent)
    bar = '█' * filled + '░' * (width - filled)
    sys.stdout.write(f'\r  Progress: [{bar}] {percent:.0%} ({current}/{total})')
    sys.stdout.flush()
    if current == total:
        print()


def format_dish_table(dishes):
    if not dishes:
        print("  No dishes found.")
        return
    headers = ["ID", "Name", "Category", "Price", "Cooking Time"]
    rows = [[d.dish_id, d.name, d.category, f"${d.price:.2f}", f"{d.cooking_time} min"] for d in dishes]
    print_table(headers, rows)


# ============================================================================
# Dish Data Management Module
# ============================================================================

def dish_management_menu(store):
    while True:
        print()
        print_separator()
        print("  === Dish Data Management ===")
        print("  1. Add Dish")
        print("  2. Delete Dish")
        print("  3. Update Dish")
        print("  4. Search Dish")
        print("  5. Batch Import Dishes")
        print("  6. Import Ingredients")
        print("  7. Return to Main Menu")
        print_separator()
        choice = input("  Please select an option: ").strip()

        if choice == "1":
            add_dish(store)
        elif choice == "2":
            delete_dish(store)
        elif choice == "3":
            update_dish(store)
        elif choice == "4":
            search_dish_interactive(store)
        elif choice == "5":
            batch_import_dishes(store)
        elif choice == "6":
            import_ingredients(store)
        elif choice == "7":
            break
        else:
            print("  Invalid input, please try again")


def add_dish(store):
    print()
    name = input("  Enter dish name: ").strip()
    category = input("  Enter category: ").strip()
    price = input("  Enter price: ").strip()
    cooking_time = input("  Enter cooking time (minutes): ").strip()
    try:
        dish = store.add_dish(name, category, float(price), int(cooking_time))
        print(f"  Successfully added dish '{dish.name}' (ID: {dish.dish_id})")
    except ValueError:
        print("  Error: Invalid price or cooking time.")


def delete_dish(store):
    print()
    print("  Current dishes:")
    format_dish_table(list(store.dishes.values()))
    dish_id_str = input("  Enter dish ID to delete: ").strip()
    try:
        dish_id = int(dish_id_str)
        if dish_id not in store.dishes:
            print(f"  Error: Dish with ID {dish_id} not found.")
            return
        dish = store.dishes[dish_id]
        confirm = input(f"  Confirm deletion of '{dish.name}' (ID: {dish_id})? (y/n): ").strip().lower()
        if confirm == 'y':
            success, name = store.delete_dish(dish_id)
            if success:
                print(f"  Successfully deleted dish '{name}' (ID: {dish_id})")
        else:
            print("  Deletion cancelled.")
    except ValueError:
        print("  Error: Invalid dish ID.")


def update_dish(store):
    print()
    print("  Current dishes:")
    format_dish_table(list(store.dishes.values()))
    dish_id_str = input("  Enter dish ID to update: ").strip()
    try:
        dish_id = int(dish_id_str)
    except ValueError:
        print("  Error: Invalid dish ID.")
        return
    if dish_id not in store.dishes:
        print(f"  Error: Dish with ID {dish_id} not found.")
        return
    dish = store.dishes[dish_id]
    print(f"  Updating dish: {dish.name} (ID: {dish_id})")
    print("  Press Enter to keep current value.")
    name = input(f"  Enter new name [{dish.name}]: ").strip()
    category = input(f"  Enter new category [{dish.category}]: ").strip()
    price = input(f"  Enter new price [{dish.price}]: ").strip()
    cooking_time = input(f"  Enter new cooking time [{dish.cooking_time}]: ").strip()
    updated = store.update_dish(
        dish_id,
        name=name if name else None,
        category=category if category else None,
        price=price if price else None,
        cooking_time=cooking_time if cooking_time else None
    )
    print(f"  Successfully updated dish '{updated.name}' (ID: {dish_id})")


def search_dish_interactive(store):
    """Search dish with type selection (name/category)."""
    print()
    print("  Search by:")
    print("  1. Name")
    print("  2. Category")
    choice = input("  Please select search type: ").strip()
    if choice == "1":
        search_type = "name"
        term = input("  Enter dish name to search: ").strip()
    elif choice == "2":
        search_type = "category"
        term = input("  Enter category to search: ").strip()
    else:
        term = choice
        search_type = "both"
    if not term:
        print("  No search term provided.")
        return
    _display_search_results(store, term, search_type)


def search_dish_direct(store, term):
    """Direct search by both name and category (for main menu option 4)."""
    _display_search_results(store, term, "both")


def _display_search_results(store, term, search_type):
    results = store.search_dishes(term, search_type)
    if results:
        print(f"\n  Found {len(results)} dish(es):")
        format_dish_table(results)
        for dish in results:
            print(f"  Record entry for {dish.name}: ID={dish.dish_id}, Category={dish.category}, Price=${dish.price:.2f}, Cooking Time={dish.cooking_time} min")
    else:
        print(f"  No dishes found matching '{term}'.")


def batch_import_dishes(store):
    print()
    use_default = input("  Use default file path (data/dishes.csv)? (y/n): ").strip().lower()
    if use_default == 'y':
        filepath = os.path.join(DATA_DIR, "dishes.csv")
    else:
        filepath = input("  Enter CSV file path: ").strip()
    if not os.path.exists(filepath):
        print(f"  Error: File '{filepath}' not found.")
        return
    try:
        imported = store.import_dishes_from_file(filepath, progress_callback=print_progress_bar)
        print(f"  Successfully imported {imported} dish(es).")
    except Exception as e:
        print(f"  Error importing dishes: {e}")


def import_ingredients(store):
    print()
    use_default = input("  Use default file path (data/ingredients.csv)? (y/n): ").strip().lower()
    if use_default == 'y':
        filepath = os.path.join(DATA_DIR, "ingredients.csv")
    else:
        filepath = input("  Enter CSV file path: ").strip()
    if not os.path.exists(filepath):
        print(f"  Error: File '{filepath}' not found.")
        return
    try:
        count = store.import_ingredients_from_file(filepath)
        print(f"  Successfully imported {count} ingredient record(s).")
    except Exception as e:
        print(f"  Error importing ingredients: {e}")


# ============================================================================
# Ingredient and Cost Analysis Module
# ============================================================================

def ingredient_analysis_menu(store):
    while True:
        print()
        print_separator()
        print("  === Ingredient and Cost Analysis ===")
        print("  1. Analyze Dish Cost")
        print("  2. Allergen Identification")
        print("  3. Return to Main Menu")
        print_separator()
        choice = input("  Please select an option: ").strip()

        if choice == "1":
            analyze_dish_cost(store)
        elif choice == "2":
            identify_allergens(store)
        elif choice == "3":
            break
        else:
            print("  Invalid input, please try again")


def analyze_dish_cost(store):
    print()
    print("  Current dishes:")
    format_dish_table(list(store.dishes.values()))
    dish_id_str = input("  Enter dish ID to analyze: ").strip()
    try:
        dish_id = int(dish_id_str)
    except ValueError:
        print("  Error: Invalid dish ID.")
        return
    if dish_id not in store.dishes:
        print(f"  Error: Dish with ID {dish_id} not found.")
        return
    dish = store.dishes[dish_id]
    ingredients = store.get_dish_ingredients(dish_id)
    if not ingredients:
        print(f"  No ingredient data found for '{dish.name}'.")
        return
    total_ingredient_cost = sum(ing.total_cost for ing in ingredients)
    gross_profit = dish.price - total_ingredient_cost
    gross_margin = (gross_profit / dish.price * 100) if dish.price > 0 else 0
    print()
    print(f"  === Cost Analysis: {dish.name} (ID: {dish_id}) ===")
    print(f"  Selling Price: ${dish.price:.2f}")
    print(f"  Total Ingredient Cost: ${total_ingredient_cost:.2f}")
    print(f"  Gross Profit: ${gross_profit:.2f}")
    print(f"  Gross Profit Margin: {gross_margin:.1f}%")
    print()
    print("  Ingredient Cost Breakdown:")
    headers = ["Ingredient", "Quantity", "Unit", "Cost/Unit", "Total Cost", "Cost %", "Allergen"]
    rows = []
    for ing in ingredients:
        cost_pct = (ing.total_cost / total_ingredient_cost * 100) if total_ingredient_cost > 0 else 0
        rows.append([
            ing.ingredient_name, f"{ing.quantity:.2f}", ing.unit,
            f"${ing.cost_per_unit:.2f}", f"${ing.total_cost:.2f}",
            f"{cost_pct:.1f}%", ing.allergen if ing.allergen else "-"
        ])
    print_table(headers, rows)


def identify_allergens(store):
    print()
    print("  === Allergen Identification ===")
    allergen_dishes = store.get_allergen_dishes()
    if not allergen_dishes:
        print("  No allergens detected in any dish.")
        return
    print(f"  Found {len(allergen_dishes)} dish(es) containing allergens:")
    print()
    headers = ["Dish ID", "Dish Name", "Allergens"]
    rows = []
    for dish, allergens in allergen_dishes:
        allergen_str = ", ".join(sorted(allergens))
        rows.append([dish.dish_id, dish.name, allergen_str])
        print(f"  Dish '{dish.name}' (ID: {dish.dish_id}) contains allergens: {allergen_str}")
    print()
    print_table(headers, rows)


# ============================================================================
# Sales Data Analysis Module
# ============================================================================

def sales_analysis_menu(store):
    while True:
        print()
        print_separator()
        print("  === Sales Data Analysis ===")
        print("  1. Daily Analysis")
        print("  2. Weekly Analysis")
        print("  3. Monthly Analysis")
        print("  4. Return to Main Menu")
        print_separator()
        choice = input("  Please select an option: ").strip()

        if choice == "1":
            display_sales_analysis(store, "day")
        elif choice == "2":
            display_sales_analysis(store, "week")
        elif choice == "3":
            display_sales_analysis(store, "month")
        elif choice == "4":
            break
        else:
            print("  Invalid input, please try again")


def display_sales_analysis(store, dimension):
    print()
    dimension_name = {"day": "daily", "week": "weekly", "month": "monthly"}[dimension]
    print(f"  === Sales Trend Analysis ({dimension_name.capitalize()} Analysis) ===")
    results = store.get_sales_analysis(dimension)
    if not results:
        print("  No sales data available.")
        return
    print(f"  Sales trend analysis ({dimension_name} analysis) list:")
    print()
    headers = ["Period", "Total Quantity", "Total Revenue"]
    rows = [[r["period"], r["total_quantity"], f"${r['total_revenue']:.2f}"] for r in results]
    print_table(headers, rows)
    print()
    print("  Sales Volume Chart:")
    max_qty = max(r["total_quantity"] for r in results) if results else 1
    for r in results:
        bar_len = int(r["total_quantity"] / max_qty * 40) if max_qty > 0 else 0
        bar = '█' * bar_len
        print(f"  {r['period']}: {bar} {r['total_quantity']}")


# ============================================================================
# Dish Similarity Matching Module (also serves as Search from main menu)
# ============================================================================

def similarity_matching_menu(store):
    print()
    print_separator()
    print("  === Dish Similarity Matching ===")
    print()
    search_term = input("  Enter dish name or category to search (or 'n' for file-based matching): ").strip()

    if search_term and search_term.lower() != 'n':
        # Search mode - search by both name and category
        search_dish_direct(store, search_term)
        # Ask if user wants similarity matching
        find_similar = input("\n  Find similar dishes? (y/n): ").strip().lower()
        if find_similar == 'y':
            _run_file_based_matching(store)
    else:
        _run_file_based_matching(store)


def _run_file_based_matching(store):
    print()
    filepath = input("  Enter file path for approximate dishes CSV: ").strip()
    if not filepath:
        filepath = os.path.join(DATA_DIR, "approximate_dishes.csv")
    if not os.path.exists(filepath):
        print(f"  Error: File '{filepath}' not found.")
        return
    threshold_str = input("  Enter similarity threshold (0-100, default 80): ").strip()
    try:
        threshold = int(threshold_str) if threshold_str else 80
    except ValueError:
        threshold = 80

    approximate_names = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'name' in row:
                approximate_names.append(row['name'].strip())

    if not approximate_names:
        print("  No dish names found in the file.")
        return

    print(f"\n  Loaded {len(approximate_names)} approximate dish name(s).")
    print(f"  Similarity threshold: {threshold}%")

    try:
        from thefuzz import fuzz
        use_fuzz = True
    except ImportError:
        use_fuzz = False

    groups = {}
    for approx_name in approximate_names:
        best_match = None
        best_score = 0
        for dish in store.dishes.values():
            if use_fuzz:
                score = fuzz.ratio(approx_name.lower(), dish.name.lower())
            else:
                common = len(set(approx_name.lower()) & set(dish.name.lower()))
                total = len(set(approx_name.lower()) | set(dish.name.lower()))
                score = (common / total * 100) if total > 0 else 0
            if score > best_score:
                best_score = score
                best_match = dish
        if best_match and best_score >= threshold:
            group_key = best_match.name
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append((approx_name, best_match, best_score))

    print()
    print("  === Similarity Matching Results ===")
    if groups:
        headers = ["Group", "Similar Dish", "Matched Dish", "Score"]
        rows = []
        for group_key, matches in groups.items():
            for approx_name, dish, score in matches:
                rows.append([group_key, approx_name, dish.name, f"{score:.0f}%"])
                print(f"  '{approx_name}' matched with '{dish.name}' (score: {score:.0f}%) -> Group: {group_key}")

            all_dish_ids = [d.dish_id for _, d, _ in matches]
            for d in store.dishes.values():
                if d.name == group_key:
                    all_dish_ids.append(d.dish_id)

            group_orders = [o for o in store.orders if o.dish_id in all_dish_ids]
            if group_orders:
                total_qty = sum(o.quantity for o in group_orders)
                avg_price = sum(o.settlement_price for o in group_orders) / len(group_orders)
                if len(group_orders) > 1:
                    mean_qty = total_qty / len(group_orders)
                    variance = sum((o.quantity - mean_qty) ** 2 for o in group_orders) / len(group_orders)
                    volatility = (variance ** 0.5 / mean_qty * 100) if mean_qty > 0 else 0
                else:
                    volatility = 0
                print(f"    Group '{group_key}' Statistics:")
                print(f"      Cumulative Order Volume: {total_qty}")
                print(f"      Average Settlement Price: ${avg_price:.2f}")
                print(f"      Sales Volatility Coefficient: {volatility:.1f}%")

        print()
        print_table(headers, rows)
    else:
        print("  No similar dish groups found above the threshold.")


# ============================================================================
# Main Menu
# ============================================================================

def main_menu(store):
    while True:
        print()
        print_separator()
        print("  Main Menu: Please select a functional module")
        print("  1. Dish Data Management")
        print("  2. Ingredient and Cost Analysis")
        print("  3. Sales Data Analysis")
        print("  4. Dish Similarity Matching")
        print("  5. Exit")
        print_separator()
        choice = input("  Please select an option: ").strip()

        if choice == "1":
            dish_management_menu(store)
        elif choice == "2":
            ingredient_analysis_menu(store)
        elif choice == "3":
            sales_analysis_menu(store)
        elif choice == "4":
            similarity_matching_menu(store)
        elif choice == "5":
            print("\n  Thank you for using the system. Goodbye!")
            sys.exit(0)
        else:
            print("  Invalid input, please try again")


# ============================================================================
# Entry Point
# ============================================================================

def main():
    store = DataStore()
    try:
        main_menu(store)
    except KeyboardInterrupt:
        print("\n\n  Program interrupted. Goodbye!")
        sys.exit(0)
    except EOFError:
        print("\n  Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
