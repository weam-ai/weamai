def extract_text_by_page(doc,words_per_page=300):
    current_word_count = 0
    current_page_text = []
    page_texts = []

    for para in doc.paragraphs:
        words = para.text.split()
        current_word_count += len(words)
        current_page_text.append(para.text)

        if current_word_count >= words_per_page:
            page_texts.append('\n'.join(current_page_text))
            current_page_text = []
            current_word_count = 0

    # Add the remaining text as a last page if there's any
    if current_page_text:
        page_texts.append('\n'.join(current_page_text))

    return page_texts

def extract_text_by_page_from_string(text, words_per_page=300):
    words = text.split()
    page_texts = []
    current_page = []

    for word in words:
        current_page.append(word)
        if len(current_page) >= words_per_page:
            page_texts.append(' '.join(current_page))
            current_page = []

    # Add the remaining text as a last page if there's any
    if current_page:
        page_texts.append(' '.join(current_page))

    return page_texts
