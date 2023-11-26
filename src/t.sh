#!/bin/bash

# Specify the path to the usernames file
usernames_file="usernames.txt"

# Specify the path to the followers.py script
followers_script="followers.py"

# Read each username from the file and call the followers.py script
while IFS= read -r username; do
  # Set the USERNAME environment variable
  export USERNAME="$username"

  # Call the followers.py script
  python3 "$followers_script"

  # Optionally, you can unset the environment variable after the script is executed
  unset USERNAME
done < "$usernames_file"