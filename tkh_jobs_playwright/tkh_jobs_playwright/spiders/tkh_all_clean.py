# tkh_jobs_playwright/spiders/tkh_all.py

import scrapy
from scrapy_playwright.page import PageMethod
import re
from urllib.parse import urljoin

def clean_text(text):
    if not text:
        return "Not mentioned"
    # Usuwa nadmiarowe białe znaki, HTML tagów resztki i CSS klasy
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'<[^>]+>', '', text)  # usuwa ewentualne tagi które się przedostaną
    return text.strip()

class TkhAllSpider(scrapy.Spider):
    name = "tkh_all_clean"
    custom_settings = {
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 90000,
        "DEPTH_LIMIT": 1,
        "CONCURRENT_REQUESTS": 10,
        "DOWNLOAD_DELAY": 0,
        "FEED_FORMAT": "csv",
        "FEED_URI": "tkh_jobs.csv",
        "FEED_EXPORT_FIELDS": ["group","company","position","salary","url","work_mode","published","expires"],
    }

    start_urls = [
        # Smart Vision Systems
        "https://www.alliedvision.com/en/career/jobs/",
        "https://www.alphatronics.nl/nl/",
        "https://www.dewetron.com/about-us/career/#jobs",
        "https://www.euresys.com/en/careers/",
        "https://chromasens.de/en/company/careers/jobs",
        "https://mikrotron.de/en/company/mik-jobs.php",
        "https://net-gmbh.com/en/company/#karriere",
        "https://www.svs-vistek.com/en/company/svs-jobs.php",
        "https://tkhsecurity.com/careers/",
        "https://lmitechnologies.applytojob.com/",
        "https://liberty-robotics.com/careers/",
        "https://www.tattile.com/careers/",
        "https://www.tkhvision-italy.com/careers/",
        "https://www.commend.com/en/jobs/",
        "https://www.mextal.com/over-ons/werken-bij-mextal/",

        # Smart Manufacturing
        "https://pl.vmi-group.com/kariera/aktualne-oferty-pracy/",
        "https://careers-vmi.com/vacatures/",

        # Smart Connectivity
        "https://www.technospecials.be/nl/vacatures",
        "https://www.tkf.nl/en/about-tkf/working-at-tkf/job-vacancies#current-vacancies",
        "https://www.ccpartners.pl/kariera-w-c-c-partners",
        "https://ee-cables.com/en/jobs/",
        "https://www.intronics.nl/en-us/intronics-job-opportunities",
        "https://isolectra.nl/en/about-us/vacancies/",
        "https://www.texim-europe.com/jobs",
        "https://careers.tkh-airportsolutions.com/en/jobs",

        # Corporate
        "https://careers.tkh.ai/",
        "https://www.tkhlogistics.nl/?page_id=113",
    ]

    group_mapping = {
        "alliedvision.com": "Smart Vision Systems",
        "alphatronics.nl": "Smart Vision Systems",
        "dewetron.com": "Smart Vision Systems",
        "euresys.com": "Smart Vision Systems",
        "chromasens.de": "Smart Vision Systems",
        "mikrotron.de": "Smart Vision Systems",
        "net-gmbh.com": "Smart Vision Systems",
        "svs-vistek.*": "Smart Vision Systems",
        "tkhsecurity.com": "Smart Vision Systems",
        "lmitechnologies": "Smart Vision Systems",
        "liberty-robotics.com": "Smart Vision Systems",
        "tattile.com": "Smart Vision Systems",
        "tkhvision-italy.com": "Smart Vision Systems",
        "commend.com": "Smart Vision Systems",
        "mextal.com": "Smart Vision Systems",

        "vmi-group.com": "Smart Manufacturing Systems",
        "careers-vmi.com": "Smart Manufacturing Systems",

        "technospecials.be": "Smart Connectivity Systems",
        "tkf.nl": "Smart Connectivity Systems",
        "ccpartners.pl": "Smart Connectivity Systems",
        "ee-cables.com": "Smart Connectivity Systems",
        "intronics.nl": "Smart Connectivity Systems",
        "isolectra.nl": "Smart Connectivity Systems",
        "texim-europe.com": "Smart Connectivity Systems",
        "tkh-airportsolutions.com": "Smart Connectivity Systems",

        "tkh.ai": "Corporate",
        "tkhlogistics.nl": "Corporate",
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", "body", timeout=60000),
                    PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight)"),
                    PageMethod("wait_for_timeout", 4000),
                ]
            }, callback=self.parse_overview)

    async def parse_overview(self, response):
            page = response.meta["playwright_page"]
            await page.close()

            # === NOWY, MOCNY FILTR – usuwa wszystkie śmieci ===
            raw_links = response.css('a::attr(href)').getall()
            job_links = set()

            for raw_href in raw_links:
                if not raw_href:
                    continue
                href = raw_href.lower().strip()

                # 1. Blokujemy typowe śmieci od razu
                if any(bad in href for bad in [
                    "cookie", "privacy", "policy", "legal", "terms", "impressum",
                    "datenschutz", "consent", "gdpr", "preferences", "settings",
                    "linkedin", "xing", "facebook", "twitter", "youtube"
                ]):
                    continue

                # 2. Javascript i kotwice
                if href.startswith(("javascript:", "#")) or href == "/":
                    continue

                # 3. Pliki (CV template itp.)
                if href.endswith((".pdf", ".doc", ".docx", ".zip")):
                    continue

                # 4. Musi zawierać choć jedno dobre słowo kluczowe
                if not any(good in href for good in [
                    "job", "vacature", "stellen", "career", "apply", "position",
                    "offre", "praca", "solliciter", "/o/", "/job/", "/apply/", "/position/"
                ]):
                    continue

                full_url = urljoin(response.url, raw_href)
                job_links.add(full_url)

            # === Koniec filtra – teraz tylko prawdziwe oferty ===
            for url in job_links:
                yield scrapy.Request(url, callback=self.parse_job, meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [PageMethod("wait_for_timeout", 6000)]
                })

    async def parse_job(self, response):
        page = response.meta["playwright_page"]
        await page.close()

        # <<< KLUCZOWE – bierzemy tylko czysty tekst >>>
        # 1. Stanowisko – próbujemy po kolei najczęstsze selektory
        position = (
            response.css('h1::text').get(default="") or
            response.css('.job-title::text').get(default="") or
            response.css('[data-testid="hero-job-title"]::text').get(default="") or
            response.css('.position-title::text').get(default="") or
            "".join(response.css('h1 *::text, h2 *::text').getall())
        )
        position = clean_text(position)[:150]

        if len(position) < 6:
            position = "Not detected"

        # 2. Widełki – szukamy liczb z €, PLN, k, brutto itd.
        body_text = " ".join(response.css('body ::text').getall()).lower()
        salary_match = re.findall(r'€ ?\d{1,3}[,\.\d]*\s*(-|–|to|tot)\s*€ ?\d{1,3}[,\.\d]*|€ ?\d{1,3}[,\.\d]*|\d{1,3}[,\.\d]* ?(-|–) ?\d{1,3}[,\.\d]* ?(k|000|brutto|pln)', body_text)
        salary = " | ".join(set(salary_match)) if salary_match else "Not mentioned"

        # 3. Tryb pracy
        work_mode = "Not mentioned"
        lower = body_text
        if any(x in lower for x in ["remote", "zdalna", "volledig thuis", "home ?office", "from home"]):
            work_mode = "Remote" if "hybrid" not in lower else "Hybrid"
        elif "hybrid" in lower:
            work_mode = "Hybrid"
        elif any(x in lower for x in ["on.?site", "kantoor", "biuro", "vor ort"]):
            work_mode = "On-site"

        # 4. Daty
        published = response.css('meta[property="article:published_time"]::attr(content), time::text, .posted::text, .date-posted::text').get(default="")
        expires = response.css('.application-deadline::text, .closing-date::text, .expires::text').get(default="")

        # Grupa i firma
        domain = response.url.split("/")[2].replace("www.", "")
        group = next((g for d, g in self.group_mapping.items() if d in domain), "Other")
        company = domain.split(".")[0].replace("careers-", "").replace("apply-", "").title()

        if position != "Not detected":
            yield {
                "group": group,
                "company": company,
                "position": position,
                "salary": salary,
                "url": response.url,
                "work_mode": work_mode,
                "published": clean_text(published)[:20],
                "expires": clean_text(expires)[:20],
            }
