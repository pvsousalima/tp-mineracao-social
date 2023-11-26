import os
import pandas as pd
from typing import Iterator, Literal
from get import get_paginated
import psycopg2

# Define database connection parameters (replace with your database credentials and settings)
db_config = {
    "host": "35.192.158.57",
    "user": "my-database-user1",
    "password": "my-password",
    "database": "my-database",
}

# Função para salvar dados do post no banco de dados se não for uma duplicata
def save_relationship(post_data):
    try:
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()

        # Define a consulta SQL para criar a tabela 'posts' se ela não existir
        create_table_query = """
            CREATE TABLE IF NOT EXISTS follow_relationships (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255),
                location VARCHAR(255),
                relationship_type VARCHAR(255),
                target VARCHAR(255)
            )
        """
        
        # Execute a consulta de criação da tabela
        cursor.execute(create_table_query)
        connection.commit()

        # Define a consulta SQL para inserir dados do post na tabela
        insert_query = """
            INSERT INTO follow_relationships (username, location, relationship_type, target)
            VALUES (%s, %s, %s, %s)
        """

        username = post_data.get("username", "")
        location = post_data.get("location", "")
        relationship_type = post_data.get("relationship_type", "")
        target  =  post_data.get("target", "")

        # Insira dados do post no banco de dados
        cursor.execute(insert_query, (username, location, relationship_type, target))
        connection.commit()

        print("Dados do post salvos no banco de dados.")

    except psycopg2.Error as err:
        print("Erro:", err)

    finally:
        if connection:
            cursor.close()
            connection.close()

def pull_follow_relations(
    username: str,
    max: int = None,
    type: Literal["following", "followers"] = "following",
) -> Iterator[dict]:
    """Pull the given users' followers or the users a given user follows.

    :param str username: the username of the desired user
    :param int max: the maximum number of followers to pull
    :param str type: whether to pull followers or following"""

    # https://api.gettr.com/u/user/dineshdsouza/followers/?offset=0&max=10&incl=userstats|userinfo
    assert type in ["following", "followers"]

    if type == "following":
        url = f"/u/user/{username}/followings"
    elif type == "followers":
        url = f"/u/user/{username}/followers"

    n = 0  # Number of users emitted

    for data in get_paginated(
        url,
        params={
            "max": 20,  # They don't seem to limit this!
            "incl": "userstats|userinfo",
        },
        offset_step=20,
    ):

        # Check if we've run out of users to pull
        if len(data["data"]["list"]) == 0:
            return

        for username in data["data"]["list"]:
            # Verify that we haven't passed the max number of posts
            if max is not None and n >= max:
                return

            n += 1
            yield data["aux"]["uinf"].get(username)


def extract_data(user, target, relationship_type):
    username = user.get("username", "")
    location = user.get("location", "")
    return {'username': username, 'location': location, 'relationship_type': relationship_type, 'target': target}

# Assuming you have a DataFrame named df with columns: id, txt, username, udate, nickname, lang, detected_language, toxicity
# Add more columns as needed
df = pd.read_csv('./data/posts_with_detected_language.csv')

# Filter users with toxicity between 0.5 and 1 (inclusive)
filtered_users = df[(df['toxicity'] >= 0.5) & (df['toxicity'] <= 1)]

# Get the list of usernames from the filtered users
toxic_users = list(set(filtered_users['username']))

# Print or use the list of usernames as needed
# print(toxic_users)
print(len(toxic_users))

# Initialize a list to store extracted data
relationship_data = []

# Extract data for followers
for follower in pull_follow_relations(os.getenv('USERNAME'), 50, 'followers'):
    relationship_data.append(extract_data(follower, os.getenv('USERNAME'), 'follower'))

# Extract data for following
for following in pull_follow_relations(os.getenv('USERNAME'), 50, 'following'):
    relationship_data.append(extract_data(following, os.getenv('USERNAME'), 'following'))

for relationship in relationship_data:
    print(relationship)
    save_relationship(relationship)
    