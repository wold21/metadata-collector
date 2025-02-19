from deep_translator import GoogleTranslator
from utils.logging_config import logger

def translate_to_korean(text):
    try:
        # 텍스트가 너무 길면 문장 단위로 나눠서 번역
        if len(text) > 1000:
            sentences = text.split('. ')
            translated_sentences = []
            translator = GoogleTranslator(source='auto', target='ko')
            
            for sentence in sentences:
                if sentence:
                    translated = translator.translate(sentence)
                    translated_sentences.append(translated)
            
            return '. '.join(translated_sentences)
        else:
            translator = GoogleTranslator(source='auto', target='ko')
            return translator.translate(text)
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        return text