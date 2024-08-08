import praw
import re
from datetime import datetime

# Function to setup Reddit account connection
def setup_reddit():
    print("Please enter your Reddit API credentials:")
    client_id = input("Client ID: ")
    client_secret = input("Client Secret: ")
    user_agent = input("User Agent: ")
    username = input("Username: ")
    password = input("Password: ")

    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
            username=username,
            password=password
        )
        reddit.user.me()
        print("Successfully connected to Reddit!")
        return reddit
    
    except Exception as e:
        print(f"Error connecting to Reddit: {e}")
        return None

# Function to choose a subreddit and keyword
def inputs():
    while True:
        subreddit_input = input("Enter the subreddit that you would like to search from: ")
        search_input = input(f'Enter a keyword to search for post titles in the {subreddit_input} subreddit: ')
        try:
            scrape_subreddit = scraping.subreddit(subreddit_input)
            return scrape_subreddit, search_input
        except Exception as e:
            print(f"Error: {e}")
            print("Subreddit not found or another error occurred. Please try again.")

# Function to search for and store matching posts
def search_posts(sub, key):
    matching_posts = []
    for post in sub.new(limit=None):
        if re.search(key, post.title, re.IGNORECASE):
            matching_posts.append(post)
    return matching_posts

# Function to print matching posts
def display_posts(posts):
    for i, post in enumerate(posts, 1):
        print(f"{i}. {post.title}")

# Function to give user choice to pick which post they want to view
def get_post_selection(posts):
    while True:
        try:
            selection = int(input("Enter the number of the post you want to view comments for (0 to exit): "))
            if selection == 0:
                return None
            if 1 <= selection <= len(posts):
                return posts[selection - 1]
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

# Function to display comments for the user selected post
def display_comments(item, depth=0, max_depth=3):
    if depth > max_depth:
        return
    if isinstance(item, praw.models.Submission):
        item.comments.replace_more(limit=0)
        for comment in item.comments:
            print_comment(comment, depth)
            display_comments(comment, depth + 1, max_depth)
    elif isinstance(item, praw.models.Comment):
        if hasattr(item, 'replies'):
            for reply in item.replies:
                print_comment(reply, depth)
                display_comments(reply, depth + 1, max_depth)

# Function to print the comments properly formatted as seen in reddit
def print_comment(comment, depth):
    indent = "  " * depth
    author = comment.author.name if comment.author else "[deleted]"
    score = comment.score
    created_time = datetime.fromtimestamp(comment.created_utc).strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"{indent}├─ Author: {author} | Score: {score} | Created: {created_time}")
    print(f"{indent}│  {comment.body.replace(chr(10), chr(10) + indent + '│  ')}")
    print(f"{indent}│")


# Main program loop to handle user interactions and display results
while True:
    scraping = setup_reddit()
    if scraping is not None:
        break
    print("Please try again with correct credentials.")

sub, key = inputs()

print("Searching for posts. This may take a while...")
matching_posts = search_posts(sub, key)

if not matching_posts:
    print("No matching posts found.")
else:
    print(f"Found {len(matching_posts)} matching post(s):\n")
    while True:
        display_posts(matching_posts)
        selected_post = get_post_selection(matching_posts)
        if selected_post is None:
            break
        print("\n" + "=" * 100 + '\n')
        print(f"Title: {selected_post.title}")
        print(f"Author: {selected_post.author}")
        print(f"Score: {selected_post.score}")
        print(f"Created: {datetime.fromtimestamp(selected_post.created_utc).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Number of comments: {selected_post.num_comments}")
        print(f"URL: {selected_post.url}")
        print('\n' + "=" * 100)
        if selected_post.selftext:
            print("\nPost content:")
            print(selected_post.selftext)
        print('\n'+"=" * 100)
        print("\nComments:\n")
        display_comments(selected_post)
        print("=" * 60 + "\n")