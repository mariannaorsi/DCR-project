import mysql.connector
from tabulate import tabulate

def search_database(parameter):
    conn = mysql.connector.connect(
        user="root",
        host="localhost",
        ssl_disabled=True,
        database="schema",
        charset="utf8mb4",
        collation="utf8mb4_general_ci"
    )

    cursor = conn.cursor()

    query = '''
    ( SELECT '{search}' as search, 'File content' as find_match_in, file_name, path, file_type, dimension, last_modify ,owner,
   ROUND((LENGTH(content) - LENGTH(REPLACE(LOWER(content), LOWER('{search}'), ''))) / LENGTH('{search}')  ) as count
FROM file_info
USE INDEX (idx_filename)
WHERE LOWER(content) LIKE '%{search}%')

UNION ALL (

SELECT '{search}' as Search, 'Directory/File name' as find_match_in, file_name, path, file_type, dimension, last_modify, owner,
   ROUND((LENGTH(file_name) - LENGTH(REPLACE(LOWER(file_name), LOWER('{search}'), ''))) / LENGTH('{search}')  ) as count
FROM file_info2
WHERE LOWER(file_name) LIKE '%{search}%' )

    '''
    d = (query.format(search=parameter))

    cursor.execute(query.format(search=parameter))
    results = cursor.fetchall()

    conn.close()
    print(tabulate(results, headers=cursor.column_names))



if __name__ == '__main__':
    tosearch = input("Insert what you want to search:")
    search_database(tosearch)
