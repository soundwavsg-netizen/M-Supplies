"""
Firestore Database Adapter

This module provides a wrapper around Firestore to make it compatible with existing repository interfaces.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.core.firebase import get_firestore_client


class FirestoreAdapter:
    """Adapter to make Firestore work like MongoDB collections"""
    
    def __init__(self, collection_name: str):
        self.db = get_firestore_client()
        self.collection_name = collection_name
        self._collection_ref = None
    
    @property
    def collection(self):
        """Get Firestore collection reference"""
        if self._collection_ref is None:
            self._collection_ref = self.db.collection(self.collection_name)
        return self._collection_ref
    
    async def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find a single document matching the query
        
        Args:
            query: Dictionary with field: value pairs
            
        Returns:
            Document dict or None
        """
        try:
            # Build Firestore query
            collection_ref = self.collection
            
            for field, value in query.items():
                collection_ref = collection_ref.where(field, '==', value)
            
            docs = collection_ref.limit(1).stream()
            
            for doc in docs:
                data = doc.to_dict()
                data['_id'] = doc.id  # Add document ID for compatibility
                return data
            
            return None
        
        except Exception as e:
            print(f"Error in find_one: {e}")
            return None
    
    async def find(self, query: Dict[str, Any] = None, skip: int = 0, limit: int = 100, sort: List[tuple] = None) -> List[Dict[str, Any]]:
        """
        Find multiple documents matching the query
        
        Args:
            query: Dictionary with field: value pairs (optional)
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            sort: List of (field, direction) tuples for sorting
            
        Returns:
            List of document dicts
        """
        try:
            collection_ref = self.collection
            
            # Apply filters
            if query:
                for field, value in query.items():
                    collection_ref = collection_ref.where(field, '==', value)
            
            # Apply sorting
            if sort:
                for field, direction in sort:
                    # 1 for ascending, -1 for descending
                    firestore_direction = 'ASCENDING' if direction == 1 else 'DESCENDING'
                    collection_ref = collection_ref.order_by(field, direction=firestore_direction)
            
            # Apply pagination
            if skip > 0:
                collection_ref = collection_ref.offset(skip)
            
            if limit > 0:
                collection_ref = collection_ref.limit(limit)
            
            # Get documents
            docs = collection_ref.stream()
            
            results = []
            for doc in docs:
                data = doc.to_dict()
                data['_id'] = doc.id
                results.append(data)
            
            return results
        
        except Exception as e:
            print(f"Error in find: {e}")
            return []
    
    async def insert_one(self, document: Dict[str, Any]) -> str:
        """
        Insert a single document
        
        Args:
            document: Document to insert
            
        Returns:
            Document ID
        """
        try:
            # Use 'id' field as document ID if available
            doc_id = document.get('id')
            doc_data = {k: v for k, v in document.items() if k != '_id'}
            
            if doc_id:
                self.collection.document(doc_id).set(doc_data)
                return doc_id
            else:
                doc_ref = self.collection.add(doc_data)
                return doc_ref[1].id
        
        except Exception as e:
            print(f"Error in insert_one: {e}")
            raise
    
    async def update_one(self, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        """
        Update a single document
        
        Args:
            query: Dictionary with field: value pairs to find document
            update: Update operations (supports $set, $inc, etc.)
            
        Returns:
            True if document was updated, False otherwise
        """
        try:
            # Find the document first
            doc = await self.find_one(query)
            if not doc:
                return False
            
            # Extract document ID
            doc_id = doc.get('id') or doc.get('_id')
            
            # Process update operations
            update_data = {}
            
            if '$set' in update:
                update_data.update(update['$set'])
            
            if '$inc' in update:
                # For increment operations, we need to get current value
                for field, value in update['$inc'].items():
                    current_value = doc.get(field, 0)
                    update_data[field] = current_value + value
            
            if '$push' in update:
                # For array push operations
                for field, value in update['$push'].items():
                    current_array = doc.get(field, [])
                    if not isinstance(current_array, list):
                        current_array = []
                    current_array.append(value)
                    update_data[field] = current_array
            
            if '$pull' in update:
                # For array pull operations
                for field, value in update['$pull'].items():
                    current_array = doc.get(field, [])
                    if isinstance(current_array, list) and value in current_array:
                        current_array.remove(value)
                    update_data[field] = current_array
            
            # Perform update
            self.collection.document(doc_id).update(update_data)
            return True
        
        except Exception as e:
            print(f"Error in update_one: {e}")
            return False
    
    async def delete_one(self, query: Dict[str, Any]) -> bool:
        """
        Delete a single document
        
        Args:
            query: Dictionary with field: value pairs to find document
            
        Returns:
            True if document was deleted, False otherwise
        """
        try:
            # Find the document first
            doc = await self.find_one(query)
            if not doc:
                return False
            
            # Extract document ID
            doc_id = doc.get('id') or doc.get('_id')
            
            # Delete document
            self.collection.document(doc_id).delete()
            return True
        
        except Exception as e:
            print(f"Error in delete_one: {e}")
            return False
    
    async def count_documents(self, query: Dict[str, Any] = None) -> int:
        """
        Count documents matching the query
        
        Args:
            query: Dictionary with field: value pairs (optional)
            
        Returns:
            Number of matching documents
        """
        try:
            collection_ref = self.collection
            
            # Apply filters
            if query:
                for field, value in query.items():
                    collection_ref = collection_ref.where(field, '==', value)
            
            # Get all documents and count
            docs = list(collection_ref.stream())
            return len(docs)
        
        except Exception as e:
            print(f"Error in count_documents: {e}")
            return 0


class FirestoreDB:
    """
    Firestore database wrapper to provide MongoDB-like interface
    """
    
    def __init__(self):
        self._collections = {}
    
    def __getattr__(self, collection_name: str) -> FirestoreAdapter:
        """
        Get a collection adapter by name
        
        Usage:
            db = FirestoreDB()
            users_collection = db.users
        """
        if collection_name not in self._collections:
            self._collections[collection_name] = FirestoreAdapter(collection_name)
        
        return self._collections[collection_name]
    
    def collection(self, collection_name: str) -> FirestoreAdapter:
        """
        Get a collection adapter by name (alternative syntax)
        
        Usage:
            db = FirestoreDB()
            users_collection = db.collection('users')
        """
        return self.__getattr__(collection_name)


# Global Firestore DB instance
firestore_db = FirestoreDB()
