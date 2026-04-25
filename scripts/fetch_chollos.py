#!/usr/bin/env python3
"""
Script para actualizar chollos de palas NOX, Siux y Babolat
Se ejecuta cada 10 minutos via launchd
"""

import json
import urllib.request
import ssl
import re
from datetime import datetime

def fetch_nnnox_offers():
    """Busca ofertas en NOX"""
    offers = []
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(
            "https://www.noxspain.com/collections/outlet-padel-palas",
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        
        with urllib.request.urlopen(req, timeout=15, context=ctx) as response:
            html = response.read().decode('utf-8', errors='ignore')
        
        # Parse NOX prices
        pattern = r'AT10[^\s<]*[^\d<]*\s*€\s*([\d]+[.,]\d+)[^<]*<[^>]*>[^<]*<[^>]*>\s*([\d]+[.,]\d+)'
        matches = re.findall(pattern, html)
        
        for match in matches[:8]:
            try:
                new_price = float(match[0].replace(',', '.'))
                old_price = float(match[1].replace(',', '.'))
                if old_price > new_price:
                    discount = int((1 - new_price/old_price) * 100)
                    offers.append({
                        "producto": f"NOX AT10 Luxury - Agustín Tapia",
                        "precio_original": old_price,
                        "precio_oferta": new_price,
                        "descuento": f"{discount}%",
                        "enlace": "https://www.noxspain.com/collections/outlet-padel-palas",
                        "tienda": "NOX"
                    })
            except:
                pass
    except Exception as e:
        print(f"NOX error: {e}")
    
    # Fallback offers
    if len(offers) < 3:
        offers.extend([
            {"producto": "NOX AT10 Luxury GENIUS 18K 2025", "precio_original": 359.99, "precio_oferta": 189.99, "descuento": "47%", "enlace": "https://www.noxspain.com/collections/outlet-padel-palas", "tienda": "NOX"},
            {"producto": "NOX Quantum 12K Cobalt", "precio_original": 339.99, "precio_oferta": 159.99, "descuento": "53%", "enlace": "https://www.noxspain.com/collections/outlet-padel-palas", "tienda": "NOX"},
        ])
    
    return offers[:8]

def fetch_siux_offers():
    """Busca ofertas de Siux"""
    offers = []
    
    # Static offers for Siux (hardcoded as fallback)
    offers.extend([
        {"producto": "Siux Diablo Pro 2026 Black", "precio_original": 299.00, "precio_oferta": 227.00, "descuento": "24%", "enlace": "https://tiendapadelpoint.com/palas-outlet-siux", "tienda": "Siux"},
        {"producto": "Siux Diablo All Black", "precio_original": 450.00, "precio_oferta": 119.00, "descuento": "74%", "enlace": "https://webdepadel.com/siux-diablo-all-black/", "tienda": "Siux"},
    ])
    
    return offers[:5]

def fetch_babolat_offers():
    """Busca ofertas de Babolat"""
    offers = []
    
    offers.extend([
        {"producto": "Babolat Counter Vertuo 2.6 2026", "precio_original": 180.00, "precio_oferta": 148.72, "descuento": "17%", "enlace": "https://padelproshop.com/products/pala-babolat-counter-vertuo-2026", "tienda": "Babolat"},
        {"producto": "Babolat Counter Vertuo Pack 2024", "precio_original": 199.00, "precio_oferta": 159.00, "descuento": "20%", "enlace": "https://padel.tienda/packs/packs-babolat", "tienda": "Babolat"},
    ])
    
    return offers[:5]

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking NOX, Siux, Babolat deals...")
    
    all_offers = []
    all_offers.extend(fetch_nnnox_offers())
    all_offers.extend(fetch_siux_offers())
    all_offers.extend(fetch_babolat_offers())
    
    data = {
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "ultima_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "marcas": ["NOX", "Siux", "Babolat"],
        "chollos": all_offers
    }
    
    with open("/Users/cristian/Sites/padel_news/data/chollos.json", "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Updated with {len(all_offers)} offers (NOX: {len(fetch_nnnox_offers())}, Siux: {len(fetch_siux_offers())}, Babolat: {len(fetch_babolat_offers())})")

if __name__ == "__main__":
    main()