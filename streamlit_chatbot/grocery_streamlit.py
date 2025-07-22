import streamlit as st
import pandas as pd
from datetime import datetime

# Initialize session state
if 'grocery_items' not in st.session_state:
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

if 'shopping_cart' not in st.session_state:
    st.session_state.shopping_cart = {}

def main():
    st.title("🛒 Family Grocery List & Price Checker")
    st.write("Malaysian grocery prices in MYR")
    
    # Sidebar for cart
    with st.sidebar:
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
                    st.write(f"Qty: {qty} × RM{price:.2f}")
                with col2:
                    if st.button("❌", key=f"remove_{item}"):
                        del st.session_state.shopping_cart[item]
                        st.rerun()
                
                st.write(f"**RM{subtotal:.2f}**")
                st.divider()
            
            st.write(f"### Total: RM{total:.2f}")
            
            if st.button("🗑️ Clear Cart"):
                st.session_state.shopping_cart.clear()
                st.rerun()
                
            if st.button("📋 Export List"):
                export_shopping_list(total)
                
        else:
            st.write("Your cart is empty")
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["🛒 Shop", "💰 Price Manager", "📊 Analysis"])
    
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
                st.write(f"RM{price:.2f}")
            
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
    
    with tab3:
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
                st.metric("Total Cost", f"RM{total_cost:.2f}")
            
            # Price breakdown chart
            if len(cart_data) > 0:
                st.subheader("Spending Breakdown")
                chart_data = df.set_index('Item')['Subtotal (RM)']
                st.bar_chart(chart_data)
        else:
            st.info("Add items to your cart to see analysis")

def export_shopping_list(total):
    """Export shopping list to text format"""
    export_text = f"GROCERY SHOPPING LIST\n"
    export_text += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    export_text += "="*40 + "\n\n"
    
    for item, details in st.session_state.shopping_cart.items():
        qty = details['quantity']
        price = details['price']
        subtotal = qty * price
        export_text += f"□ {item}\n"
        export_text += f"  Qty: {qty} × RM{price:.2f} = RM{subtotal:.2f}\n\n"
    
    export_text += "="*40 + "\n"
    export_text += f"TOTAL: RM{total:.2f}\n"
    
    st.download_button(
        label="📄 Download Shopping List",
        data=export_text,
        file_name=f"grocery_list_{datetime.now().strftime('%Y%m%d')}.txt",
        mime="text/plain"
    )

if __name__ == "__main__":
    main()
