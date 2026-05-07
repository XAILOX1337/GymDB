from db.connection import engine

class ClientService:
    def register(self, last_name, first_name, birth_date, phone, passport, employee_id):
        
        with engine.raw_connection() as raw_conn:
            cursor = raw_conn.cursor()
            
            
            cursor.execute("""
                EXEC sp_RegisterClient 
                    @LastName=?, @FirstName=?, @BirthDate=?, 
                    @Phone=?, @PassportData=?, @EmployeeID=?
            """, last_name, first_name, birth_date, phone, passport, employee_id)
            
           
            while cursor.description is None:
                if not cursor.nextset():
                    break
            
            
            row = cursor.fetchone()
            client_id = row[0] if row else None
            
            raw_conn.commit()
            cursor.close()
            return client_id


# Тест на добавление клиента 
# client = ClientService()
# client_id = client.register(
#     last_name="Иванов",
#     first_name="Петр",
#     birth_date="1999-05-15",
#     phone="+78991459868",
#     passport="1200 132358",
#     employee_id=3  # ← ID администратора
# )
# print(client_id)