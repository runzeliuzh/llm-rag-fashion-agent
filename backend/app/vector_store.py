import chromadb
import json
import os
import numpy as np
from datetime import datetime
import hashlib

class LightweightEmbeddingModel:
    """Ultra-lightweight embedding using simple text features (no heavy models)"""
    
    def __init__(self):
        # No heavy model loading - use text-based features
        self.feature_keywords = [
            'fashion', 'style', 'trend', 'outfit', 'dress', 'casual', 'formal',
            'summer', 'winter', 'spring', 'autumn', 'fall', 'color', 'pattern',
            'vintage', 'modern', 'classic', 'bohemian', 'minimalist', 'chic'
        ]
    
    def encode(self, texts):
        """Create simple feature vectors without heavy ML models"""
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = []
        for text in texts:
            # Create simple feature vector based on keyword presence
            text_lower = text.lower()
            features = [
                1.0 if keyword in text_lower else 0.0 
                for keyword in self.feature_keywords
            ]
            
            # Add simple text statistics
            features.extend([
                len(text) / 1000.0,  # Normalized length
                text.count(' ') / 100.0,  # Word count approximation
                text.count(',') / 10.0,   # Punctuation density
            ])
            
            # Pad or truncate to fixed size
            while len(features) < 50:
                features.append(0.0)
            features = features[:50]
            
            embeddings.append(features)
        
        return embeddings

