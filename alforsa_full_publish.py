"""
alforsa_full_publish.py
One-file generator + publisher for Alforsa (EN + AR), with SEO, JSON-LD, sitemap, google verification,
and automatic GitHub repo + Pages activation.

USAGE:
1) Save this file.
2) Run: python alforsa_full_publish.py
3) Enter your GitHub username and personal access token when prompted.
4) Follow printed next steps (Google Search Console, Google Business Profile, domain DNS).

SECURITY: After you finish, revoke the token in GitHub (https://github.com/settings/tokens).
"""

import os
import json
import datetime
import pathlib
import zipfile
import requests
import getpass
import sys
from git import Repo, GitCommandError

# ---------------- USER CONFIG (edit if you want to customise defaults) ----------------
BUSINESS = {
    "name_en": "Alforsa Ice Cream Machines",
    "name_ar": "الفرصة لمكائن الآيس كريم",
    "phone": "+966509995448",
    "main_url": "https://alforsa.sa/",  # your domain if already owned; used in metadata
    "description_en": "Supplier of soft serve ice cream machines, slush machines, spare parts and maintenance in Saudi Arabia and worldwide.",
    "description_ar": "مورد ماكينات الآيس كريم السوفتر، ماكينات سلاش، قطع غيار وصيانة في السعودية وحول العالم.",
    "streetAddress": "Riyadh, Saudi Arabia",
    "currency": "SAR"
}

# Keywords and pages we'll create (EN + AR)
PAGES = [
    {"slug": "soft-serve-ice-cream-machine", "title_en": "Soft Serve Ice Cream Machine", "title_ar": "ماكينة آيس كريم سوفت سيرف"},
    {"slug": "alforsa-ice-cream-machine", "title_en": "Alforsa Ice Cream Machine", "title_ar": "ماكينة آيس كريم الفرصة"},
    {"slug": "slush-machine", "title_en": "Slush Machine", "title_ar": "ماكينة سلاش"},
    {"slug": "3-burner-slush-machine", "title_en": "3 Burner Slush Machine", "title_ar": "ماكينة سلاش بثلاث شعلات"},
    {"slug": "spare-parts", "title_en": "Spare Parts", "title_ar": "قطع غيار"},
    {"slug": "maintenance", "title_en": "Maintenance & Service", "title_ar": "الصيانة والخدمة"}
]

OUTPUT_DIR = pathlib.Path("alforsa_site")  # folder created by script
REPO_NAME = "alforsa"  # github repo name to create/push
# --------------------------------------------------------------------------------------

def ensure_dirs():
    OUTPUT_DIR.mkdir(exist_ok=True)
    (OUTPUT_DIR / "en").mkdir(exist_ok=True)
    (OUTPUT_DIR / "ar").mkdir(exist_ok=True)

def make_html_page(title, description, canonical, body_html, lang="en", hreflang_links=None):
    # hreflang_links: list of tuples (href, hreflang)
    og_title = title
    og_desc = description
    hreflang_tags = ""
    if hreflang_links:
        for href, hl in hreflang_links:
            hreflang_tags += f'<link rel="alternate" href="{href}" hreflang="{hl}">\n    '
    head = f"""<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <meta name="keywords" content="Alforsa, الفرصة, ice cream machine, soft serve, slush, slush machine, spare parts, maintenance, 3 burner slush">
  <link rel="canonical" href="{canonical}">
  {hreflang_tags}
  <meta property="og:site_name" content="{BUSINESS['name_en']}">
  <meta property="og:title" content="{og_title}">
  <meta property="og:description" content="{og_desc}">
  <meta property="og:url" content="{canonical}">
  <meta name="twitter:card" content="summary_large_image">
  <style>body{{font-family:Arial,Helvetica,sans-serif;max-width:960px;margin:20px auto;padding:0 16px;line-height:1.5}} header h1{{font-size:1.6rem}} footer{{margin-top:40px;color:#444}}</style>
</head>
<body>
<header>
  <h1>{BUSINESS['name_en']} — {BUSINESS['name_ar']}</h1>
  <p>{BUSINESS['description_en']}</p>
  <p><strong>Phone:</strong> <a href="tel:{BUSINESS['phone']}">{BUSINESS['phone']}</a> | <strong>Website:</strong> <a href="{BUSINESS['main_url']}">{BUSINESS['main_url']}</a></p>
  <hr>
</header>
<main>
{body_html}
</main>
<footer>
  <p>{BUSINESS['name_en']} — {BUSINESS['name_ar']}</p>
  <p>Address: {BUSINESS['streetAddress']}</p>
  <p>Phone: <a href="tel:{BUSINESS['phone']}">{BUSINESS['phone']}</a> | Website: <a href="{BUSINESS['main_url']}">{BUSINESS['main_url']}</a></p>
  <small>© {datetime.datetime.utcnow().year} {BUSINESS['name_en']}</small>
</footer>
</body>
</html>
"""
    return head

