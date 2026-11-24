import streamlit as st
from datetime import date, timedelta
import csv
import io

# PROJECT 15 - LIBRARY BOOK BORROWING AND TRACKING SYSTEM

st.set_page_config(page_title="Library Management System", page_icon="📚", layout="wide")

# Keep the library data during Streamlit reruns
if "books" not in st.session_state:
    st.session_state.books = [
        {"title": "Harry Potter", "author": "J.K. Rowling", "status": "Available"},
        {"title": "Matilda", "author": "Roald Dahl", "status": "Available"},
        {"title": "The Hobbit", "author": "J.R.R. Tolkien", "status": "Available"},
        {"title": "Wonder", "author": "R.J. Palacio", "status": "Available"},
    ]

if "borrowed" not in st.session_state:
    st.session_state.borrowed = []

books = st.session_state.books
borrowed = st.session_state.borrowed

st.title("📚 Library Management System")
st.write("Search, borrow, return, and track library books.")

menu = st.sidebar.radio(
    "Library Menu",
    [
        "Show all books",
        "Search book",
        "Borrow book",
        "Return book",
        "Available books",
        "Borrowed books",
        "Overdue books",
        "Summary report",
    ],
)

# 1. Show all books
if menu == "Show all books":
    st.header("All Books")
    st.dataframe(
        [
            {"Book": book["title"], "Author": book["author"], "Status": book["status"]}
            for book in books
        ],
        use_container_width=True,
        hide_index=True,
    )

# 2. Search for a book
elif menu == "Search book":
    st.header("Search for a Book")
    search_text = st.text_input("Enter a book title or author").strip().lower()

    if search_text:
        matches = [
            book for book in books
            if search_text in book["title"].lower()
            or search_text in book["author"].lower()
        ]

        if matches:
            st.dataframe(
                [
                    {"Book": book["title"], "Author": book["author"], "Status": book["status"]}
                    for book in matches
                ],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.warning("Book not found.")

# 3. Borrow a book
elif menu == "Borrow book":
    st.header("Borrow a Book")
    available_books = [book for book in books if book["status"] == "Available"]

    if not available_books:
        st.info("There are no books currently available to borrow.")
    else:
        selected_title = st.selectbox(
            "Choose a book",
            [book["title"] for book in available_books],
        )
        student_name = st.text_input("Enter your name")

        if st.button("Borrow book", type="primary"):
            if not student_name.strip():
                st.error("Please enter your name.")
            else:
                selected_book = next(
                    book for book in books if book["title"] == selected_title
                )
                borrow_date = date.today()
                due_date = borrow_date + timedelta(days=14)

                selected_book["status"] = "Borrowed"
                borrowed.append(
                    {
                        "title": selected_book["title"],
                        "student": student_name.strip(),
                        "borrow_date": borrow_date,
                        "return_date": due_date,
                    }
                )

                st.success(f'"{selected_title}" was borrowed successfully!')
                st.write("Borrow date:", borrow_date.strftime("%d %B %Y"))
                st.write("Expected return date:", due_date.strftime("%d %B %Y"))

# 4. Return a book
elif menu == "Return book":
    st.header("Return a Book")
    if not borrowed:
        st.info("There are no borrowed books to return.")
    else:
        selected_title = st.selectbox(
            "Choose the book being returned",
            [record["title"] for record in borrowed],
        )

        if st.button("Return book", type="primary"):
            matching_record = next(
                record for record in borrowed if record["title"] == selected_title
            )
            matching_book = next(
                book for book in books if book["title"] == selected_title
            )

            borrowed.remove(matching_record)
            matching_book["status"] = "Available"
            st.success(f'"{selected_title}" has been returned successfully.')

# 5. Available books
elif menu == "Available books":
    st.header("Available Books")
    available_books = [book for book in books if book["status"] == "Available"]

    if available_books:
        st.dataframe(
            [
                {"Book": book["title"], "Author": book["author"]}
                for book in available_books
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("There are no available books.")

# 6. Borrowed books
elif menu == "Borrowed books":
    st.header("Currently Borrowed Books")

    if borrowed:
        st.dataframe(
            [
                {
                    "Book": record["title"],
                    "Borrower": record["student"],
                    "Borrowed on": record["borrow_date"],
                    "Expected return": record["return_date"],
                }
                for record in borrowed
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("There are no borrowed books.")

# 7. Overdue books
elif menu == "Overdue books":
    st.header("Overdue Books")
    overdue_records = [
        record for record in borrowed if date.today() > record["return_date"]
    ]

    if overdue_records:
        st.dataframe(
            [
                {
                    "Book": record["title"],
                    "Borrower": record["student"],
                    "Expected return": record["return_date"],
                    "Days overdue": (date.today() - record["return_date"]).days,
                }
                for record in overdue_records
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.success("There are no overdue books.")

# 8. Summary report
elif menu == "Summary report":
    st.header("Library Summary Report")
    available_count = sum(1 for book in books if book["status"] == "Available")
    borrowed_count = len(borrowed)
    overdue_count = sum(
        1 for record in borrowed if date.today() > record["return_date"]
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total books", len(books))
    col2.metric("Available books", available_count)
    col3.metric("Borrowed books", borrowed_count)
    col4.metric("Overdue books", overdue_count)

# Download the current book list as a CSV file
st.sidebar.divider()
csv_buffer = io.StringIO()
writer = csv.writer(csv_buffer)
writer.writerow(["Book title", "Author", "Availability"])
for book in books:
    writer.writerow([book["title"], book["author"], book["status"]])

st.sidebar.download_button(
    label="Download book list (CSV)",
    data=csv_buffer.getvalue(),
    file_name="books.csv",
    mime="text/csv",
)

st.sidebar.caption("Borrowing period: 14 days")