class CostOptimizedVectorStore:
    """Memory and cost-optimized vector store for Railway hobby plan"""
    
    def __init__(self, persist_directory="./data/chroma_db", max_documents=50):
        os.environ["CHROMA_TELEMETRY_ENABLED"] = "false"
        
        self.persist_directory = persist_directory
        self.backup_file = os.path.join(persist_directory, "lightweight_backup.json")
        self.max_documents = max_documents  # Reduced from 200 to 50 for Railway
        os.makedirs(persist_directory, exist_ok=True)
        
        # Use EphemeralClient (memory-only, no disk usage)
        self.client = chromadb.EphemeralClient()
        
        # Create collection with optimized settings for Railway
        self.collection = self.client.get_or_create_collection(
            name="fashion_lite",
            metadata={"hnsw:space": "cosine", "hnsw:M": 8}  # Reduced M for memory efficiency
        )
        
        # Use lightweight embedding
        self.embedding_model = LightweightEmbeddingModel()
        
        # Load existing data
        self.load_from_backup()
    
    def get_content_hash(self, content):
        """Generate hash for deduplication"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()[:16]
    
    def add_documents(self, documents, metadatas=None, ids=None, save_backup=True):
        """Add documents with size limits and deduplication"""
        if not documents:
            return
        
        # Deduplication
        unique_docs = []
        unique_metas = []
        unique_ids = []
        
        existing_hashes = set()
        try:
            # Get existing content hashes
            existing_data = self.collection.get()
            for existing_meta in existing_data.get('metadatas', []):
                if existing_meta and 'content_hash' in existing_meta:
                    existing_hashes.add(existing_meta['content_hash'])
        except:
            pass
        
        for i, doc in enumerate(documents):
            # Truncate long content to save memory
            doc_truncated = doc[:500] if len(doc) > 500 else doc
            doc_hash = self.get_content_hash(doc_truncated)
            
            if doc_hash not in existing_hashes:
                unique_docs.append(doc_truncated)
                
                # Add hash to metadata
                meta = metadatas[i] if metadatas and i < len(metadatas) else {}
                meta['content_hash'] = doc_hash
                meta['created_at'] = datetime.now().isoformat()
                unique_metas.append(meta)
                
                doc_id = ids[i] if ids and i < len(ids) else f"doc_{doc_hash}"
                unique_ids.append(doc_id)
                
                existing_hashes.add(doc_hash)
        
        if not unique_docs:
            print("No new unique documents to add")
            return
        
        # Check size limits before adding
        current_count = len(self.collection.get().get('documents', []))
        if current_count + len(unique_docs) > self.max_documents:
            # Remove oldest documents first
            self.cleanup_old_documents(target_size=self.max_documents - len(unique_docs))
        
        # Generate lightweight embeddings
        embeddings = self.embedding_model.encode(unique_docs)
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=unique_docs,
            metadatas=unique_metas,
            ids=unique_ids
        )
        
        print(f"Added {len(unique_docs)} unique documents (deduplication: {len(documents) - len(unique_docs)} skipped)")
        
        if save_backup:
            self.save_to_backup()
    
    def cleanup_old_documents(self, target_size):
        """Remove oldest documents to maintain size limits"""
        try:
            all_data = self.collection.get()
            documents = all_data.get('documents', [])
            metadatas = all_data.get('metadatas', [])
            ids = all_data.get('ids', [])
            
            if len(documents) <= target_size:
                return
            
            # Sort by creation time and keep newest
            docs_with_time = []
            for i, meta in enumerate(metadatas):
                created_at = meta.get('created_at', '2000-01-01T00:00:00') if meta else '2000-01-01T00:00:00'
                docs_with_time.append((created_at, i))
            
            # Sort by time (newest first) and keep target_size
            docs_with_time.sort(reverse=True)
            keep_indices = [idx for _, idx in docs_with_time[:target_size]]
            
            # Clear collection and re-add kept documents
            self.collection.delete(ids=ids)
            
            if keep_indices:
                keep_docs = [documents[i] for i in keep_indices]
                keep_metas = [metadatas[i] for i in keep_indices]
                keep_ids = [ids[i] for i in keep_indices]
                
                # Re-generate embeddings for kept documents
                embeddings = self.embedding_model.encode(keep_docs)
                
                self.collection.add(
                    embeddings=embeddings,
                    documents=keep_docs,
                    metadatas=keep_metas,
                    ids=keep_ids
                )
            
            removed_count = len(documents) - len(keep_indices)
            print(f"🧹 Cleaned up {removed_count} old documents, kept {len(keep_indices)}")
            
        except Exception as e:
            print(f"Cleanup failed: {e}")
    
    def save_to_backup(self):
        """Save to lightweight backup file"""
        try:
            all_data = self.collection.get()
            
            # Only save essential data (no embeddings to save space)
            backup_data = {
                "documents": all_data.get("documents", []),
                "metadatas": all_data.get("metadatas", []),
                "ids": all_data.get("ids", []),
                "timestamp": datetime.now().isoformat(),
                "count": len(all_data.get("documents", []))
            }
            
            with open(self.backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=1, ensure_ascii=False)
            
            # Check file size
            file_size = os.path.getsize(self.backup_file) / 1024  # KB
            print(f"💾 Backup saved: {backup_data['count']} docs, {file_size:.1f} KB")
            
        except Exception as e:
            print(f"Backup failed: {e}")
    
    def load_from_backup(self):
        """Load from backup with size limits"""
        if not os.path.exists(self.backup_file):
            print("No backup file found, starting fresh")
            return
        
        try:
            with open(self.backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            documents = backup_data.get("documents", [])
            metadatas = backup_data.get("metadatas", [])
            ids = backup_data.get("ids", [])
            
            if documents:
                # Limit loaded documents to max size
                if len(documents) > self.max_documents:
                    documents = documents[-self.max_documents:]
                    metadatas = metadatas[-self.max_documents:] if metadatas else []
                    ids = ids[-self.max_documents:] if ids else []
                
                # Load without triggering another backup
                self.add_documents(documents, metadatas, ids, save_backup=False)
                print(f"🔄 Restored {len(documents)} documents from backup")
            
        except Exception as e:
            print(f"Load from backup failed: {e}")
    
    def query(self, query_text, n_results=2):
        """Query with lightweight embeddings"""
        query_embedding = self.embedding_model.encode([query_text])
        return self.collection.query(
            query_embeddings=query_embedding,
            n_results=min(n_results, 5)  # Limit results
        )
    
    def load_crawled_data(self, json_file_path):
        """Load crawled data from JSON file (compatible with crawler.py)"""
        try:
            if not os.path.exists(json_file_path):
                print(f"File not found: {json_file_path}")
                return False
            
            with open(json_file_path, 'r', encoding='utf-8') as f:
                crawled_data = json.load(f)
            
            if not crawled_data:
                print("No data found in JSON file")
                return False
            
            # Convert crawled data to documents and metadata
            documents = []
            metadatas = []
            ids = []
            
            for item in crawled_data:
                if isinstance(item, dict) and 'content' in item:
                    # Create document text from content
                    doc_text = item['content']
                    
                    # Create metadata from other fields
                    metadata = {
                        'title': item.get('title', 'Untitled'),
                        'url': item.get('url', ''),
                        'source': item.get('source', ''),
                        'publication_date': item.get('publication_date', ''),
                        'categories': str(item.get('categories', [])),
                        'trend_keywords': str(item.get('trend_keywords', [])),
                        'extracted_at': item.get('extracted_at', ''),
                        'type': 'crawled_content'
                    }
                    
                    documents.append(doc_text)
                    metadatas.append(metadata)
                    ids.append(f"crawled_{self.get_content_hash(doc_text)}")
            
            if documents:
                self.add_documents(documents, metadatas, ids)
                print(f"✅ Successfully loaded {len(documents)} documents from {json_file_path}")
                return True
            else:
                print("No valid content found in crawled data")
                return False
                
        except Exception as e:
            print(f"Error loading crawled data: {e}")
            return False
    
    def get_stats(self):
        """Get storage statistics"""
        try:
            all_data = self.collection.get()
            doc_count = len(all_data.get('documents', []))
            
            backup_size = 0
            if os.path.exists(self.backup_file):
                backup_size = os.path.getsize(self.backup_file) / 1024  # KB
            
            return {
                "document_count": doc_count,
                "max_documents": self.max_documents,
                "backup_file_size_kb": backup_size,
                "memory_usage": "minimal (EphemeralClient)"
            }
        except Exception:
            return {"error": "Could not get stats"}

# Global lightweight instance with increased capacity for DeepSeek integration
cost_optimized_vector_store = CostOptimizedVectorStore(max_documents=200)
