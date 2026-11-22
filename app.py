
# import streamlit as st
# from db import create_tables

# # Initialize database
# create_tables()

# # Page configuration
# st.set_page_config(
#     page_title="SmartDukaan",
#     page_icon="🛒",
#     layout="wide"
# )

# # Application title
# st.title("🛒 SmartDukaan")
# st.subheader("Digital Business Management System")

# st.divider()

# # Dashboard metrics
# col1, col2, col3, col4 = st.columns(4)

# col1.metric("Total Products", "0")
# col2.metric("Total Sales", "₹0")
# col3.metric("Total Expenses", "₹0")
# col4.metric("Low Stock", "0")

# st.divider()

# st.success("Welcome to SmartDukaan!")

# st.write(
#     "Manage your shop products, sales, "
#     "expenses and customer credit in one place."
# )



import streamlit as st
import pandas as pd
from db import set_stock
from db import record_sale,get_sales
from datetime import date


from db import (
    create_tables,
    get_connection,
    add_product,
    get_products,
    update_product,
    update_stock,
    delete_product,
    add_expense,
    get_expenses,
    update_expense,
    delete_expense,
    add_customer,
    get_customers,
    update_customer,
    delete_customer,
    add_customer_credit,
    get_customer_credits,
    update_credit_status,
    delete_customer_credit
)   

# Initialize database
create_tables()

# Page configuration
st.set_page_config(
    page_title="SmartDukaan",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 SmartDukaan")
st.caption("Digital Business Management System")

# Navigation tabs
dashboard_tab, product_tab, sales_tab, expense_tab, customer_tab, credit_tab = st.tabs([
    "Dashboard",
    "Product & Stock Management",
    "Sales",
    "Expense Management",
    "Customer Management",
    "Customer Credit"
     
])
 

# ---------------- DASHBOARD ----------------

with dashboard_tab:

    st.header("Business Dashboard")

    products = get_products()

    conn = get_connection()

    total_sales = conn.execute(
        "SELECT COALESCE(SUM(total_amount), 0) FROM sales"
    ).fetchone()[0]

    total_expenses = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM expenses"
    ).fetchone()[0]

    conn.close()

    total_products = len(products)

    low_stock = 0

    if not products.empty:
        low_stock = len(
            products[
                products["quantity"] <=
                products["low_stock_limit"]
            ]
        )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Products", total_products)
    c2.metric("Total Sales", f"₹{total_sales:.2f}")
    c3.metric("Total Expenses", f"₹{total_expenses:.2f}")
    c4.metric("Low Stock", low_stock)

    st.subheader("Recent Products")

    if products.empty:
        st.info("No products added yet.")
    else:
        st.dataframe(products, use_container_width=True)


# ---------------- PRODUCT MANAGEMENT ----------------

with product_tab:

    st.header("Product & Stock Management")

    add_tab, view_tab, edit_tab, stock_tab = st.tabs([
        "Add Product",
        "View Products",
        "Edit Product",
        "Update Stock"
    ])


with sales_tab:

    st.subheader("Record New Sale")

    products = get_products()

    if products.empty:
        st.warning("Please add products before recording a sale.")

    else:
        product_options = {
            f"{row['name']} (Stock: {row['quantity']})": row['product_id']
            for _, row in products.iterrows()
        }

        selected_product = st.selectbox(
            "Select Product",
            list(product_options.keys())
        )

        product_id = product_options[selected_product]

        selected_row = products[
            products["product_id"] == product_id
        ].iloc[0]

        quantity = st.number_input(
            "Quantity Sold",
            min_value=1,
            max_value=max(1, int(selected_row["quantity"])),
            step=1
        )

        total = selected_row["price"] * quantity

        st.write(f"Price: ₹{selected_row['price']}")
        st.write(f"Total Amount: ₹{total:.2f}")

        if st.button("Complete Sale"):

            if selected_row["quantity"] < quantity:
                st.error("Insufficient stock!")

            elif record_sale(product_id, quantity):
                st.success("Sale recorded successfully!")
                st.rerun()

            else:
                st.error("Unable to record sale.")


    st.divider()

    st.subheader("Sales History")

    sales = get_sales()

    if sales.empty:
        st.info("No sales recorded yet.")

    else:
        st.dataframe(sales, use_container_width=True)


# ---------------- EXPENSE MANAGEMENT ----------------

