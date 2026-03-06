import sys
import os

from core.rag import retrieve_math_context

def main():
    print("Starting test...")
    test_query = "What is the Pythagorean theorem?"
    print(f"Querying: {test_query}")
    try:
        context = retrieve_math_context(test_query, k=2)
        print("Success! Context retrieved successfully:\n")
        print(context)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
