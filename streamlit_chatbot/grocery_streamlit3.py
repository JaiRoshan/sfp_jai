import streamlit as st
import pandas as pd
from datetime import datetime
import base64
import requests
import json

def get_exchange_rates():
    """Fetch real-time exchange rates from MYR to other currencies"""
    try:
        # Using exchangerate-api.com (free tier allows 1500 requests/month)
        url = "https://api.exchangerate-api.com/v4/latest/MYR"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data['rates']
        else:
            return None
    except:
        return None

def get_cached_exchange_rates():
    """Get exchange rates with caching to avoid too many API calls"""
    if 'exchange_rates' not in st.session_state or 'rates_timestamp' not in st.session_state:
        st.session_state.exchange_rates = get_exchange_rates()
        st.session_state.rates_timestamp = datetime.now()
        return st.session_state.exchange_rates
    
    # Refresh rates every 30 minutes
    time_diff = datetime.now() - st.session_state.rates_timestamp
    if time_diff.seconds > 1800:  # 30 minutes
        st.session_state.exchange_rates = get_exchange_rates()
        st.session_state.rates_timestamp = datetime.now()
    
    return st.session_state.exchange_rates

def convert_currency(amount_myr, target_currency, rates):
    """Convert MYR amount to target currency"""
    if rates and target_currency in rates:
        return amount_myr * rates[target_currency]
    return None

def format_currency(amount, currency_code):
    """Format currency with appropriate symbol"""
    currency_symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'SGD': 'S$',
        'THB': '฿',
        'IDR': 'Rp',
        'JPY': '¥',
        'CNY': '¥',
        'AUD': 'A$',
        'CAD': 'C$',
        'INR': '₹'
    }
    
    symbol = currency_symbols.get(currency_code, currency_code + ' ')
    
    if currency_code == 'JPY' or currency_code == 'IDR':
        return f"{symbol}{amount:.0f}"
    else:
        return f"{symbol}{amount:.2f}"

def load_default_items():
    """Load default grocery items"""
    st.session_state.grocery_items = {
        # Rice & Grains
        'Basmati Rice (5kg)': 25.90,
        'Jasmine Rice (10kg)': 42.00,
        'Brown Rice (2kg)': 18.50,
        'Instant Oats (1kg)': 12.80,
        'Bread (White)': 2.50,
        'Wholemeal Bread': 3.20,
        
        # Proteins
        'Chicken Breast (1kg)': 18.90,
        'Chicken Thigh (1kg)': 12.50,
        'Beef (1kg)': 32.00,
        'Fish - Mackerel (1kg)': 15.00,
        'Fish - Salmon (500g)': 28.00,
        'Eggs (30pcs)': 12.50,
        'Tofu (500g)': 3.50,
        
        # Dairy
        'Fresh Milk (1L)': 4.20,
        'UHT Milk (1L)': 3.80,
        'Yogurt (500g)': 8.90,
        'Cheese Slices (200g)': 7.50,
        'Butter (250g)': 6.80,
        
        # Vegetables
        'Potatoes (1kg)': 4.50,
        'Onions (1kg)': 5.20,
        'Carrots (1kg)': 6.80,
        'Cabbage (1pc)': 3.50,
        'Tomatoes (1kg)': 7.20,
        'Cucumbers (1kg)': 4.80,
        'Spinach (bunch)': 2.50,
        'Broccoli (500g)': 5.90,
        
        # Fruits
        'Bananas (1kg)': 4.20,
        'Apples (1kg)': 8.90,
        'Oranges (1kg)': 6.50,
        'Watermelon (1pc)': 8.00,
        'Papaya (1pc)': 5.50,
        'Mangoes (1kg)': 12.00,
        
        # Pantry Staples
        'Cooking Oil (2L)': 12.90,
        'Soy Sauce (500ml)': 4.50,
        'Salt (1kg)': 1.80,
        'Sugar (1kg)': 2.60,
        'Flour (1kg)': 3.20,
        'Garlic (500g)': 8.00,
        'Ginger (500g)': 6.50,
        
        # Beverages
        'Coffee (200g)': 15.80,
        'Tea Bags (25pcs)': 4.90,
        'Fruit Juice (1L)': 5.50,
        'Mineral Water (1.5L)': 1.20,
        
        # Household
        'Dishwashing Liquid': 4.80,
        'Laundry Detergent': 18.50,
        'Toilet Paper (12 rolls)': 15.90,
        'Shampoo (400ml)': 12.80,
    }

def save_purchase_to_history():
    """Save current cart to purchase history"""
    if st.session_state.shopping_cart:
        purchase = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'items': dict(st.session_state.shopping_cart),
            'total': sum(details['price'] * details['quantity'] for details in st.session_state.shopping_cart.values())
        }
        st.session_state.purchase_history.append(purchase)
        
        # Update category statistics
        update_category_stats()
        
        # Clear cart
        st.session_state.shopping_cart.clear()

def update_category_stats():
    """Update category statistics based on purchase history"""
    category_totals = {}
    
    for purchase in st.session_state.purchase_history:
        for item, details in purchase['items'].items():
            category = get_item_category(item)
            if category not in category_totals:
                category_totals[category] = 0
            category_totals[category] += details['price'] * details['quantity']
    
    st.session_state.category_stats = category_totals

