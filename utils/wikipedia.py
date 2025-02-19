import wikipediaapi
from utils.logging_config import logger

def getWikiSummary(artist_name, lang="ko"):

    user_agent = "Wikipedia-API Example (merlin@example.com)"
    wiki = wikipediaapi.Wikipedia(
        user_agent=user_agent, 
        language=lang,
        extract_format=wikipediaapi.ExtractFormat.WIKI)

    page = wiki.page(artist_name)
    
    if not page.exists() and lang == "ko":
        logger.warning(f"⚠️ '{artist_name}' 한국어 페이지 없음 → 영어로 검색")
        return getWikiSummary(artist_name, lang="en")
    
    if not page.exists():
        logger.warning(f"⚠️ '{artist_name}'에 대한 위키백과 페이지가 없음")
        return None
    
    return page.summary
