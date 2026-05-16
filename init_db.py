import pg8000

def create_infrastructure():
    try:
        # Conecta no banco padrao 'postgres'
        conn = pg8000.connect(
            user="postgres",
            password="Lylu2904",
            host="localhost",
            port=5432,
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Cria o banco de dados do projeto
        cursor.execute("CREATE DATABASE salacerta_reservas")
        print("Database 'salacerta_reservas' created successfully.")
        
        cursor.close()
        conn.close()
    except Exception as e:
        if "already exists" in str(e):
            print("Database already exists. Proceeding...")
        else:
            print(f"Error creating database: {e}")

if __name__ == "__main__":
    create_infrastructure()