def get_item_category(item_name):
    """Determine which category an item belongs to"""
    # Check if item has a stored category first
    if 'item_categories' in st.session_state and item_name in st.session_state.item_categories:
        return st.session_state.item_categories[item_name]
    
    # Otherwise, determine by keywords
    item_lower = item_name.lower()
    
    if any(grain in item_lower for grain in ['rice', 'bread', 'oats', 'flour']):
        return 'Rice & Grains'
    elif any(protein in item_lower for protein in ['chicken', 'beef', 'fish', 'eggs', 'tofu']):
        return 'Proteins'
    elif any(dairy in item_lower for dairy in ['milk', 'yogurt', 'cheese', 'butter']):
        return 'Dairy'
    elif any(veg in item_lower for veg in ['potatoes', 'onions', 'carrots', 'cabbage', 'tomatoes', 'cucumber', 'spinach', 'broccoli']):
        return 'Vegetables'
    elif any(fruit in item_lower for fruit in ['banana', 'apple', 'orange', 'watermelon', 'papaya', 'mango']):
        return 'Fruits'
    elif any(pantry in item_lower for pantry in ['oil', 'sauce', 'salt', 'sugar', 'garlic', 'ginger']):
        return 'Pantry'
    elif any(bev in item_lower for bev in ['coffee', 'tea', 'juice', 'water']):
        return 'Beverages'
    elif any(house in item_lower for house in ['dish', 'detergent', 'toilet', 'shampoo']):
        return 'Household'
    else:
        return 'Other'

def set_item_category(item_name, category):
    """Manually set an item's category"""
    if 'item_categories' not in st.session_state:
        st.session_state.item_categories = {}
    st.session_state.item_categories[item_name] = category

def remove_item_from_category(item_name):
    """Remove an item's category assignment"""
    if 'item_categories' in st.session_state and item_name in st.session_state.item_categories:
        del st.session_state.item_categories[item_name]

def get_category_items(category):
    """Get all items in a specific category"""
    category_items = []
    for item in st.session_state.grocery_items.keys():
        if get_item_category(item) == category:
            category_items.append(item)
    return sorted(category_items)

def move_item_to_category(item_name, new_category):
    """Move an item to a different category"""
    set_item_category(item_name, new_category)