def build_site_and_assets():
    ensure_dirs()

    # Create bilingual home pages (EN at /en/index.html and AR at /ar/index.html) plus root index that redirects to /en/
    en_home_body = "<h2>Products & Services</h2><ul>"
    ar_home_body = "<h2>المنتجات والخدمات</h2><ul>"
    hreflangs = []
    # prepare page files
    for p in PAGES:
        # english page
        en_body = f"<h2>{p['title_en']}</h2>\n<p>{p['title_en']} — {BUSINESS['description_en']}</p>\n<ul><li>High performance machines</li><li>Genuine spare parts</li><li>Maintenance & service</li></ul>"
        en_canon = BUSINESS['main_url'].rstrip("/") + "/en/" + p['slug'] + ".html"
        en_html = make_html_page(p['title_en'] + " — " + BUSINESS['name_en'], en_body, en_canon, en_body, lang="en")
        (OUTPUT_DIR / "en" / (p['slug'] + ".html")).write_text(en_html, encoding="utf-8")

        # arabic page
        ar_body = f"<h2>{p['title_ar']}</h2>\n<p>{p['title_ar']} — {BUSINESS['description_ar']}</p>\n<ul><li>أداء عالي</li><li>قطع غيار أصلية</li><li>خدمات وصيانة</li></ul>"
        ar_canon = BUSINESS['main_url'].rstrip("/") + "/ar/" + p['slug'] + ".html"
        ar_html = make_html_page(p['title_ar'] + " — " + BUSINESS['name_en'], ar_body, ar_canon, ar_body, lang="ar")
        (OUTPUT_DIR / "ar" / (p['slug'] + ".html")).write_text(ar_html, encoding="utf-8")

        # Add to home lists
        en_home_body += f'<li><a href="/en/{p["slug"]}.html">{p["title_en"]} — {p["title_ar"]}</a></li>\n'
        ar_home_body += f'<li><a href="/ar/{p["slug"]}.html">{p["title_ar"]} — {p["title_en"]}</a></li>\n'

    en_home_body += "</ul>\n<p>Contact us: <a href='tel:{0}'>{0}</a></p>".format(BUSINESS["phone"])
    ar_home_body += "</ul>\n<p>اتصل بنا: <a href='tel:{0}'>{0}</a></p>".format(BUSINESS["phone"])

    # EN home page
    en_index_canon = BUSINESS['main_url'].rstrip("/") + "/en/index.html"
    en_index_html = make_html_page(BUSINESS['name_en'] + " — Home", BUSINESS['description_en'], en_index_canon, en_home_body, lang="en")
    (OUTPUT_DIR / "en" / "index.html").write_text(en_index_html, encoding="utf-8")

    # AR home page
    ar_index_canon = BUSINESS['main_url'].rstrip("/") + "/ar/index.html"
    ar_index_html = make_html_page(BUSINESS['name_ar'] + " — الصفحة الرئيسية", BUSINESS['description_ar'], ar_index_canon, ar_home_body, lang="ar")
    (OUTPUT_DIR / "ar" / "index.html").write_text(ar_index_html, encoding="utf-8")

    # Root index: simple language selector and links to en/ and ar/
    root_body = f"""
<h2>Welcome / مرحباً</h2>
<p><a href="/en/index.html">English site — English</a></p>
<p><a href="/ar/index.html">الموقع باللغة العربية — Arabic</a></p>
<p>Or visit the official site: <a href="{BUSINESS['main_url']}">{BUSINESS['main_url']}</a></p>
"""
    root_html = make_html_page(BUSINESS['name_en'] + " — Landing", BUSINESS['description_en'], BUSINESS['main_url'], root_body, lang="en",
                               hreflang_links=[(BUSINESS['main_url'].rstrip("/") + "/en/index.html", "en"), (BUSINESS['main_url'].rstrip("/") + "/ar/index.html", "ar")])
    (OUTPUT_DIR / "index.html").write_text(root_html, encoding="utf-8")

    # Create sitemap.xml referencing /en/ and /ar/
    today = datetime.date.today().isoformat()
    base = BUSINESS['main_url'].rstrip("/")
    urls = [base + "/index.html", base + "/en/index.html", base + "/ar/index.html"]
    for p in PAGES:
        urls.append(base + "/en/" + p["slug"] + ".html")
        urls.append(base + "/ar/" + p["slug"] + ".html")
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sitemap.append("  <url>")
        sitemap.append(f"    <loc>{u}</loc>")
        sitemap.append(f"    <lastmod>{today}</lastmod>")
        sitemap.append("  </url>")
    sitemap.append("</urlset>")
    (OUTPUT_DIR / "sitemap.xml").write_text("\n".join(sitemap), encoding="utf-8")

    # robots.txt
    robots_txt = f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n"
    (OUTPUT_DIR / "robots.txt").write_text(robots_txt, encoding="utf-8")

    # JSON-LD LocalBusiness (single file to reference in pages if desired)
    ld = {
      "@context": "https://schema.org",
      "@type": "LocalBusiness",
      "name": BUSINESS["name_en"],
      "alternateName": BUSINESS["name_ar"],
      "url": BUSINESS["main_url"],
      "telephone": BUSINESS["phone"],
      "address": {
        "@type": "PostalAddress",
        "streetAddress": BUSINESS["streetAddress"],
        "addressCountry": "SA"
      }
    }
    (OUTPUT_DIR / "schema_localbusiness.json").write_text(json.dumps(ld, ensure_ascii=False, indent=2), encoding="utf-8")

    # Example HTML verification file for Google Search Console (replace code string if Google gives different token)
    verification_filename = "google-site-verification-alforsa.html"
    verification_content = "<html><head><meta name='google-site-verification' content='replace_with_token'></head><body>Google site verification file for Alforsa</body></html>"
    (OUTPUT_DIR / verification_filename).write_text(verification_content, encoding="utf-8")

    # CNAME (if you will use alforsa.sa as a custom domain on GitHub Pages)
    (OUTPUT_DIR / "CNAME").write_text("alforsa.sa\n", encoding="utf-8")

    # Zip package for offline upload
    zipname = "alforsa_site.zip"
    with zipfile.ZipFile(zipname, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(OUTPUT_DIR):
            for f in files:
                fp = os.path.join(root, f)
                arc = os.path.relpath(fp, OUTPUT_DIR)
                z.write(fp, arc)
    print(f"✅ Built site in '{OUTPUT_DIR.resolve()}', and packaged as {zipname}")

def create_github_repo(username, token):
    url = "https://api.github.com/user/repos"
    data = {"name": REPO_NAME, "private": False, "has_pages": True}
    r = requests.post(url, auth=(username, token), json=data)
    if r.status_code == 201:
        print("✅ GitHub repository created.")
    elif r.status_code == 422:
        print("⚠️ Repo may already exist (HTTP 422). Will continue and try to push to it.")
    else:
        print("❌ Failed to create repo via API. Response:", r.status_code, r.text)
        # Continue anyway — repo might exist

def push_site_to_github(username, token):
    """
    We'll push to GitHub but avoid storing the token in local config.
    The approach: create repo, then add a temporary remote with token in URL, push, then remove remote.
    WARNING: the token is only used at push time and not saved in files by this script.
    """
    repo_dir = str(OUTPUT_DIR.resolve())
    try:
        repo = Repo.init(repo_dir)
    except Exception as e:
        print("❌ Git init error:", e)
        return
    # add all files
    try:
        repo.git.add(A=True)
        repo.index.commit("Initial commit - Alforsa site")
    except Exception as e:
        print("⚠️ Commit warning:", e)

    # set temp remote with token in URL for push, then remove remote to avoid storing token
    remote_url_with_token = f"https://{username}:{token}@github.com/{username}/{REPO_NAME}.git"
    try:
        if "temp-origin" in [r.name for r in repo.remotes]:
            repo.delete_remote("temp-origin")
        temp = repo.create_remote("temp-origin", remote_url_with_token)
    except GitCommandError as e:
        print("⚠️ Could not create temporary remote — it may exist. Continuing...")
        temp = repo.remotes.temporigin if hasattr(repo.remotes, "temporigin") else repo.remotes[0]
    # push master/main whichever exists
    branch = "master"
    try:
        repo.remotes["temp-origin"].push(refspec=f"{branch}:{branch}", force=True)
    except Exception as e:
        # try main
        branch = "main"
        try:
            repo.remotes["temp-origin"].push(refspec=f"{branch}:{branch}", force=True)
        except Exception as e2:
            print("❌ Push failed. Error:", e2)
            print("Possible reasons: authentication failed, repo already exists with protected branches, or token scopes insufficient.")
            # remove temporary remote if exists
            try:
                repo.delete_remote("temp-origin")
            except Exception:
                pass
            return
    # remove temporary remote so token is not stored
    try:
        repo.delete_remote("temp-origin")
    except Exception:
        pass
    print(f"🚀 Files pushed to GitHub repository '{username}/{REPO_NAME}' (branch: {branch}).")

def enable_github_pages_api(username, token):
    # Try to enable Pages using GitHub API (best-effort)
    pages_url = f"https://api.github.com/repos/{username}/{REPO_NAME}/pages"
    payload = {"source": {"branch": "master", "path": "/"}}
    r = requests.post(pages_url, auth=(username, token), json=payload)
    # GitHub may return 201 or 204 or 409 depending on repo state
    if r.status_code in (201, 204):
        print("🌐 GitHub Pages enabled via API.")
    else:
        print("⚠️ GitHub Pages API response:", r.status_code, r.text)
    print(f"Your GitHub Pages URL (expected): https://{username}.github.io/{REPO_NAME}/")

def print_next_manual_steps(username):
    print("\n==== NEXT STEPS (copy/paste exact instructions) ====\n")
    print("1) Visit your GitHub Pages URL (it may take a minute to build):")
    print(f"   https://{username}.github.io/{REPO_NAME}/")
    print("\n2) Google Search Console verification (two common options):")
    print("   A) HTML file method:")
    print(f"      - Go to https://search.google.com/search-console/")
    print("      - Add property: 'https://{username}.github.io/{REPO_NAME}/' (URL prefix)")
    print(f"      - Choose 'HTML file' verification and upload the file named 'google-site-verification-alforsa.html' from the root of the site (it's inside the alforsa_site folder).")
    print("   B) Or choose 'Domain' and add the DNS TXT record at your domain provider (if you own alforsa.sa).")
    print("\n3) Google Business Profile (very important):")
    print("   - Go to https://business.google.com/ and sign in with a Google account.")
    print("   - Create a new business with the name EXACTLY: '{}'".format(BUSINESS["name_en"]))
    print("   - Fill in address (Riyadh, Saudi Arabia) and phone:", BUSINESS["phone"])
    print("   - Add website: your GitHub Pages URL or your custom domain.")
    print("   - Request verification (phone/postcard) and complete it.")
    print("\n4) If you own alforsa.sa and want to use it as custom domain (recommended):")
    print("   - In your domain DNS settings, create CNAME record:")
    print("       Host/Name: www")
    print("       Value/Target: {username}.github.io.")
    print("   - If you want root domain (alforsa.sa) to point to Pages, follow GitHub docs for A records -> https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site")
    print("   - Then, in your GitHub repo's Settings → Pages → set custom domain to 'alforsa.sa' and enable HTTPS.")
    print("\n5) Submit sitemap to Search Console:")
    print(f"   - In Search Console, go to Sitemaps and submit: https://{username}.github.io/{REPO_NAME}/sitemap.xml")
    print("\n6) Revoke the GitHub token if you don't need it anymore (recommended):")
    print("   - Go to https://github.com/settings/tokens and delete the token you used.")
    print("\n7) Add social profiles and link to your site:")
    print("   - Create Google Business Profile, Facebook Page, Instagram, YouTube channel, LinkedIn page.")
    print("   - Add the site URL to each profile and add photos, product descriptions and contact info.")
    print("\n8) Add detailed product pages: photos, specs, manuals, pricing and FAQs to improve indexing and authority.")
    print("\n9) For Arabic/English SEO best practice: ensure each page has proper <link rel='alternate' hreflang='en'/'ar'> to its counterpart (this script uses canonical links pointing to your domain).")
    print("\nIf anything failed during push (auth, API), see the printed errors above. You can also create the repo manually in GitHub and push the 'alforsa_site' folder using git commands.")

def main():
    print("=== Alforsa site builder & GitHub publisher ===")
    print("This script will create a bilingual site under the folder 'alforsa_site' and attempt to push it to GitHub.")
    build_site_and_assets()

    username = input("Enter your GitHub username: ").strip()
    token = getpass.getpass("Enter your GitHub personal access token (keeps it hidden): ").strip()
    if not username or not token:
        print("Username and token are required to push to GitHub. Exiting after local build. You can push manually later.")
        print(f"Local site is in: {OUTPUT_DIR.resolve()}")
        return

    print("\nCreating GitHub repo (if not exists) ...")
    create_github_repo(username, token)
    print("Pushing site to GitHub (temporary token used only for push) ...")
    push_site_to_github(username, token)
    print("Attempting to enable GitHub Pages via API (best-effort)...")
    enable_github_pages_api(username, token)
    print_next_manual_steps(username)
    print("\n✅ Done. Local files are in:", OUTPUT_DIR.resolve())

if __name__ == "__main__":
    main()
