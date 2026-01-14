"""
Test script to verify Vector Search Index is working
"""
import asyncio
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

async def test_vector_search():
    uri = os.getenv('MONGODB_URI')
    if not uri:
        print('ERROR: MONGODB_URI not set')
        return

    client = AsyncIOMotorClient(uri)
    db = client[os.getenv('MONGODB_DB_NAME', 'personal_website')]
    collection = db[os.getenv('MONGODB_COLLECTION', 'documents')]

    # Create a dummy embedding (1536 dimensions of zeros)
    dummy_embedding = [0.0] * 1536

    # Try vector search
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": dummy_embedding,
                "numCandidates": 10,
                "limit": 3
            }
        },
        {
            "$project": {
                "_id": 1,
                "filename": 1,
                "content": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]

    try:
        print("Testing Vector Search...")
        results = await collection.aggregate(pipeline).to_list(length=3)

        if results:
            print(f"SUCCESS! Found {len(results)} results")
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result.get('filename')}")
                print(f"   Score: {result.get('score', 0):.4f}")
                print(f"   Content preview: {result.get('content', '')[:100]}...")
        else:
            print("WARNING: Vector Search executed but returned no results")
            print("This might mean:")
            print("  1. The index is still building (check Atlas UI)")
            print("  2. No documents in the collection")

    except Exception as e:
        print("ERROR: Vector Search failed!")
        print(f"Error: {str(e)}")
        print("\nPossible causes:")
        print("  1. Vector Search Index 'vector_index' does not exist")
        print("  2. Index is still building (check Atlas UI)")
        print("  3. Index configuration is incorrect")

    client.close()

if __name__ == "__main__":
    asyncio.run(test_vector_search())
