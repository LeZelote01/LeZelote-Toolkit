"""
Gestionnaire de base de données pour CyberSec Toolkit Pro 2025
Support mode portable (SQLite) et serveur (MongoDB)
"""
import os
import asyncio
from typing import Optional

# Configuration
from config import settings

# Adaptateur portable
if settings.portable_mode and settings.database_type == "sqlite":
    from portable.database.sqlite_adapter import get_portable_database
    
    class DatabaseManager:
        """Gestionnaire de base de données portable"""
        
        def __init__(self):
            self.adapter = get_portable_database(settings.get_database_url().replace("sqlite:///", ""))
            self.connected = False
        
        async def connect(self):
            """Connexion à la base portable"""
            # SQLite n'a pas besoin de connexion explicite
            self.connected = True
            print(f"✅ Base de données portable connectée: {settings.database_type}")
            return True
        
        async def disconnect(self):
            """Déconnexion de la base portable"""
            if self.adapter:
                self.adapter.close()
            self.connected = False
        
        async def get_collection(self, collection_name: str):
            """Retourne une collection (compatible MongoDB)"""
            return await self.adapter.get_collection(collection_name)
        
        def get_stats(self):
            """Statistiques de la base portable"""
            return {
                "type": "sqlite_portable",
                "mode": "portable",
                "file": settings.get_database_url(),
                "status": "connected" if self.connected else "disconnected"
            }

else:
    # Mode serveur avec MongoDB (original)
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        import pymongo
        MONGODB_AVAILABLE = True
    except ImportError:
        MONGODB_AVAILABLE = False
        print("⚠️ MongoDB modules non disponibles - mode serveur non supporté")
    
    if MONGODB_AVAILABLE:
        class DatabaseManager:
            """Gestionnaire de base de données serveur"""
            
            def __init__(self):
                self.client: Optional[AsyncIOMotorClient] = None
                self.database = None
                self.connected = False
        
        async def connect(self):
            """Connexion à MongoDB"""
            try:
                self.client = AsyncIOMotorClient(settings.mongo_url)
                self.database = self.client[settings.database_name]
                
                # Test de connexion
                await self.client.admin.command('ping')
                self.connected = True
                print(f"✅ Base de données MongoDB connectée: {settings.database_name}")
                return True
                
            except Exception as e:
                print(f"❌ Erreur connexion MongoDB: {e}")
                self.connected = False
                return False
        
        async def disconnect(self):
            """Déconnexion de MongoDB"""
            if self.client:
                self.client.close()
            self.connected = False
        
        async def get_collection(self, collection_name: str):
            """Retourne une collection MongoDB"""
            if not self.connected:
                await self.connect()
            return self.database[collection_name]
        
        def get_stats(self):
            """Statistiques de la base MongoDB"""
            return {
                "type": "mongodb",
                "mode": "server",
                "url": settings.mongo_url,
                "database": settings.database_name,
                "status": "connected" if self.connected else "disconnected"
            }
    else:
        # MongoDB non disponible - utiliser SQLite en fallback
        from portable.database.sqlite_adapter import get_portable_database
        
        class DatabaseManager:
            """Gestionnaire de base de données fallback"""
            
            def __init__(self):
                self.adapter = get_portable_database("cybersec_toolkit_fallback.db")
                self.connected = False
            
            async def connect(self):
                """Connexion à la base fallback"""
                self.connected = True
                print("📱 Mode fallback SQLite activé")
            
            async def disconnect(self):
                """Déconnexion de la base fallback"""
                self.connected = False
            
            async def get_collection(self, collection_name: str):
                """Retourne une collection via l'adaptateur"""
                return await self.adapter.get_collection(collection_name)
            
            def get_stats(self):
                """Statistiques de la base fallback"""
                return {
                    "type": "sqlite",
                    "mode": "fallback",
                    "file": "cybersec_toolkit_fallback.db",
                    "status": "connected" if self.connected else "disconnected"
                }

# Instance globale du gestionnaire
db_manager = DatabaseManager()

# Fonctions utilitaires
async def get_database():
    """Retourne la base de données (portable ou serveur)"""
    if not db_manager.connected:
        await db_manager.connect()
    return db_manager

async def get_collection(collection_name: str):
    """Retourne une collection (compatible portable/serveur)"""
    return await db_manager.get_collection(collection_name)

async def init_database():
    """Initialise la base de données selon le mode"""
    await db_manager.connect()
    
    if settings.portable_mode:
        # Initialiser les migrations portable
        from portable.database.migrations import setup_portable_database
        await setup_portable_database()
    
    return db_manager

async def close_database():
    """Ferme la connexion à la base de données"""
    await db_manager.disconnect()