with expense_tab:

    st.header("Expense Management")

    add_exp_tab, view_exp_tab, edit_exp_tab = st.tabs([
        "Add Expense",
        "View Expenses",
        "Edit / Delete Expense"
    ])

    categories = [
        "Rent",
        "Electricity",
        "Transportation",
        "Salary",
        "Maintenance",
        "Inventory",
        "Other"
    ]

    # ADD EXPENSE
    with add_exp_tab:

        st.subheader("Record New Expense")

        with st.form("add_expense_form"):

            category = st.selectbox(
                "Expense Category",
                categories
            )

            description = st.text_input(
                "Expense Description"
            )

            amount = st.number_input(
                "Expense Amount (₹)",
                min_value=0.01,
                value=100.0
            )

            expense_date = st.date_input(
                "Expense Date",
                value=date.today()
            )

            submitted = st.form_submit_button(
                "Add Expense"
            )

            if submitted:

                if not description.strip():
                    st.error("Please enter expense description.")

                else:

                    success = add_expense(
                        category,
                        description,
                        amount,
                        expense_date.isoformat()
                    )

                    if success:
                        st.success("Expense recorded successfully!")
                        st.rerun()

                    else:
                        st.error("Unable to record expense.")


    
# ---------------- CUSTOMER MANAGEMENT ----------------

with customer_tab:

    st.header("Customer Management")

    add_customer_tab, view_customer_tab, edit_customer_tab = st.tabs([
        "Add Customer",
        "View Customers",
        "Edit / Delete Customer"
    ])

    # ADD CUSTOMER
    with add_customer_tab:

        with st.form("add_customer_form"):

            name = st.text_input("Customer Name")
            phone = st.text_input("Phone Number")

            submitted = st.form_submit_button("Add Customer")

            if submitted:

                if not name.strip():
                    st.error("Enter customer name.")

                else:
                    if add_customer(name, phone):
                        st.success("Customer added successfully!")
                        st.rerun()
                    else:
                        st.error("Unable to add customer.")

    # VIEW CUSTOMERS
    with view_customer_tab:

        customers = get_customers()

        st.subheader("Customer List")

        if customers.empty:
            st.info("No customers available.")

        else:
            st.dataframe(
                customers,
                use_container_width=True,
                hide_index=True
            )

    # EDIT / DELETE CUSTOMER
    with edit_customer_tab:

        customers = get_customers()

        if customers.empty:

            st.info("No customers available.")

        else:

            options = {
                f"{row['customer_id']} - {row['name']}":
                row['customer_id']
                for _, row in customers.iterrows()
            }

            selected = st.selectbox(
                "Select Customer",
                list(options.keys())
            )

            customer_id = options[selected]

            customer = customers[
                customers["customer_id"] == customer_id
            ].iloc[0]

            with st.form("edit_customer_form"):

                new_name = st.text_input(
                    "Customer Name",
                    value=customer["name"]
                )

                new_phone = st.text_input(
                    "Phone Number",
                    value=customer["phone"] or ""
                )

                save = st.form_submit_button("Update Customer")

                if save:

                    if update_customer(
                        customer_id,
                        new_name,
                        new_phone
                    ):
                        st.success("Customer updated!")
                        st.rerun()
                    else:
                        st.error("Unable to update customer.")

            if st.button("Delete Selected Customer"):

                if delete_customer(customer_id):
                    st.success("Customer deleted!")
                    st.rerun()

                else:
                    st.error(
                        "Cannot delete customer because credit records exist."
                    )


    # VIEW EXPENSES
    with view_exp_tab:

        st.subheader("Expense History")

        expenses = get_expenses()

        if expenses.empty:

            st.info("No expenses recorded yet.")

        else:

            st.dataframe(
                expenses,
                use_container_width=True,
                hide_index=True
            )

            total = expenses["amount"].sum()

            st.metric(
                "Total Expenses",
                f"₹{total:.2f}"
            )

            st.subheader("Category-wise Expenses")

            category_summary = (
                expenses.groupby("category")["amount"]
                .sum()
                .reset_index()
            )

            st.bar_chart(
                category_summary.set_index("category")
            )

    # EDIT / DELETE EXPENSE
    with edit_exp_tab:

        st.subheader("Manage Existing Expenses")

        expenses = get_expenses()

        if expenses.empty:

            st.info("No expenses available.")

        else:

            expense_options = {
                f"{row['expense_id']} - {row['category']} - ₹{row['amount']}":
                row["expense_id"]
                for _, row in expenses.iterrows()
            }

            selected = st.selectbox(
                "Select Expense",
                list(expense_options.keys())
            )

            expense_id = expense_options[selected]

            expense = expenses[
                expenses["expense_id"] == expense_id
            ].iloc[0]

            with st.form("edit_expense_form"):

                new_category = st.selectbox(
                    "Category",
                    categories,
                    index=(
                        categories.index(expense["category"])
                        if expense["category"] in categories
                        else categories.index("Other")
                    )
                )

                new_description = st.text_input(
                    "Description",
                    value=expense["description"]
                )

                new_amount = st.number_input(
                    "Amount (₹)",
                    min_value=0.01,
                    value=float(expense["amount"])
                )

                new_date = st.date_input(
                    "Expense Date",
                    value=pd.to_datetime(
                        expense["expense_date"]
                    ).date()
                )

                save = st.form_submit_button(
                    "Update Expense"
                )

                if save:

                    if not new_description.strip():

                        st.error("Description cannot be empty.")

                    else:

                        success = update_expense(
                            expense_id,
                            new_category,
                            new_description,
                            new_amount,
                            new_date.isoformat()
                        )

                        if success:
                            st.success("Expense updated successfully!")
                            st.rerun()

                        else:
                            st.error("Unable to update expense.")

            st.divider()

            if st.button("Delete Selected Expense"):

                if delete_expense(expense_id):
                    st.success("Expense deleted successfully!")
                    st.rerun()

                else:
                    st.error("Unable to delete expense.")



