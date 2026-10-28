from database.supabase_client import supabase

response = (
    supabase.table("documents")
    .select("id")
    .limit(1)
    .execute()
)

print("Supabase query successful!")
print(response.data)