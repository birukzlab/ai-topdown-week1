from fetcher import (
    fetch_bitcoin_price,
    fetch_posts,
    fetch_post_by_id,
    APIError,
)


def show_bitcoin_price():
    currency = input("Enter currency code (e.g. USD, EUR, GBP): ").strip() or "USD"
    try:
        price = fetch_bitcoin_price(currency)
        print(f"\n1 BTC ≈ {price:.2f} {currency.upper()}\n")
    except APIError as e:
        print(f"Error: {e}")


def show_posts_list():
    limit_str = input("How many posts to fetch? (blank for all): ").strip()
    limit = int(limit_str) if limit_str else None

    try:
        posts = fetch_posts(limit=limit)
        print(f"\nFetched {len(posts)} posts:")
        for post in posts:
            print(f"- [{post['id']}] {post['title']}")
        print()
    except APIError as e:
        print(f"Error: {e}")


def show_single_post():
    id_str = input("Enter post id: ").strip()
    if not id_str.isdigit():
        print("Post id must be a number.")
        return
    post_id = int(id_str)

    try:
        post = fetch_post_by_id(post_id)
        print(f"\nPost {post['id']}: {post['title']}\n")
        print(post["body"])
        print()
    except APIError as e:
        print(f"Error: {e}")


def main_menu():
    while True:
        print("=== API Data Fetcher ===")
        print("1. Show Bitcoin price")
        print("2. List posts")
        print("3. View a post by ID")
        print("0. Quit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            show_bitcoin_price()
        elif choice == "2":
            show_posts_list()
        elif choice == "3":
            show_single_post()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid option.\n")


if __name__ == "__main__":
    main_menu()