# ---------------- CUSTOMER CREDIT ----------------

with credit_tab:

    st.header("Customer Credit Management")

    add_credit_tab, view_credit_tab, manage_credit_tab = st.tabs([
        "Record Credit",
        "Credit History",
        "Manage Credit"
    ])

    customers = get_customers()

    # RECORD CREDIT
    with add_credit_tab:

        st.subheader("Record New Customer Credit")

        if customers.empty:

            st.warning("Please add customers first.")

        else:

            customer_options = {
                f"{row['name']} - {row['phone'] or 'No phone'}":
                row['customer_id']
                for _, row in customers.iterrows()
            }

            with st.form("add_credit_form"):

                selected = st.selectbox(
                    "Select Customer",
                    list(customer_options.keys())
                )

                customer_id = customer_options[selected]

                amount = st.number_input(
                    "Credit Amount (₹)",
                    min_value=0.01,
                    value=100.0
                )

                submitted = st.form_submit_button("Record Credit")

                if submitted:

                    if add_customer_credit(customer_id, amount):
                        st.success("Customer credit recorded!")
                        st.rerun()
                    else:
                        st.error("Unable to record credit.")

    # CREDIT HISTORY
    with view_credit_tab:

        credits = get_customer_credits()

        if credits.empty:

            st.info("No credit records available.")

        else:

            st.dataframe(
                credits,
                use_container_width=True,
                hide_index=True
            )

            pending = credits[
                credits["status"] == "Pending"
            ]["amount"].sum()

            paid = credits[
                credits["status"] == "Paid"
            ]["amount"].sum()

            c1, c2 = st.columns(2)

            c1.metric("Pending Credit", f"₹{pending:.2f}")
            c2.metric("Paid Credit", f"₹{paid:.2f}")

            st.subheader("Customer-wise Pending Credit")

            pending_summary = (
                credits[credits["status"] == "Pending"]
                .groupby("customer_name")["amount"]
                .sum()
            )

            st.bar_chart(pending_summary)

    # MANAGE CREDIT
    with manage_credit_tab:

        credits = get_customer_credits()

        if credits.empty:

            st.info("No credit records available.")

        else:

            options = {
                f"ID {row['credit_id']} - {row['customer_name']} - ₹{row['amount']} ({row['status']})":
                row['credit_id']
                for _, row in credits.iterrows()
            }

            selected = st.selectbox(
                "Select Credit Record",
                list(options.keys())
            )

            credit_id = options[selected]

            credit = credits[
                credits["credit_id"] == credit_id
            ].iloc[0]

            st.write("Customer:", credit["customer_name"])
            st.write("Amount:", f"₹{credit['amount']:.2f}")
            st.write("Current Status:", credit["status"])

            new_status = st.selectbox(
                "Update Credit Status",
                ["Pending", "Paid"],
                index=(
                    0 if credit["status"] == "Pending" else 1
                )
            )

            if st.button("Save Credit Status"):

                if update_credit_status(credit_id, new_status):
                    st.success("Credit status updated!")
                    st.rerun()
                else:
                    st.error("Unable to update credit.")

            if st.button("Delete Credit Record"):
                if delete_customer_credit(credit_id):
                    st.success("Credit record deleted!")
                    st.rerun()
                else:
                    st.error("Unable to delete credit.")




    
