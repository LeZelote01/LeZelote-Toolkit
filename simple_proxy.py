#!/usr/bin/env python3
"""
Simple proxy pour adapter les ports Emergent aux ports natifs du projet
Backend: 8001 -> 8000
Frontend: 3000 -> 8002
"""

import asyncio
import aiohttp
import aiohttp.web
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def proxy_backend(request):
    """Proxy pour backend: 8001 -> 8000"""
    url = f"http://localhost:8000{request.path_qs}"
    
    async with aiohttp.ClientSession() as session:
        async with session.request(
            method=request.method,
            url=url,
            headers=request.headers,
            data=await request.read()
        ) as resp:
            body = await resp.read()
            return aiohttp.web.Response(
                body=body,
                status=resp.status,
                headers=resp.headers
            )

async def proxy_frontend(request):
    """Proxy pour frontend: 3000 -> 8002"""
    url = f"http://localhost:8002{request.path_qs}"
    
    async with aiohttp.ClientSession() as session:
        async with session.request(
            method=request.method,
            url=url,
            headers=request.headers,
            data=await request.read()
        ) as resp:
            body = await resp.read()
            return aiohttp.web.Response(
                body=body,
                status=resp.status,
                headers=resp.headers
            )

async def create_backend_proxy():
    """Créer le proxy backend sur port 8001"""
    app = aiohttp.web.Application()
    app.router.add_route('*', '/{path:.*}', proxy_backend)
    return app

async def create_frontend_proxy():
    """Créer le proxy frontend sur port 3000"""
    app = aiohttp.web.Application()
    app.router.add_route('*', '/{path:.*}', proxy_frontend)
    return app

async def main():
    """Démarrer les deux proxies"""
    logger.info("🔧 Démarrage des proxies CyberSec Toolkit Pro 2025...")
    
    # Créer les applications
    backend_app = await create_backend_proxy()
    frontend_app = await create_frontend_proxy()
    
    # Créer les runners
    backend_runner = aiohttp.web.AppRunner(backend_app)
    frontend_runner = aiohttp.web.AppRunner(frontend_app)
    
    await backend_runner.setup()
    await frontend_runner.setup()
    
    # Créer les sites
    backend_site = aiohttp.web.TCPSite(backend_runner, 'localhost', 8001)
    frontend_site = aiohttp.web.TCPSite(frontend_runner, 'localhost', 3000)
    
    # Démarrer les serveurs
    await backend_site.start()
    await frontend_site.start()
    
    logger.info("✅ Proxies démarrés:")
    logger.info("   Backend: http://localhost:8001 -> http://localhost:8000")
    logger.info("   Frontend: http://localhost:3000 -> http://localhost:8002")
    logger.info("🎯 Les outils Emergent peuvent utiliser les ports 8001/3000")
    
    # Maintenir les serveurs actifs
    try:
        await asyncio.sleep(float('inf'))
    except KeyboardInterrupt:
        logger.info("🛑 Arrêt des proxies...")
    finally:
        await backend_runner.cleanup()
        await frontend_runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())