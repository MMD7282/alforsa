# scripts/generate_sitemap.py
import os
from datetime import datetime

base = "https://alforsa.sa"
# List your pages here (automate if you have many)
urls = [
    "/", "/en/", "/ar/",
    "/en/product-mini.html", "/ar/product-mini.html"
]

now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")
lines = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
for path in urls:
    en = path if path.startswith("/en/") else ("/en/" + path.lstrip("/")) if path == "/" else path.replace("/ar/", "/en/")
    ar = path if path.startswith("/ar/") else ("/ar/" + path.lstrip("/")) if path == "/" else path.replace("/en/", "/ar/")
    lines.append("  <url>")
    lines.append(f"    <loc>{base}{path}</loc>")
    lines.append(f"    <lastmod>{now}</lastmod>")
    lines.append("    <changefreq>weekly</changefreq>")
    lines.append("    <priority>0.8</priority>")
    lines.append(f'    <xhtml:link rel="alternate" hreflang="en" href="{base}{en}" />')
    lines.append(f'    <xhtml:link rel="alternate" hreflang="ar" href="{base}{ar}" />')
    lines.append("  </url>")
lines.append("</urlset>")

out_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public", "sitemap.xml")
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("sitemap.xml generated at", out_path)
 
