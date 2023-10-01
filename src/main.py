import psycopg2
from search import pull
import pandas as pd
import time 
import random

# Define database connection parameters (replace with your database credentials and settings)
db_config = {
    "host": "35.232.206.196",
    "user": "my-database-user1",
    "password": "my-password",
    "database": "my-database",
}

def is_duplicate(post_data, db_config):
    try:
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()

        # Define the SQL query to check for duplicates based on all relevant fields
        check_query = """
            SELECT COUNT(*) FROM posts
            WHERE 
                txt = %s
                AND username = %s
                AND udate = %s
                AND nickname = %s
                AND lang = %s
        """

        # Extract post properties
        txt = post_data.get("txt", "")
        username = post_data.get("username", "")
        udate = post_data.get("udate", "")
        nickname = post_data.get("nickname", "")
        lang = post_data.get("lang", "")

        # Execute the query
        cursor.execute(check_query, (txt, username, udate, nickname, lang))
        count = cursor.fetchone()[0]

        # If count > 0, a similar record exists (duplicate)
        return count > 0

    except psycopg2.Error as err:
        print("Error:", err)

    finally:
        if connection:
            cursor.close()
            connection.close()

# Função para salvar dados do post no banco de dados se não for uma duplicata
def save_post_to_database_if_not_duplicate(post_data, db_config):
    try:
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()

        # Define a consulta SQL para criar a tabela 'posts' se ela não existir
        create_table_query = """
            CREATE TABLE IF NOT EXISTS posts (
                id SERIAL PRIMARY KEY,
                txt TEXT,
                username VARCHAR(255),
                udate BIGINT,
                nickname VARCHAR(255),
                lang VARCHAR(255)
            )
        """
        
        # Execute a consulta de criação da tabela
        cursor.execute(create_table_query)
        connection.commit()

        # Verifique se o post é uma duplicata antes de inserir
        if not is_duplicate(post_data, db_config):
            # Define a consulta SQL para inserir dados do post na tabela
            insert_query = """
                INSERT INTO posts (txt, username, udate, nickname, lang)
                VALUES (%s, %s, %s, %s, %s)
            """

            # Extraia as propriedades do post
            txt = post_data.get("txt", "")
            username = post_data.get("username", "")
            udate = post_data.get("udate", "")
            nickname = post_data.get("nickname", "")
            lang = post_data.get("lang", "")

            # Insira dados do post no banco de dados
            cursor.execute(insert_query, (txt, username, udate, nickname, lang))
            connection.commit()

            print("Dados do post salvos no banco de dados.")

    except psycopg2.Error as err:
        print("Erro:", err)

    finally:
        if connection:
            cursor.close()
            connection.close()


def extract_data_properties(data):
    """Extract specific properties from the given data format.

    :param dict data: The data format as provided.
    :return: A dictionary containing the extracted properties.
    :rtype: dict
    """
    properties = {
        'txt': data.get('txt', ''),
        'username': data.get('uinf', {}).get('username', ''),
        'udate': data.get('udate', ''),
        'nickname': data.get('uinf', {}).get('nickname', ''),
        'lang': data.get('uinf', {}).get('lang', '')
    }
    return properties

# Read data from the CSV file into a DataFrame
df = pd.read_csv('hatebase_data.csv')

# Extract the numeric part from the 'sightings' column
# Extract the numeric part from the 'sightings' column (handling both comma and dot as separators)
df['sightings'] = df['sightings'].str.replace(',', '').str.extract('(\d+)', expand=False)

# Convert the 'sightings' column to numeric type (float)
df['sightings'] = pd.to_numeric(df['sightings'], errors='coerce')

# Remove rows with NaN values in the 'sightings' column
df = df.dropna(subset=['sightings'])

df['term'] = df['term'].str.replace(r'\([^)]*\)', '', regex=True)

# Filter rows where offense_level is "Highly offensive" or "Highly offensive"
filtered_df = df[(df['offense_level'] == 'Extremely offensive') | (df['offense_level'] == 'Highly offensive')]

# Display the filtered DataFrame
print(filtered_df)

for term in filtered_df['term']:
    for post in pull(term, 500):
        result = extract_data_properties(post)
        print(result)
        save_post_to_database_if_not_duplicate(result, db_config)
    
    # Gere um valor aleatório entre 30 e 60 segundos
    random_sleep_time = random.randint(30, 60)

    # Aguarde o tempo aleatório
    time.sleep(random_sleep_time)
