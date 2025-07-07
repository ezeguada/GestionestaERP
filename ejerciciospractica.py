# Create a Python dictionary similar to a Hash Table
book_ratings = {"Moby-Dick": 8, "The Great Gatsby": 9, "War and Peace": 10, "The Catcher in the Rye": 8}

# Access a value with its key. This happens in O(1) time
print(book_ratings["Moby-Dick"])   # Outputs: 8
# Another way to access a value with its key is by providing the default value if the key is not there. Complexity is also O(1).
print(book_ratings.get("Moby-Dick", 0)) # Outputs: 8
print(book_ratings.get("Moby Dick", 0)) # Outputs: 0

# Add a new key-value pair. The addition operation is also O(1)
book_ratings["To Kill a Mockingbird"] = 9
book_ratings["The Great Gatsby"] = 8
print(book_ratings)
# Outputs: {"Moby-Dick": 8, "The Great Gatsby": 8, "War and Peace": 10, "The Catcher in the Rye": 8, "To Kill a Mockingbird": 9}

# Remove a key-value pair. Deletion is also a constant time operation
del book_ratings["War and Peace"]
print(book_ratings)
# Outputs: {"Moby-Dick": 8, "The Great Gatsby": 9, "The Catcher in the Rye": 8, "To Kill a Mockingbird": 9}