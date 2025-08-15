"""
Adaptateur SQLite pour CyberSec Toolkit Pro 2025 PORTABLE
Émule l'API MongoDB pour la compatibilité
"""
import aiosqlite
import json
import uuid
import asyncio
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime


class PortableSQLiteAdapter:
    """Adaptateur SQLite qui émule l'API MongoDB pour la portabilité"""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = None
        
    async def _get_connection(self):
        """Obtient une connexion SQLite asynchrone"""
        if not self._connection:
            self._connection = await aiosqlite.connect(self.db_path)
            await self._connection.execute("PRAGMA foreign_keys = ON")
            await self._connection.commit()
        return self._connection
    
    async def get_collection(self, collection_name: str):
        """Retourne une collection émulée compatible MongoDB"""
        return PortableSQLiteCollection(self, collection_name)
    
    def close(self):
        """Ferme la connexion"""
        if self._connection:
            asyncio.create_task(self._connection.close())
            self._connection = None
    
    def get_stats(self):
        """Statistiques de la base portable"""
        return {
            "type": "sqlite_portable",
            "mode": "portable", 
            "file": str(self.db_path),
            "status": "connected" if self._connection else "disconnected"
        }


class PortableSQLiteCollection:
    """Collection SQLite qui émule l'API MongoDB"""
    
    def __init__(self, adapter: PortableSQLiteAdapter, collection_name: str):
        self.adapter = adapter
        self.collection_name = collection_name
        self.table_name = f"collection_{collection_name}"
    
    async def _ensure_table(self):
        """Assure l'existence de la table"""
        conn = await self.adapter._get_connection()
        await conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id TEXT PRIMARY KEY,
                data JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await conn.commit()
    
    async def insert_one(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Insère un document (émule MongoDB)"""
        await self._ensure_table()
        
        # Générer un ID si pas présent
        if '_id' not in document:
            document['_id'] = str(uuid.uuid4())
        
        # Ajouter timestamps
        document['created_at'] = datetime.now().isoformat()
        document['updated_at'] = datetime.now().isoformat()
        
        conn = await self.adapter._get_connection()
        await conn.execute(
            f"INSERT INTO {self.table_name} (id, data) VALUES (?, ?)",
            (document['_id'], json.dumps(document))
        )
        await conn.commit()
        
        return {"inserted_id": document['_id']}
    
    async def find_one(self, filter_dict: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Trouve un document (émule MongoDB)"""
        await self._ensure_table()
        
        conn = await self.adapter._get_connection()
        
        if not filter_dict:
            cursor = await conn.execute(f"SELECT data FROM {self.table_name} LIMIT 1")
        else:
            # Recherche simple par ID
            if '_id' in filter_dict:
                cursor = await conn.execute(
                    f"SELECT data FROM {self.table_name} WHERE id = ?",
                    (filter_dict['_id'],)
                )
            else:
                # Recherche JSON basique (peut être améliorée)
                cursor = await conn.execute(f"SELECT data FROM {self.table_name}")
        
        row = await cursor.fetchone()
        if row:
            return json.loads(row[0])
        return None
    
    async def find(self, filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Trouve des documents (émule MongoDB)"""
        await self._ensure_table()
        
        conn = await self.adapter._get_connection()
        cursor = await conn.execute(f"SELECT data FROM {self.table_name}")
        rows = await cursor.fetchall()
        
        documents = []
        for row in rows:
            doc = json.loads(row[0])
            # Filtrage simple si filtre fourni
            if not filter_dict or self._matches_filter(doc, filter_dict):
                documents.append(doc)
        
        return documents
    
    def _matches_filter(self, document: Dict[str, Any], filter_dict: Dict[str, Any]) -> bool:
        """Vérifie si un document correspond au filtre (logique simple)"""
        for key, value in filter_dict.items():
            if key not in document or document[key] != value:
                return False
        return True
    
    async def update_one(self, filter_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Met à jour un document (émule MongoDB)"""
        await self._ensure_table()
        
        conn = await self.adapter._get_connection()
        
        # Trouver le document à mettre à jour
        doc = await self.find_one(filter_dict)
        if not doc:
            return {"matched_count": 0, "modified_count": 0}
        
        # Appliquer la mise à jour
        if '$set' in update_dict:
            for key, value in update_dict['$set'].items():
                doc[key] = value
        
        doc['updated_at'] = datetime.now().isoformat()
        
        # Sauvegarder
        await conn.execute(
            f"UPDATE {self.table_name} SET data = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (json.dumps(doc), doc['_id'])
        )
        await conn.commit()
        
        return {"matched_count": 1, "modified_count": 1}
    
    async def delete_one(self, filter_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Supprime un document (émule MongoDB)"""
        await self._ensure_table()
        
        conn = await self.adapter._get_connection()
        
        if '_id' in filter_dict:
            cursor = await conn.execute(
                f"DELETE FROM {self.table_name} WHERE id = ?",
                (filter_dict['_id'],)
            )
            await conn.commit()
            return {"deleted_count": cursor.rowcount}
        
        return {"deleted_count": 0}


# Instance globale portable
_portable_db = None

def get_portable_database(db_path: str) -> PortableSQLiteAdapter:
    """Obtient l'instance de base portable"""
    global _portable_db
    if not _portable_db:
        _portable_db = PortableSQLiteAdapter(db_path)
    return _portable_db