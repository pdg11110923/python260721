import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}


def fetch_html(url):
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    return response.text


def clean_text(text):
    return " ".join(text.split())


def get_news_items(search_url, max_items=5):
    html = fetch_html(search_url)
    soup = BeautifulSoup(html, "html.parser")

    items = []
    seen = set()

    result_blocks = soup.select(
        'div.sds-comps-vertical-layout.sds-comps-full-layout.fds-news-item-list-desk'
    )

    for block in result_blocks:
        for card in block.select('div.sds-comps-vertical-layout.sds-comps-full-layout.ycsljrdBI8UnL49R'):
            title_link = card.select_one('a[data-heatmap-target=".tit"]')
            if not title_link:
                continue

            href = title_link.get("href", "").strip()
            if not href or href.startswith("javascript"):
                continue

            for hidden in title_link.select('span.fender-ui_0cb57fb2'):
                hidden.decompose()
            title = clean_text(title_link.get_text(" ", strip=True))

            body_link = card.select_one('a[data-heatmap-target=".body"]')
            summary = ""
            if body_link:
                for hidden in body_link.select('span.fender-ui_0cb57fb2'):
                    hidden.decompose()
                summary = clean_text(body_link.get_text(" ", strip=True))

            profile_link = card.select_one('a[data-heatmap-target=".prof"]')
            source = ""
            if profile_link:
                source = clean_text(profile_link.get_text(" ", strip=True))

            full_url = urljoin(search_url, href)
            if full_url not in seen:
                seen.add(full_url)
                items.append(
                    {
                        "title": title,
                        "link": full_url,
                        "source": source,
                        "summary": summary,
                    }
                )

    if not items:
        for a in soup.select('a[data-heatmap-target=".tit"]'):
            href = a.get("href", "").strip()
            if not href or href.startswith("javascript"):
                continue
            for hidden in a.select('span.fender-ui_0cb57fb2'):
                hidden.decompose()
            full_url = urljoin(search_url, href)
            title = clean_text(a.get_text(" ", strip=True))
            if full_url not in seen:
                seen.add(full_url)
                items.append({"title": title, "link": full_url, "source": "", "summary": ""})

    return items[:max_items]


def extract_article_text(article_url):
    html = fetch_html(article_url)
    soup = BeautifulSoup(html, "html.parser")

    selectors = [
        "article",
        "#dic_area",
        "#newsct_article",
        "#articleBodyContents",
        ".article_body",
        ".newsct_article",
        ".view_con",
        ".article-view",
    ]

    for selector in selectors:
        node = soup.select_one(selector)
        if node:
            text = "\n".join(
                line.strip() for line in node.get_text("\n").splitlines() if line.strip()
            )
            if len(text) > 100:
                return text

    body_text = soup.get_text("\n", strip=True)
    return body_text[:3000]


def main():
    query = "반도체"
    search_url = f"https://search.naver.com/search.naver?where=news&query={quote(query)}"

    print("검색 URL:", search_url)
    print("기사 제목과 링크를 찾는 중...")

    news_items = get_news_items(search_url, max_items=5)

    if not news_items:
        print("검색 결과에서 뉴스 링크를 찾지 못했습니다.")
        return

    for i, item in enumerate(news_items, 1):
        print(f"\n[{i}] {item['title']}")
        print("출처:", item['source'] or "-")
        print("링크:", item['link'])
        if item['summary']:
            print("요약:", item['summary'][:200])
        text = extract_article_text(item['link'])
        print("본문 미리보기:", text[:1000])
        print("-" * 80)


if __name__ == "__main__":
    main()