# ADD PRODUCT
with add_tab:

    st.subheader("Add New Product")

    with st.form("add_product_form"):

        name = st.text_input("Product Name")
        category = st.text_input("Category")

        price = st.number_input(
            "Selling Price (₹)",
            min_value=0.01,
            value=10.0
        )

        quantity = st.number_input(
            "Initial Quantity",
            min_value=0,
            step=1
        )

        low_limit = st.number_input(
            "Low Stock Limit",
            min_value=0,
            value=5,
            step=1
        )

        submitted = st.form_submit_button("Add Product")

        if submitted:

            if not name.strip():
                st.error("Please enter product name.")

            else:
                success = add_product(
                    name.strip(),
                    category.strip(),
                    price,
                    quantity,
                    low_limit
                )

                if success:
                    st.success("Product added successfully!")
                    st.rerun()

                else:
                    st.error("This product already exists!")



    # VIEW PRODUCTS
    with view_tab:

        st.subheader("Available Products")

        products = get_products()

        if products.empty:
            st.info("No products available.")

        else:

            st.dataframe(
                products,
                use_container_width=True,
                hide_index=True
            )

            st.subheader("Low Stock Products")

            low_products = products[
                products["quantity"] <=
                products["low_stock_limit"]
            ]

            if low_products.empty:
                st.success("All products have sufficient stock.")

            else:
                st.warning("Some products need restocking.")

                st.dataframe(
                    low_products,
                    use_container_width=True,
                    hide_index=True
                )


    # EDIT PRODUCT
    with edit_tab:

        st.subheader("Edit Product Details")

        products = get_products()

        if products.empty:
            st.info("Add a product first.")

        else:

            product_options = {
                f"{row['product_id']} - {row['name']}":
                row["product_id"]
                for _, row in products.iterrows()
            }

            selected = st.selectbox(
                "Select Product",
                list(product_options.keys())
            )

            product_id = product_options[selected]

            product = products[
                products["product_id"] == product_id
            ].iloc[0]

            with st.form("edit_product_form"):

                new_name = st.text_input(
                    "Product Name",
                    value=product["name"]
                )

                new_category = st.text_input(
                    "Category",
                    value=product["category"] or ""
                )

                new_price = st.number_input(
                    "Selling Price",
                    min_value=0.01,
                    value=float(product["price"])
                )

                new_limit = st.number_input(
                    "Low Stock Limit",
                    min_value=0,
                    value=int(product["low_stock_limit"])
                )

                save = st.form_submit_button("Save Changes")

                if save:

                    if not new_name.strip():
                        st.error("Product name cannot be empty.")

                    else:
                        update_product(
                            product_id,
                            new_name.strip(),
                            new_category.strip(),
                            new_price,
                            new_limit
                        )

                        st.success("Product updated successfully!")
                        st.rerun()


    
    # UPDATE STOCK
    with stock_tab:

        st.subheader("Set Available Stock")

        products = get_products()

        if products.empty:
            st.info("Add a product first.")

        else:

            options = {
                f"{row['name']} (Current Stock: {row['quantity']})":
                row["product_id"]
                for _, row in products.iterrows()
            }

            selected = st.selectbox(
                "Select Product",
                list(options.keys()),
                key="stock_product"
            )

            product_id = options[selected]

            new_quantity = st.number_input(
                "Enter Actual Available Quantity",
                min_value=0,
                step=1,
                key="new_stock_quantity"
            )

            if st.button("Save Stock"):

                success = set_stock(
                    product_id,
                    int(new_quantity)
                )

                if success:
                    st.success("Stock quantity updated successfully!")
                    st.rerun()
                else:
                    st.error("Unable to update stock.")

            st.divider()

            if st.button("Delete Selected Product"):
                if delete_product(product_id):
                    st.success("Product deleted successfully!")
                    st.rerun()
                else:
                    st.error("Could not delete product.")


