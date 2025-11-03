"""
Firestore Database Adapter

This module provides a wrapper around Firestore to make it compatible with existing repository interfaces.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.core.firebase import get_firestore_client
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Thread pool for running synchronous Firestore operations
executor = ThreadPoolExecutor(max_workers=10)


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
    
    def _find_one_sync(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Synchronous find_one implementation"""
        try:
            collection_ref = self.collection
            
            for field, value in query.items():
                collection_ref = collection_ref.where(field, '==', value)
            
            docs = list(collection_ref.limit(1).stream())
            
            if docs:
                doc = docs[0]
                data = doc.to_dict()
                data['_id'] = doc.id
                return data
            
            return None
        except Exception as e:
            print(f"Error in find_one: {e}")
            return None
    
    async def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find a single document matching the query
        
        Args:
            query: Dictionary with field: value pairs
            
        Returns:
            Document dict or None
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(executor, self._find_one_sync, query)
    
    def _find_sync(self, query: Dict[str, Any], skip: int, limit: int, sort: List[tuple]) -> List[Dict[str, Any]]:
        """Synchronous find implementation"""
        try:
            collection_ref = self.collection
            
            if query:
                for field, value in query.items():
                    collection_ref = collection_ref.where(field, '==', value)
            
            if sort:
                for field, direction in sort:
                    from google.cloud.firestore import Query
                    firestore_direction = Query.ASCENDING if direction == 1 else Query.DESCENDING
                    collection_ref = collection_ref.order_by(field, direction=firestore_direction)
            
            if skip > 0:
                collection_ref = collection_ref.offset(skip)
            
            if limit > 0:
                collection_ref = collection_ref.limit(limit)
            
            docs = list(collection_ref.stream())
            
            results = []
            for doc in docs:
                data = doc.to_dict()
                data['_id'] = doc.id
                results.append(data)
            
            return results
        except Exception as e:
            print(f"Error in find: {e}")
            return []
    
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
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(executor, self._find_sync, query, skip, limit, sort)
    
    def _insert_one_sync(self, document: Dict[str, Any]) -> str:
        """Synchronous insert_one implementation"""
        try:
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
    
    async def insert_one(self, document: Dict[str, Any]) -> str:
        """
        Insert a single document
        
        Args:
            document: Document to insert
            
        Returns:
            Document ID
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(executor, self._insert_one_sync, document)
    
    def _update_one_sync(self, doc, update: Dict[str, Any]) -> bool:
        """Synchronous update_one helper"""
        try:
            doc_id = doc.get('id') or doc.get('_id')
            
            update_data = {}
            
            if '$set' in update:
                update_data.update(update['$set'])
            
            if '$inc' in update:
                for field, value in update['$inc'].items():
                    current_value = doc.get(field, 0)
                    update_data[field] = current_value + value
            
            if '$push' in update:
                for field, value in update['$push'].items():
                    current_array = doc.get(field, [])
                    if not isinstance(current_array, list):
                        current_array = []
                    current_array.append(value)
                    update_data[field] = current_array
            
            if '$pull' in update:
                for field, value in update['$pull'].items():
                    current_array = doc.get(field, [])
                    if isinstance(current_array, list) and value in current_array:
                        current_array.remove(value)
                    update_data[field] = current_array
            
            self.collection.document(doc_id).update(update_data)
            return True
        except Exception as e:
            print(f"Error in update_one_sync: {e}")
            return False
    
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
            doc = await self.find_one(query)
            if not doc:
                return False
            
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(executor, self._update_one_sync, doc, update)
        except Exception as e:
            print(f"Error in update_one: {e}")
            return False
    
    def _delete_one_sync(self, doc_id: str) -> bool:
        """Synchronous delete_one helper"""
        try:
            self.collection.document(doc_id).delete()
            return True
        except Exception as e:
            print(f"Error in delete_one_sync: {e}")
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
            doc = await self.find_one(query)
            if not doc:
                return False
            
            doc_id = doc.get('id') or doc.get('_id')
            
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(executor, self._delete_one_sync, doc_id)
        except Exception as e:
            print(f"Error in delete_one: {e}")
            return False
    
    def _count_documents_sync(self, query: Dict[str, Any]) -> int:
        """Synchronous count_documents implementation"""
        try:
            collection_ref = self.collection
            
            if query:
                for field, value in query.items():
                    collection_ref = collection_ref.where(field, '==', value)
            
            docs = list(collection_ref.stream())
            return len(docs)
        except Exception as e:
            print(f"Error in count_documents: {e}")
            return 0
    
    async def count_documents(self, query: Dict[str, Any] = None) -> int:
        """
        Count documents matching the query
        
        Args:
            query: Dictionary with field: value pairs (optional)
            
        Returns:
            Number of matching documents
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(executor, self._count_documents_sync, query)
    
    def _distinct_sync(self, field: str) -> List[Any]:
        """Synchronous distinct implementation"""
        try:
            docs = list(self.collection.stream())
            values = set()
            for doc in docs:
                data = doc.to_dict()
                if field in data and data[field] is not None:
                    values.add(data[field])
            return list(values)
        except Exception as e:
            print(f"Error in distinct: {e}")
            return []
    
    async def distinct(self, field: str) -> List[Any]:
        """
        Get distinct values for a field
        
        Args:
            field: Field name to get distinct values for
            
        Returns:
            List of distinct values
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(executor, self._distinct_sync, field)


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