def export_shopping_list(total):
    """Export shopping list to HTML format (can be saved as PDF)"""
    # Create HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Grocery Shopping List</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                line-height: 1.6;
            }}
            .header {{
                text-align: center;
                border-bottom: 2px solid #333;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }}
            .title {{
                font-size: 28px;
                font-weight: bold;
                color: #333;
                margin-bottom: 10px;
            }}
            .date {{
                font-size: 14px;
                color: #666;
            }}
            .item {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 10px 0;
                border-bottom: 1px solid #eee;
            }}
            .item-info {{
                flex-grow: 1;
            }}
            .item-name {{
                font-weight: bold;
                font-size: 16px;
                margin-bottom: 5px;
            }}
            .item-details {{
                font-size: 14px;
                color: #666;
            }}
            .checkbox {{
                font-size: 20px;
                margin-right: 15px;
            }}
            .subtotal {{
                font-weight: bold;
                font-size: 16px;
                min-width: 100px;
                text-align: right;
            }}
            .total-section {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 2px solid #333;
                text-align: right;
            }}
            .total {{
                font-size: 24px;
                font-weight: bold;
                color: #333;
            }}
            .footer {{
                text-align: center;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #eee;
                color: #666;
                font-style: italic;
            }}
            @media print {{
                body {{ margin: 0; }}
                .no-print {{ display: none; }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="title">🛒 GROCERY SHOPPING LIST</div>
            <div class="date">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
        </div>
        
        <div class="items-section">
    """
    
    # Add each item
    for item, details in st.session_state.shopping_cart.items():
        qty = details['quantity']
        price = details['price']
        subtotal = qty * price
        
        html_content += f"""
            <div class="item">
                <div class="checkbox">☐</div>
                <div class="item-info">
                    <div class="item-name">{item}</div>
                    <div class="item-details">Qty: {qty} × RM{price:.2f}</div>
                </div>
                <div class="subtotal">RM{subtotal:.2f}</div>
            </div>
        """
    
    # Add total and footer
    html_content += f"""
        </div>
        
        <div class="total-section">
            <div class="total">TOTAL: RM{total:.2f}</div>
        </div>
        
        <div class="footer">
            Happy Shopping! 🛒<br>
            <small>Tip: Use Ctrl+P (or Cmd+P on Mac) to print or save as PDF</small>
        </div>
    </body>
    </html>
    """
    
    # Create download button for HTML file
    st.download_button(
        label="📄 Download Shopping List (HTML)",
        data=html_content,
        file_name=f"grocery_list_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
        mime="text/html"
    )
    
    # Display the HTML content in an expandable section
    with st.expander("📋 Preview Shopping List"):
        st.components.v1.html(html_content, height=600, scrolling=True)
        st.info("💡 **Tip**: Download the HTML file and open it in your browser. Then use Ctrl+P (or Cmd+P on Mac) to save it as a PDF!")

# Initialize session state
if 'grocery_items' not in st.session_state:
    load_default_items()

if 'shopping_cart' not in st.session_state:
    st.session_state.shopping_cart = {}

if 'purchase_history' not in st.session_state:
    st.session_state.purchase_history = []

if 'category_stats' not in st.session_state:
    st.session_state.category_stats = {}

if 'item_categories' not in st.session_state:
    st.session_state.item_categories = {}

def main():
    st.title("🛒 Family Grocery List & Price Checker")
    st.write("Malaysian grocery prices in MYR with real-time currency conversion")
    
    # Currency conversion settings in sidebar
    with st.sidebar:
        st.header("💱 Currency Settings")
        
        # Get exchange rates
        rates = get_cached_exchange_rates()
        
        if rates:
            st.success("✅ Exchange rates updated")
            last_update = st.session_state.get('rates_timestamp', datetime.now())
            st.caption(f"Last updated: {last_update.strftime('%H:%M')}")
            
            # Currency selection
            popular_currencies = ['USD', 'EUR', 'GBP', 'SGD', 'THB', 'IDR', 'JPY', 'CNY', 'AUD', 'INR']
            available_currencies = [curr for curr in popular_currencies if curr in rates.keys()]
            
            selected_currency = st.selectbox(
                "Convert prices to:",
                ['MYR (Default)'] + available_currencies,
                help="Select a currency to see converted prices"
            )
            
            if selected_currency != 'MYR (Default)':
                st.info(f"Showing prices in MYR and {selected_currency}")
                # Show current exchange rate
                if selected_currency in rates:
                    rate = rates[selected_currency]
                    st.metric(
                        f"1 MYR = ",
                        f"{format_currency(rate, selected_currency)}"
                    )
        else:
            st.warning("⚠️ Unable to fetch exchange rates")
            st.caption("Showing MYR prices only")
            selected_currency = 'MYR (Default)'
        
        st.divider()
        
        st.header("🛍️ Shopping Cart")
        
        if st.session_state.shopping_cart:
            total = 0
            for item, details in st.session_state.shopping_cart.items():
                qty = details['quantity']
                price = details['price']
                subtotal = qty * price
                total += subtotal
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"{item}")
                    price_display = f"Qty: {qty} × RM{price:.2f}"
                    
                    # Add currency conversion if enabled
                    if selected_currency != 'MYR (Default)' and rates:
                        converted_price = convert_currency(price, selected_currency, rates)
                        if converted_price:
                            price_display += f" ({format_currency(converted_price, selected_currency)})"
                    
                    st.write(price_display)
                with col2:
                    if st.button("❌", key=f"remove_{item}"):
                        del st.session_state.shopping_cart[item]
                        st.rerun()
                
                subtotal_display = f"**RM{subtotal:.2f}**"
                if selected_currency != 'MYR (Default)' and rates:
                    converted_subtotal = convert_currency(subtotal, selected_currency, rates)
                    if converted_subtotal:
                        subtotal_display += f" **({format_currency(converted_subtotal, selected_currency)})**"
                
                st.write(subtotal_display)
                st.divider()
            
            total_display = f"### Total: RM{total:.2f}"
            if selected_currency != 'MYR (Default)' and rates:
                converted_total = convert_currency(total, selected_currency, rates)
                if converted_total:
                    total_display += f"\n### ({format_currency(converted_total, selected_currency)})"
            
            st.write(total_display)
            
            if st.button("🗑️ Clear Cart"):
                st.session_state.shopping_cart.clear()
                st.rerun()
            
            if st.button("✅ Complete Purchase"):
                save_purchase_to_history()
                st.success("🎉 Purchase completed and saved to history!")
                st.rerun()
                
            if st.button("📋 Export List"):
                export_shopping_list(total)
                
        else:
            st.write("Your cart is empty")
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["🛒 Shop", "📦 Quick Add", "💰 Price Manager", "🗑️ Remove Items", "📊 Analysis", "📈 History", "💱 Currency Info"])
    
    with tab1:
        st.header("Browse Items")
        
        # Category filter
        categories = {
            'All': list(st.session_state.grocery_items.keys()),
            'Rice & Grains': [k for k in st.session_state.grocery_items.keys() if any(grain in k.lower() for grain in ['rice', 'bread', 'oats'])],
            'Proteins': [k for k in st.session_state.grocery_items.keys() if any(protein in k.lower() for protein in ['chicken', 'beef', 'fish', 'eggs', 'tofu'])],
            'Dairy': [k for k in st.session_state.grocery_items.keys() if any(dairy in k.lower() for dairy in ['milk', 'yogurt', 'cheese', 'butter'])],
            'Vegetables': [k for k in st.session_state.grocery_items.keys() if any(veg in k.lower() for veg in ['potatoes', 'onions', 'carrots', 'cabbage', 'tomatoes', 'cucumber', 'spinach', 'broccoli'])],
            'Fruits': [k for k in st.session_state.grocery_items.keys() if any(fruit in k.lower() for fruit in ['banana', 'apple', 'orange', 'watermelon', 'papaya', 'mango'])],
            'Pantry': [k for k in st.session_state.grocery_items.keys() if any(pantry in k.lower() for pantry in ['oil', 'sauce', 'salt', 'sugar', 'flour', 'garlic', 'ginger'])],
            'Beverages': [k for k in st.session_state.grocery_items.keys() if any(bev in k.lower() for bev in ['coffee', 'tea', 'juice', 'water'])],
            'Household': [k for k in st.session_state.grocery_items.keys() if any(house in k.lower() for house in ['dish', 'detergent', 'toilet', 'shampoo'])]
        }
        
        selected_category = st.selectbox("Filter by category:", list(categories.keys()))
        
        # Search
        search_term = st.text_input("🔍 Search items:")
        
        # Filter items
        items_to_show = categories[selected_category]
        if search_term:
            items_to_show = [item for item in items_to_show if search_term.lower() in item.lower()]
        
        # Display items
        for item in sorted(items_to_show):
            price = st.session_state.grocery_items[item]
            
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{item}**")
                price_display = f"RM{price:.2f}"
                
                # Add currency conversion
                if selected_currency != 'MYR (Default)' and rates:
                    converted_price = convert_currency(price, selected_currency, rates)
                    if converted_price:
                        price_display += f" ({format_currency(converted_price, selected_currency)})"
                
                st.write(price_display)
            
            with col2:
                quantity = st.number_input("Qty", min_value=1, max_value=20, value=1, key=f"qty_{item}")
            
            with col3:
                if st.button("Add to Cart", key=f"add_{item}"):
                    if item in st.session_state.shopping_cart:
                        st.session_state.shopping_cart[item]['quantity'] += quantity
                    else:
                        st.session_state.shopping_cart[item] = {
                            'price': price,
                            'quantity': quantity
                        }
                    st.success(f"Added {quantity}x {item}")
                    st.rerun()
            
            st.divider()
    
    with tab2:
        st.header("📦 Quick Add by Category")
        st.write("Quickly add items by browsing categories or add new items to specific categories")
        
        # Category selection
        categories = ['Rice & Grains', 'Proteins', 'Dairy', 'Vegetables', 'Fruits', 'Pantry', 'Beverages', 'Household']
        
        selected_cat = st.selectbox("🏷️ Select Category:", categories)
        
        if selected_cat:
            # Add new item to category section
            st.subheader(f"➕ Add New Item to {selected_cat}")
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                new_item_name = st.text_input(f"New {selected_cat.lower()} item name:", key=f"new_item_{selected_cat}")
            
            with col2:
                new_item_price = st.number_input("Price (RM):", min_value=0.01, step=0.10, value=1.00, key=f"new_price_{selected_cat}")
            
            with col3:
                if st.button(f"Add to {selected_cat}", key=f"add_new_{selected_cat}"):
                    if new_item_name and new_item_name not in st.session_state.grocery_items:
                        # Add item with category assignment
                        item_name = new_item_name.strip()
                        st.session_state.grocery_items[item_name] = new_item_price
                        set_item_category(item_name, selected_cat)  # Explicitly assign to category
                        st.success(f"✅ Added '{item_name}' to {selected_cat} category at RM{new_item_price:.2f}")
                        st.rerun()
                    elif new_item_name in st.session_state.grocery_items:
                        st.error("❌ Item already exists in the database!")
                    else:
                        st.error("❌ Please enter an item name")
            
            st.divider()
            
            # Show existing items in category
            category_items = get_category_items(selected_cat)
            
            if category_items:
                st.subheader(f"🛒 Existing {selected_cat} Items ({len(category_items)} items)")
                
                # Batch add functionality
                st.write("**Quick Actions:**")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button(f"🛒 Add All {selected_cat} Items (Qty: 1)", key=f"add_all_{selected_cat}"):
                        added_count = 0
                        for item in category_items:
                            if item not in st.session_state.shopping_cart:
                                st.session_state.shopping_cart[item] = {
                                    'price': st.session_state.grocery_items[item],
                                    'quantity': 1
                                }
                                added_count += 1
                            else:
                                st.session_state.shopping_cart[item]['quantity'] += 1
                                added_count += 1
                        st.success(f"✅ Added {added_count} {selected_cat.lower()} items to cart!")
                        st.rerun()
                
                with col2:
                    common_qty = st.number_input("Quantity for batch add:", min_value=1, max_value=10, value=2, key=f"batch_qty_{selected_cat}")
                    if st.button(f"🛒 Add All {selected_cat} (Qty: {common_qty})", key=f"add_all_qty_{selected_cat}"):
                        added_count = 0
                        for item in category_items:
                            if item not in st.session_state.shopping_cart:
                                st.session_state.shopping_cart[item] = {
                                    'price': st.session_state.grocery_items[item],
                                    'quantity': common_qty
                                }
                                added_count += 1
                            else:
                                st.session_state.shopping_cart[item]['quantity'] += common_qty
                                added_count += 1
                        st.success(f"✅ Added {added_count} {selected_cat.lower()} items (qty: {common_qty}) to cart!")
                        st.rerun()
                
                st.divider()
                
                # Show items in a more compact grid format
                cols = st.columns(2)
                
                for i, item in enumerate(category_items):
                    price = st.session_state.grocery_items[item]
                    col = cols[i % 2]
                    
                    with col:
                        with st.container():
                            # Item name with edit and category management options
                            item_header_col, category_col, edit_col, remove_col = st.columns([2, 1, 0.5, 0.5])
                            
                            with item_header_col:
                                st.write(f"**{item}**")
                            
                            with category_col:
                                current_category = get_item_category(item)
                                new_category = st.selectbox(
                                    "Category", 
                                    categories, 
                                    index=categories.index(current_category) if current_category in categories else 0,
                                    key=f"cat_select_{item}",
                                    help="Change item category"
                                )
                                if new_category != current_category:
                                    move_item_to_category(item, new_category)
                                    st.success(f"Moved {item} to {new_category}")
                                    st.rerun()
                            
                            with edit_col:
                                if st.button("✏️", key=f"edit_{item}", help="Edit item"):
                                    st.session_state[f"editing_{item}"] = True
                            
                            with remove_col:
                                if st.button("🗑️", key=f"remove_from_cat_{item}", help="Remove from category"):
                                    # Remove from grocery items and category
                                    if item in st.session_state.shopping_cart:
                                        del st.session_state.shopping_cart[item]
                                    del st.session_state.grocery_items[item]
                                    remove_item_from_category(item)
                                    st.success(f"Removed {item} from database")
                                    st.rerun()
                            
                            # Check if item is being edited
                            if st.session_state.get(f"editing_{item}", False):
                                new_name = st.text_input("New name:", value=item, key=f"edit_name_{item}")
                                new_price_edit = st.number_input("New price:", value=price, min_value=0.01, step=0.10, key=f"edit_price_{item}")
                                
                                save_col, cancel_col = st.columns(2)
                                with save_col:
                                    if st.button("💾 Save", key=f"save_{item}"):
                                        if new_name != item and new_name not in st.session_state.grocery_items:
                                            # Update item name and price
                                            del st.session_state.grocery_items[item]
                                            st.session_state.grocery_items[new_name] = new_price_edit
                                            
                                            # Update category assignment
                                            if item in st.session_state.item_categories:
                                                st.session_state.item_categories[new_name] = st.session_state.item_categories[item]
                                                del st.session_state.item_categories[item]
                                            
                                            # Update in cart if present
                                            if item in st.session_state.shopping_cart:
                                                cart_data = st.session_state.shopping_cart[item]
                                                del st.session_state.shopping_cart[item]
                                                st.session_state.shopping_cart[new_name] = cart_data
                                                st.session_state.shopping_cart[new_name]['price'] = new_price_edit
                                        else:
                                            # Just update price
                                            st.session_state.grocery_items[item] = new_price_edit
                                            if item in st.session_state.shopping_cart:
                                                st.session_state.shopping_cart[item]['price'] = new_price_edit
                                        
                                        st.session_state[f"editing_{item}"] = False
                                        st.success("✅ Item updated!")
                                        st.rerun()
                                
                                with cancel_col:
                                    if st.button("❌ Cancel", key=f"cancel_{item}"):
                                        st.session_state[f"editing_{item}"] = False
                                        st.rerun()
                            else:
                                # Normal display
                                price_display = f"RM{price:.2f}"
                                if selected_currency != 'MYR (Default)' and rates:
                                    converted_price = convert_currency(price, selected_currency, rates)
                                    if converted_price:
                                        price_display += f" ({format_currency(converted_price, selected_currency)})"
                                st.write(price_display)
                                
                                # Show if item is in cart
                                if item in st.session_state.shopping_cart:
                                    cart_qty = st.session_state.shopping_cart[item]['quantity']
                                    st.info(f"🛒 In cart (Qty: {cart_qty})")
                                
                                col1, col2 = st.columns([1, 1])
                                with col1:
                                    qty = st.number_input("Qty", min_value=1, max_value=20, value=1, key=f"cat_qty_{item}")
                                with col2:
                                    if st.button("Add", key=f"cat_add_{item}"):
                                        if item in st.session_state.shopping_cart:
                                            st.session_state.shopping_cart[item]['quantity'] += qty
                                        else:
                                            st.session_state.shopping_cart[item] = {
                                                'price': price,
                                                'quantity': qty
                                            }
                                        st.success(f"Added {qty}x {item}")
                                        st.rerun()
                            st.divider()
            else:
                st.info(f"No items found in {selected_cat} category. Add the first item above!")
                
        # Category management section
        st.subheader("🏷️ Advanced Category Management")
        
        with st.expander("🔄 Move Items Between Categories"):
            st.write("**Bulk Move Items:**")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                source_category = st.selectbox("From Category:", categories, key="source_cat")
                
            with col2:
                target_category = st.selectbox("To Category:", categories, key="target_cat")
            
            with col3:
                st.write(" ")  # Spacing
                if st.button("🔄 Move All Items"):
                    if source_category != target_category:
                        source_items = get_category_items(source_category)
                        if source_items:
                            for item in source_items:
                                move_item_to_category(item, target_category)
                            st.success(f"✅ Moved {len(source_items)} items from {source_category} to {target_category}")
                            st.rerun()
                        else:
                            st.info(f"No items in {source_category} to move")
                    else:
                        st.warning("Source and target categories must be different")
            
            # Individual item moving
            st.write("**Move Individual Items:**")
            all_items = list(st.session_state.grocery_items.keys())
            
            if all_items:
                selected_item = st.selectbox("Select item to move:", all_items, key="move_item")
                current_cat = get_item_category(selected_item)
                
                col1, col2, col3 = st.columns([1, 1, 1])
                
                with col1:
                    st.info(f"Current: {current_cat}")
                
                with col2:
                    new_cat = st.selectbox("Move to:", categories, key="new_cat_individual")
                
                with col3:
                    st.write(" ")  # Spacing
                    if st.button("🔄 Move Item"):
                        if new_cat != current_cat:
                            move_item_to_category(selected_item, new_cat)
                            st.success(f"✅ Moved '{selected_item}' to {new_cat}")
                            st.rerun()
                        else:
                            st.info("Item is already in that category")
        
        with st.expander("🗑️ Remove Items by Category"):
            st.warning("⚠️ This will permanently delete items from the database!")
            
            remove_category = st.selectbox("Select category to clear:", categories, key="remove_cat")
            items_in_remove_cat = get_category_items(remove_category)
            
            if items_in_remove_cat:
                st.write(f"**Items to be removed from {remove_category}:**")
                for item in items_in_remove_cat:
                    price = st.session_state.grocery_items[item]
                    st.write(f"• {item} - RM{price:.2f}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button(f"🗑️ Remove All {len(items_in_remove_cat)} Items", type="secondary"):
                        # Remove all items from category
                        for item in items_in_remove_cat:
                            if item in st.session_state.shopping_cart:
                                del st.session_state.shopping_cart[item]
                            del st.session_state.grocery_items[item]
                            remove_item_from_category(item)
                        st.success(f"✅ Removed all {len(items_in_remove_cat)} items from {remove_category}")
                        st.rerun()
                
                with col2:
                    st.write("This action cannot be undone!")
            else:
                st.info(f"No items in {remove_category} category to remove")
        
        with st.expander("📊 Category Overview"):
            category_overview = {}
            for category in categories:
                items_in_cat = get_category_items(category)
                if items_in_cat:
                    total_value = sum(st.session_state.grocery_items[item] for item in items_in_cat)
                    avg_price = total_value / len(items_in_cat)
                    category_overview[category] = {
                        'Items': len(items_in_cat),
                        'Total Value': f"RM{total_value:.2f}",
                        'Avg Price': f"RM{avg_price:.2f}"
                    }
                else:
                    category_overview[category] = {
                        'Items': 0,
                        'Total Value': "RM0.00",
                        'Avg Price': "RM0.00"
                    }
            
            overview_df = pd.DataFrame.from_dict(category_overview, orient='index')
            st.dataframe(overview_df, use_container_width=True)
            
            # Most expensive items per category
            st.write("**Most Expensive Item per Category:**")
            for category in categories:
                items_in_cat = get_category_items(category)
                if items_in_cat:
                    most_expensive = max(items_in_cat, key=lambda x: st.session_state.grocery_items[x])
                    price = st.session_state.grocery_items[most_expensive]
                    st.write(f"• **{category}**: {most_expensive} (RM{price:.2f})")

    with tab3:
        st.header("Manage Prices")
        st.write("Update item prices or add new items")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Update Existing Item")
            item_to_update = st.selectbox("Select item:", list(st.session_state.grocery_items.keys()))
            current_price = st.session_state.grocery_items[item_to_update]
            new_price = st.number_input("New price (RM):", value=current_price, min_value=0.01, step=0.10)
            
            if st.button("Update Price"):
                st.session_state.grocery_items[item_to_update] = new_price
                st.success(f"Updated {item_to_update} to RM{new_price:.2f}")
        
        with col2:
            st.subheader("Add New Item")
            new_item_name = st.text_input("Item name:")
            new_item_price = st.number_input("Price (RM):", min_value=0.01, step=0.10, value=1.00)
            
            if st.button("Add Item"):
                if new_item_name and new_item_name not in st.session_state.grocery_items:
                    st.session_state.grocery_items[new_item_name] = new_item_price
                    st.success(f"Added {new_item_name} at RM{new_item_price:.2f}")
                elif new_item_name in st.session_state.grocery_items:
                    st.error("Item already exists!")
                else:
                    st.error("Please enter an item name")
    
    with tab4:
        st.header("Remove Items from Master List")
        st.write("Permanently remove items from the grocery database")
        
        if len(st.session_state.grocery_items) > 0:
            # Search for items to remove
            st.subheader("Search & Remove Items")
            remove_search = st.text_input("🔍 Search items to remove:", key="remove_search")
            
            # Filter items based on search
            items_to_show = list(st.session_state.grocery_items.keys())
            if remove_search:
                items_to_show = [item for item in items_to_show if remove_search.lower() in item.lower()]
            
            # Show items with remove buttons
            if items_to_show:
                st.write(f"Found {len(items_to_show)} item(s)")
                
                # Create columns for better layout
                for i, item in enumerate(sorted(items_to_show)):
                    price = st.session_state.grocery_items[item]
                    
                    col1, col2, col3 = st.columns([4, 1, 1])
                    
                    with col1:
                        st.write(f"**{item}**")
                        price_display = f"RM{price:.2f}"
                        
                        # Add currency conversion
                        if selected_currency != 'MYR (Default)' and rates:
                            converted_price = convert_currency(price, selected_currency, rates)
                            if converted_price:
                                price_display += f" ({format_currency(converted_price, selected_currency)})"
                        
                        st.write(price_display)
                    
                    with col2:
                        # Show if item is in cart
                        if item in st.session_state.shopping_cart:
                            st.write("🛒 In cart")
                        else:
                            st.write("")
                    
                    with col3:
                        if st.button("🗑️ Remove", key=f"remove_item_{i}_{item}"):
                            # Remove from shopping cart if present
                            if item in st.session_state.shopping_cart:
                                del st.session_state.shopping_cart[item]
                            # Remove from master list
                            del st.session_state.grocery_items[item]
                            st.success(f"Removed {item} from database")
                            st.rerun()
                    
                    st.divider()
            else:
                if remove_search:
                    st.info("No items found matching your search")
                else:
                    st.info("Enter a search term to find items to remove")
            
            # Bulk remove section
            st.subheader("Bulk Remove by Category")
            
            # Category selection for bulk removal
            categories = {
                'Rice & Grains': [k for k in st.session_state.grocery_items.keys() if any(grain in k.lower() for grain in ['rice', 'bread', 'oats'])],
                'Proteins': [k for k in st.session_state.grocery_items.keys() if any(protein in k.lower() for protein in ['chicken', 'beef', 'fish', 'eggs', 'tofu'])],
                'Dairy': [k for k in st.session_state.grocery_items.keys() if any(dairy in k.lower() for dairy in ['milk', 'yogurt', 'cheese', 'butter'])],
                'Vegetables': [k for k in st.session_state.grocery_items.keys() if any(veg in k.lower() for veg in ['potatoes', 'onions', 'carrots', 'cabbage', 'tomatoes', 'cucumber', 'spinach', 'broccoli'])],
                'Fruits': [k for k in st.session_state.grocery_items.keys() if any(fruit in k.lower() for fruit in ['banana', 'apple', 'orange', 'watermelon', 'papaya', 'mango'])],
                'Pantry': [k for k in st.session_state.grocery_items.keys() if any(pantry in k.lower() for pantry in ['oil', 'sauce', 'salt', 'sugar', 'flour', 'garlic', 'ginger'])],
                'Beverages': [k for k in st.session_state.grocery_items.keys() if any(bev in k.lower() for bev in ['coffee', 'tea', 'juice', 'water'])],
                'Household': [k for k in st.session_state.grocery_items.keys() if any(house in k.lower() for house in ['dish', 'detergent', 'toilet', 'shampoo'])]
            }
            
            category_to_remove = st.selectbox("Select category to remove:", [''] + list(categories.keys()), key="bulk_remove")
            
            if category_to_remove and category_to_remove in categories:
                items_in_category = categories[category_to_remove]
                if items_in_category:
                    st.write(f"This will remove {len(items_in_category)} items from the {category_to_remove} category:")
                    
                    # Show items that will be removed
                    with st.expander(f"View {len(items_in_category)} items to be removed"):
                        for item in items_in_category:
                            price_display = f"• {item} - RM{st.session_state.grocery_items[item]:.2f}"
                            
                            # Add currency conversion
                            if selected_currency != 'MYR (Default)' and rates:
                                converted_price = convert_currency(st.session_state.grocery_items[item], selected_currency, rates)
                                if converted_price:
                                    price_display += f" ({format_currency(converted_price, selected_currency)})"
                            
                            st.write(price_display)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"⚠️ Remove All {category_to_remove} Items", type="secondary"):
                            # Remove items from cart first
                            for item in items_in_category:
                                if item in st.session_state.shopping_cart:
                                    del st.session_state.shopping_cart[item]
                                del st.session_state.grocery_items[item]
                            st.success(f"Removed all {len(items_in_category)} items from {category_to_remove}")
                            st.rerun()
                else:
                    st.info(f"No items found in {category_to_remove} category")
            
            # Reset database option
            st.subheader("⚠️ Danger Zone")
            with st.expander("Reset Entire Database"):
                st.warning("This will remove ALL items from the grocery database and clear your shopping cart!")
                if st.button("🔄 Reset All Data", type="secondary"):
                    if st.button("✅ Confirm Reset", type="primary"):
                        st.session_state.grocery_items.clear()
                        st.session_state.shopping_cart.clear()
                        # Reload default items
                        load_default_items()
                        st.success("Database reset to default items")
                        st.rerun()
        else:
            st.info("No items in database")
            if st.button("🔄 Load Default Items"):
                load_default_items()
                st.rerun()

    with tab5:
        st.header("Price Analysis")
        
        if st.session_state.shopping_cart:
            # Create dataframe for analysis
            cart_data = []
            for item, details in st.session_state.shopping_cart.items():
                cart_data.append({
                    'Item': item,
                    'Price (RM)': details['price'],
                    'Quantity': details['quantity'],
                    'Subtotal (RM)': details['price'] * details['quantity']
                })
            
            df = pd.DataFrame(cart_data)
            st.dataframe(df, use_container_width=True)
            
            # Summary statistics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Items", len(st.session_state.shopping_cart))
            
            with col2:
                total_qty = sum(details['quantity'] for details in st.session_state.shopping_cart.values())
                st.metric("Total Quantity", total_qty)
            
            with col3:
                total_cost = sum(details['price'] * details['quantity'] for details in st.session_state.shopping_cart.values())
                total_display = f"RM{total_cost:.2f}"
                
                # Add currency conversion
                if selected_currency != 'MYR (Default)' and rates:
                    converted_total = convert_currency(total_cost, selected_currency, rates)
                    if converted_total:
                        total_display += f"\n({format_currency(converted_total, selected_currency)})"
                
                st.metric("Total Cost", total_display)
            
            # Price breakdown chart
            if len(cart_data) > 0:
                st.subheader("Spending Breakdown")
                chart_data = df.set_index('Item')['Subtotal (RM)']
                st.bar_chart(chart_data)
        else:
            st.info("Add items to your cart to see analysis")

    with tab6:
        st.header("📈 Purchase History & Trends")
        
        if st.session_state.purchase_history:
            st.success(f"📊 Total purchases recorded: {len(st.session_state.purchase_history)}")
            
            # Summary statistics
            total_spent = sum(purchase['total'] for purchase in st.session_state.purchase_history)
            avg_purchase = total_spent / len(st.session_state.purchase_history)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Spent", f"RM{total_spent:.2f}")
            with col2:
                st.metric("Average Purchase", f"RM{avg_purchase:.2f}")
            with col3:
                st.metric("Total Purchases", len(st.session_state.purchase_history))
            
            # Category spending analysis
            if st.session_state.category_stats:
                st.subheader("🥧 Spending by Category")
                
                # Prepare data for pie chart
                categories = list(st.session_state.category_stats.keys())
                amounts = list(st.session_state.category_stats.values())
                
                # Calculate percentages
                total_category_spending = sum(amounts)
                percentages = [(amount/total_category_spending)*100 for amount in amounts]
                
                # Create DataFrame for charts
                category_df = pd.DataFrame({
                    'Category': categories,
                    'Amount (RM)': amounts,
                    'Percentage': percentages
                })
                category_df = category_df.sort_values('Amount (RM)', ascending=False)
                
                # Display pie chart using bar chart (Streamlit doesn't have native pie charts)
                st.subheader("💰 Category Spending Distribution")
                chart_data = category_df.set_index('Category')['Amount (RM)']
                st.bar_chart(chart_data)
                
                # Percentage breakdown table
                st.subheader("📊 Detailed Breakdown")
                display_df = category_df.copy()
                display_df['Percentage'] = display_df['Percentage'].apply(lambda x: f"{x:.1f}%")
                display_df['Amount (RM)'] = display_df['Amount (RM)'].apply(lambda x: f"RM{x:.2f}")
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                # Top spending category
                top_category = category_df.iloc[0]
                st.info(f"🏆 **Top spending category**: {top_category['Category']} ({top_category['Percentage']:.1f}% of total spending)")
            
            # Recent purchases
            st.subheader("🕒 Recent Purchases")
            recent_purchases = sorted(st.session_state.purchase_history, key=lambda x: x['date'], reverse=True)[:5]
            
            for i, purchase in enumerate(recent_purchases):
                with st.expander(f"Purchase #{len(st.session_state.purchase_history)-i} - {purchase['date']} (RM{purchase['total']:.2f})"):
                    for item, details in purchase['items'].items():
                        st.write(f"• {item} - Qty: {details['quantity']} × RM{details['price']:.2f} = RM{details['price'] * details['quantity']:.2f}")
            
            # Purchase frequency analysis
            st.subheader("📅 Purchase Frequency")
            
            # Group purchases by date
            purchase_dates = [datetime.strptime(p['date'].split(' ')[0], '%Y-%m-%d').date() for p in st.session_state.purchase_history]
            date_counts = pd.Series(purchase_dates).value_counts().sort_index()
            
            if len(date_counts) > 1:
                st.line_chart(date_counts)
                
                # Calculate average days between purchases
                if len(purchase_dates) > 1:
                    date_diffs = [(purchase_dates[i] - purchase_dates[i+1]).days for i in range(len(purchase_dates)-1)]
                    avg_days = sum(date_diffs) / len(date_diffs)
                    st.info(f"📈 **Average days between purchases**: {avg_days:.1f} days")
            
            # Most purchased items
            st.subheader("🥇 Most Purchased Items")
            item_frequency = {}
            item_quantities = {}
            
            for purchase in st.session_state.purchase_history:
                for item, details in purchase['items'].items():
                    if item not in item_frequency:
                        item_frequency[item] = 0
                        item_quantities[item] = 0
                    item_frequency[item] += 1
                    item_quantities[item] += details['quantity']
            
            # Top 10 most frequent items
            top_items = sorted(item_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
            
            if top_items:
                items_df = pd.DataFrame([
                    {
                        'Item': item,
                        'Times Purchased': freq,
                        'Total Quantity': item_quantities[item],
                        'Avg Qty per Purchase': f"{item_quantities[item]/freq:.1f}"
                    }
                    for item, freq in top_items
                ])
                st.dataframe(items_df, use_container_width=True, hide_index=True)
            
            # Clear history option
            st.subheader("⚠️ Manage History")
            with st.expander("Clear Purchase History"):
                st.warning("This will permanently delete all your purchase history data!")
                if st.button("🗑️ Clear All History", type="secondary"):
                    if st.button("✅ Confirm Clear History", type="primary"):
                        st.session_state.purchase_history.clear()
                        st.session_state.category_stats.clear()
                        st.success("✅ Purchase history cleared!")
                        st.rerun()
        
        else:
            st.info("📝 No purchase history yet. Complete a purchase to start tracking your grocery trends!")
            st.write("**To start tracking:**")
            st.write("1. Add items to your cart")
            st.write("2. Click '✅ Complete Purchase' in the sidebar")
            st.write("3. Your purchase will be saved to history")
            st.write("4. Come back here to see your spending trends!")

    with tab7:
        st.header("💱 Currency Conversion Information")
        
        rates = get_cached_exchange_rates()
        
        if rates:
            st.success("✅ Real-time exchange rates loaded successfully!")
            
            # Display last update time
            if 'rates_timestamp' in st.session_state:
                last_update = st.session_state.rates_timestamp
                st.info(f"📅 Last updated: {last_update.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Popular currencies section
            st.subheader("🌍 Popular Currencies")
            popular_currencies = ['USD', 'EUR', 'GBP', 'SGD', 'THB', 'IDR', 'JPY', 'CNY', 'AUD', 'INR']
            
            # Create currency conversion table
            currency_data = []
            for currency in popular_currencies:
                if currency in rates:
                    rate = rates[currency]
                    currency_names = {
                        'USD': 'US Dollar',
                        'EUR': 'Euro',
                        'GBP': 'British Pound',
                        'SGD': 'Singapore Dollar',
                        'THB': 'Thai Baht',
                        'IDR': 'Indonesian Rupiah',
                        'JPY': 'Japanese Yen',
                        'CNY': 'Chinese Yuan',
                        'AUD': 'Australian Dollar',
                        'INR': 'Indian Rupee'
                    }
                    
                    currency_data.append({
                        'Currency': f"{currency} ({currency_names.get(currency, currency)})",
                        '1 MYR =': format_currency(rate, currency),
                        '10 MYR =': format_currency(rate * 10, currency),
                        '100 MYR =': format_currency(rate * 100, currency)
                    })
            
            if currency_data:
                df_currencies = pd.DataFrame(currency_data)
                st.dataframe(df_currencies, use_container_width=True, hide_index=True)
            
            # Currency converter
            st.subheader("🔄 Quick Currency Converter")
            
            col1, col2 = st.columns(2)
            with col1:
                amount_myr = st.number_input("Amount in MYR:", min_value=0.01, value=10.00, step=0.50)
            
            with col2:
                available_currencies = [curr for curr in popular_currencies if curr in rates.keys()]
                target_currency = st.selectbox("Convert to:", available_currencies)
            
            if target_currency and target_currency in rates:
                converted_amount = convert_currency(amount_myr, target_currency, rates)
                if converted_amount:
                    st.success(f"RM{amount_myr:.2f} = {format_currency(converted_amount, target_currency)}")
            
            # Refresh rates button
            st.subheader("⚡ Manual Refresh")
            if st.button("🔄 Refresh Exchange Rates"):
                with st.spinner("Fetching latest exchange rates..."):
                    new_rates = get_exchange_rates()
                    if new_rates:
                        st.session_state.exchange_rates = new_rates
                        st.session_state.rates_timestamp = datetime.now()
                        st.success("✅ Exchange rates updated successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to fetch exchange rates. Please try again later.")
            
            # Rate source info
            with st.expander("ℹ️ About Exchange Rates"):
                st.write("""
                **Data Source**: ExchangeRate-API.com
                
                **Update Frequency**: 
                - Automatic refresh every 30 minutes
                - Manual refresh available anytime
                
                **Supported Currencies**: USD, EUR, GBP, SGD, THB, IDR, JPY, CNY, AUD, INR, and more
                
                **Note**: Exchange rates are for reference only. Actual rates may vary depending on your bank or money exchanger.
                """)
        
        else:
            st.error("❌ Unable to load exchange rates")
            st.write("**Possible reasons:**")
            st.write("- No internet connection")
            st.write("- Exchange rate service is temporarily unavailable")
            st.write("- API rate limit reached")
            
            if st.button("🔄 Retry Loading Exchange Rates"):
                with st.spinner("Attempting to fetch exchange rates..."):
                    new_rates = get_exchange_rates()
                    if new_rates:
                        st.session_state.exchange_rates = new_rates
                        st.session_state.rates_timestamp = datetime.now()
                        st.success("✅ Exchange rates loaded successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Still unable to fetch exchange rates.")

if __name__ == "__main__":
    main()