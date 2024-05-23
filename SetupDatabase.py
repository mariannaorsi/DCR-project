import mysql.connector
import subprocess
from datetime import datetime
import re

def setup_database():

    #connection at database
    conn = mysql.connector.connect(
        user="root",
        host="localhost",
        ssl_disabled=True,
        database="schema",
        charset="utf8mb4",
        collation="utf8mb4_general_ci"
    )

    cursor = conn.cursor()

    #query to create table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS file_info2  (
        id INT AUTO_INCREMENT PRIMARY KEY,
        file_type VARCHAR(255),
        path VARCHAR(255),
        file_name VARCHAR(255),
        dimension INT,
        last_modify DATETIME,
         owner VARCHAR(255),
        content MEDIUMTEXT
       
    )
    """)
    cursor.execute("SET NAMES 'UTF8MB4'")
    cursor.execute("SET CHARACTER SET 'UTF8MB4'")

    #query to create index
    cursor.execute("""
    CREATE INDEX idx_filename ON file_info2(file_name);
    """)


    conn.commit()
    conn.close()

def convert_to_datetime(datetime_str):
    datetime_str_without_offset = datetime_str.rsplit(' ', 1)[0]
    datetime_str_without_offset = re.sub(r'\.(\d+)', r'', datetime_str_without_offset)
    print(datetime_str_without_offset)
    datetime_obj = datetime.strptime(datetime_str_without_offset, '%Y-%m-%d %H:%M:%S')

    return datetime_obj.strftime('%Y-%m-%d %H:%M:%S')

def process_files():

    #connection to database
    conn = mysql.connector.connect(
        user="root",
        host="localhost",
        ssl_disabled=True,
        database="schema",
        charset="utf8mb4",
        collation="utf8mb4_general_ci"
    )

    cursor = conn.cursor()

    #linux command to return information about file, starting from a path
    #to prove scability, the project was tested with 2 starting path, one with 100 files and onestarting with path /home
    find_command = '''find /home -exec sh -c 'echo "$(file "$1" | cut -d: -f2 | cut -d, -f1);$1;$(basename "$1");$(stat -c "%s;%y;%U" "$1")"' _ {} \;'''

    output = subprocess.getoutput(find_command)
    lines = output.split('\n')
    tuple_counter = 0

    #prepare the attribute
    for line in lines:
        file_type, path, filename, dimension, last_modify, owner = line.split(';')
        last_modify = convert_to_datetime(last_modify)
        print(file_type, path, filename, dimension, last_modify, owner)

        content = ""
        if file_type == " HTML document":
            try:
                with open(path, 'r', encoding='utf-8', errors='replace') as file:
                    content = str(file.read())
            except Exception as e:
                print(f"Error reading file {path}: {e}")

        try:
            #query to fill the table
            cursor.execute("""
            INSERT INTO file_info2
            (file_type, path, file_name, dimension, last_modify, owner, content) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (file_type, path, filename, dimension, last_modify, owner, content))
            tuple_counter += 1

            # Commit every 10 tuples
            if tuple_counter % 10 == 0:
                conn.commit()
                print("Commit of 10 tuples executed.")

        except Exception as e:
            conn.rollback()  #
            print(f"Error : {e}")

    conn.commit()
    conn.close()


#SETUP DATABASE AND POPULATE
if __name__ == "__main__":
    setup_database()
    process_files()
