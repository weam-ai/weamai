from pymongo import UpdateOne
from bson.objectid import ObjectId
import json
from src.db.config import db_instance
from pymongo.errors import PyMongoError
from rapidfuzz import process, fuzz
import hashlib
class SiteMapRepo:
    """Handles MongoDB operations using Singleton MongoDBClient."""

    def __init__(self, collection_name="sitemaps"):
        """Initialize database connection using MongoDBClient Singleton."""
        try:
            self.db = db_instance  # Using the existing singleton instance
            self.collection = self.db.get_collection(collection_name)
            print(f"Connected to MongoDB collection: {collection_name} successfully!")
        except PyMongoError as e:
            print(f"MongoDB Connection Error: {e}")
            raise

    def initilize_thread_id(self,thread_id):
        self.thread_id=thread_id
    
    def initilize_extra_data(self,extra_data:dict={}):
        self.extra_data=extra_data
        self.website=extra_data['website']
        self.website_hash_id=hashlib.sha256(str(self.website).encode("utf-8")).hexdigest()

    def upsert_blog_titles(self, blog_data={}):
        """
        Updates 'blog_titles' by adding only new titles if they do not already exist.
        
        :param record_id: The ID of the document.
        :param new_blog_data: A dictionary of new blog hashes to titles.
        """
        try:
            existing_hashes = self.get_existing_hashes_from_db()
            if len(existing_hashes)>0:
                blog_data=dict(zip(blog_data['title_hash'], blog_data['title']))
              
                filtered_blog_data = {
                    title_hash: title for title_hash, title in blog_data.items()
                    if title_hash not in existing_hashes
                }
                
                if not filtered_blog_data:
                    print("No new blog titles to update. All titles already exist.")
                    return self.thread_id

                # Update the record with only new titles
                update_query = {"$set": {f"blog_titles.{k}": v for k, v in filtered_blog_data.items()}}
                self.collection.update_one({"website_hash_id": self.website_hash_id}, update_query)

                print(f"Updated record with ID: {self.website_hash_id}")
                print(f"Updated Entries: {json.dumps(filtered_blog_data, indent=2)}")
                return self.thread_id
            else:
                print("Creating new entry.")
                result = self.collection.insert_one({"website_hash_id":self.website_hash_id, "blog_titles": blog_data,"website":self.website,"thread_id":ObjectId(self.thread_id)})

                print(f"Inserted new record with ID: {result.inserted_id}")
                print(f"Inserted Entries: {json.dumps(blog_data, indent=2)}")
                return result.inserted_id
        except PyMongoError as e:
            print(f"Failed to upsert record: {e}")
            return None

        
    def get_existing_hashes_from_db(self):
        """Fetch existing hashes directly from the database if record exists."""
        try:
            existing_data = self.collection.find_one({"website_hash_id": self.website_hash_id})
            if existing_data and "blog_titles" in existing_data:
                return set(existing_data["blog_titles"]['title_hash'])  # Extract hashes into a set
        except PyMongoError as e:
            print(f"Error fetching existing hashes: {e}")
        return set()

        
   
        
    def insert_sitemap_combined_record(self, data: dict):
        """Insert a single record containing sitemap data dynamically."""
        if not data:
            print("No data to insert.")
            return None
        
        try:
            result = self.collection.insert_one(data)
            print(f"Successfully inserted record with ID: {result.inserted_id}")
            return result.inserted_id
        except PyMongoError as e:
            print(f"Failed to insert record: {e}")
            return None

   
        
    def find_similar_titles_by_id(self, record_id, search_title, limit=10, similarity_threshold=80):
        """Find similar titles using fuzzy matching within a specific record's 'titles' list."""
        try:
            # Fetch the document by _id
            # record = self.collection.find_one(
            #     { "_id": record_id },  # Filter by record ID
            #     { "titles": 1, "_id": 0 }  # Only retrieve 'titles'
            # )

            record = self.collection.find_one({"thread_id": ObjectId(record_id)}, {"blog_titles.title": 1})
    
            if not record:
                print("No record found with the given ID.")
                return []
    
            # Extract titles list from the record
            titles_list = record.get("blog_titles", {}).get("title", [])
    
            if not titles_list:
                print("No titles found in the record.")
                return []
    
            # Use fuzzy matching to find similar titles
            similar_titles = process.extract(
                search_title, titles_list, scorer=fuzz.partial_ratio, limit=limit
            )
    
            # Ensure correct unpacking of returned values
            filtered_titles = [title for title, score, _ in similar_titles if score >= similarity_threshold]
    
            return filtered_titles
    
        except PyMongoError as e:
            print(f"Error in searching similar titles: {e}")
            return []