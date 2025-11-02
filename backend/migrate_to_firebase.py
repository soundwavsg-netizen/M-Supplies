"""
MongoDB to Firebase Firestore Migration Script

This script migrates all data from MongoDB to Firebase Firestore while preserving data structure.
It also creates Firebase Auth users from existing MongoDB users.
"""
import asyncio
import os
import sys
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.firebase import initialize_firebase, get_firestore_client, create_firebase_user, get_firebase_auth

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class MongoToFirebaseMigration:
    def __init__(self):
        self.mongo_client = None
        self.mongo_db = None
        self.firestore_db = None
        self.migration_stats = {
            'collections': {},
            'firebase_users': 0,
            'errors': []
        }
    
    async def connect_mongo(self):
        """Connect to MongoDB"""
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.environ.get('DB_NAME', 'polymailer_db')
        
        self.mongo_client = AsyncIOMotorClient(mongo_url)
        self.mongo_db = self.mongo_client[db_name]
        print(f"✅ Connected to MongoDB: {db_name}")
    
    def connect_firestore(self):
        """Connect to Firestore"""
        self.firestore_db = initialize_firebase()
        print("✅ Connected to Firestore")
    
    async def migrate_collection(self, collection_name: str, batch_size: int = 500):
        """
        Migrate a single collection from MongoDB to Firestore
        
        Args:
            collection_name: Name of the collection to migrate
            batch_size: Number of documents to process in each batch
        """
        print(f"\n📦 Migrating collection: {collection_name}")
        
        try:
            # Get MongoDB collection
            mongo_collection = self.mongo_db[collection_name]
            total_docs = await mongo_collection.count_documents({})
            
            if total_docs == 0:
                print(f"⚠️  Collection '{collection_name}' is empty, skipping...")
                self.migration_stats['collections'][collection_name] = {
                    'total': 0,
                    'migrated': 0,
                    'failed': 0
                }
                return
            
            print(f"   Total documents: {total_docs}")
            
            # Get Firestore collection reference
            firestore_collection = self.firestore_db.collection(collection_name)
            
            migrated_count = 0
            failed_count = 0
            
            # Process documents in batches
            cursor = mongo_collection.find({})
            batch = []
            
            async for doc in cursor:
                # Remove MongoDB's _id field
                if '_id' in doc:
                    del doc['_id']
                
                # Convert datetime objects to ISO strings for Firestore
                doc = self._convert_dates_to_strings(doc)
                
                batch.append(doc)
                
                if len(batch) >= batch_size:
                    # Write batch to Firestore
                    migrated, failed = await self._write_batch(firestore_collection, batch)
                    migrated_count += migrated
                    failed_count += failed
                    
                    print(f"   Progress: {migrated_count}/{total_docs} documents migrated...")
                    batch = []
            
            # Write remaining documents
            if batch:
                migrated, failed = await self._write_batch(firestore_collection, batch)
                migrated_count += migrated
                failed_count += failed
            
            self.migration_stats['collections'][collection_name] = {
                'total': total_docs,
                'migrated': migrated_count,
                'failed': failed_count
            }
            
            print(f"✅ Completed: {migrated_count}/{total_docs} documents migrated")
            if failed_count > 0:
                print(f"⚠️  Failed: {failed_count} documents")
        
        except Exception as e:
            error_msg = f"Error migrating collection '{collection_name}': {str(e)}"
            print(f"❌ {error_msg}")
            self.migration_stats['errors'].append(error_msg)
    
    async def _write_batch(self, firestore_collection, batch):
        """Write a batch of documents to Firestore"""
        migrated = 0
        failed = 0
        
        for doc in batch:
            try:
                # Use 'id' field as document ID if available, otherwise auto-generate
                doc_id = doc.get('id')
                if doc_id:
                    firestore_collection.document(doc_id).set(doc)
                else:
                    firestore_collection.add(doc)
                
                migrated += 1
            
            except Exception as e:
                failed += 1
                self.migration_stats['errors'].append(f"Failed to write document: {str(e)}")
        
        return migrated, failed
    
    def _convert_dates_to_strings(self, doc):
        """Recursively convert datetime objects to ISO format strings"""
        if isinstance(doc, dict):
            return {k: self._convert_dates_to_strings(v) for k, v in doc.items()}
        elif isinstance(doc, list):
            return [self._convert_dates_to_strings(item) for item in doc]
        elif isinstance(doc, datetime):
            return doc.isoformat()
        else:
            return doc
    
    async def migrate_users_to_firebase_auth(self):
        """
        Create Firebase Auth users from MongoDB users
        Note: Passwords cannot be migrated, users will need to reset passwords
        """
        print("\n👤 Migrating users to Firebase Authentication")
        
        try:
            users_collection = self.mongo_db['users']
            total_users = await users_collection.count_documents({})
            
            if total_users == 0:
                print("⚠️  No users found in MongoDB")
                return
            
            print(f"   Total users: {total_users}")
            
            firebase_auth = get_firebase_auth()
            migrated = 0
            skipped = 0
            
            cursor = users_collection.find({})
            
            async for user in cursor:
                try:
                    email = user.get('email')
                    if not email:
                        print(f"⚠️  Skipping user without email: {user.get('id', 'unknown')}")
                        skipped += 1
                        continue
                    
                    # Check if user already exists in Firebase
                    try:
                        existing_user = firebase_auth.get_user_by_email(email)
                        print(f"   User already exists in Firebase: {email}")
                        skipped += 1
                        continue
                    except firebase_auth.UserNotFoundError:
                        pass  # User doesn't exist, proceed with creation
                    
                    # Create Firebase user with a temporary password
                    # Users will need to use "Forgot Password" to set their password
                    display_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
                    if not display_name:
                        display_name = user.get('displayName', email.split('@')[0])
                    
                    phone = user.get('phone', user.get('phoneNumber'))
                    
                    # Format phone number if needed (must start with +)
                    if phone and not phone.startswith('+'):
                        if phone.startswith('65'):
                            phone = f'+{phone}'
                        elif phone.startswith('60'):
                            phone = f'+{phone}'
                        else:
                            phone = f'+65{phone}'  # Default to Singapore
                    
                    user_data = {
                        'email': email,
                        'email_verified': False,  # Users need to verify
                        'display_name': display_name,
                    }
                    
                    if phone:
                        try:
                            user_data['phone_number'] = phone
                        except:
                            # Skip invalid phone numbers
                            pass
                    
                    # Use user's existing ID as UID if available
                    if user.get('id'):
                        user_data['uid'] = user.get('id')
                    
                    firebase_user = firebase_auth.create_user(**user_data)
                    
                    # Update Firestore user document with Firebase UID
                    firestore_users = self.firestore_db.collection('users')
                    firestore_users.document(user['id']).update({
                        'uid': firebase_user.uid,
                        'firebase_migrated': True,
                        'migration_date': datetime.utcnow().isoformat()
                    })
                    
                    migrated += 1
                    print(f"   ✅ Created Firebase user: {email} (UID: {firebase_user.uid})")
                
                except Exception as e:
                    error_msg = f"Failed to migrate user {user.get('email', 'unknown')}: {str(e)}"
                    print(f"   ❌ {error_msg}")
                    self.migration_stats['errors'].append(error_msg)
                    skipped += 1
            
            self.migration_stats['firebase_users'] = migrated
            print(f"\n✅ Firebase Auth migration complete: {migrated} users created, {skipped} skipped")
        
        except Exception as e:
            error_msg = f"Error migrating users to Firebase Auth: {str(e)}"
            print(f"❌ {error_msg}")
            self.migration_stats['errors'].append(error_msg)
    
    async def migrate_all(self):
        """Run complete migration"""
        print("\n" + "="*60)
        print("🚀 MONGODB TO FIREBASE MIGRATION")
        print("="*60)
        
        # Connect to databases
        await self.connect_mongo()
        self.connect_firestore()
        
        # Get list of collections to migrate
        collection_names = await self.mongo_db.list_collection_names()
        print(f"\n📚 Found {len(collection_names)} collections to migrate")
        
        # Migrate each collection
        for collection_name in collection_names:
            await self.migrate_collection(collection_name)
        
        # Migrate users to Firebase Auth
        await self.migrate_users_to_firebase_auth()
        
        # Print summary
        self.print_summary()
        
        # Close connections
        self.mongo_client.close()
        print("\n✅ Migration complete!")
    
    def print_summary(self):
        """Print migration summary"""
        print("\n" + "="*60)
        print("📊 MIGRATION SUMMARY")
        print("="*60)
        
        print("\n📦 Collections:")
        for collection_name, stats in self.migration_stats['collections'].items():
            status = "✅" if stats['failed'] == 0 else "⚠️ "
            print(f"   {status} {collection_name}: {stats['migrated']}/{stats['total']} documents")
        
        print(f"\n👤 Firebase Auth Users: {self.migration_stats['firebase_users']} created")
        
        if self.migration_stats['errors']:
            print(f"\n❌ Errors ({len(self.migration_stats['errors'])}):")
            for error in self.migration_stats['errors'][:10]:  # Show first 10 errors
                print(f"   - {error}")
            
            if len(self.migration_stats['errors']) > 10:
                print(f"   ... and {len(self.migration_stats['errors']) - 10} more errors")


async def main():
    """Main migration function"""
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv('/app/backend/.env')
    
    migration = MongoToFirebaseMigration()
    await migration.migrate_all()


if __name__ == "__main__":
    asyncio.run(main())
