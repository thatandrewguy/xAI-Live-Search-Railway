import requests
import markdown
from flask import Flask, render_template, request
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    xai_api_key = request.form.get('xai_api_key')
    search_term = request.form.get('search_term')
    enable_search = request.form.get('enable_search', 'auto')
    return_citations = request.form.get('return_citations', 'False')
    from_date = request.form.get('from_date')
    to_date = request.form.get('to_date')
    max_search_results = request.form.get('max_search_results')
    data_sources = request.form.getlist('data_source')
    country_web = request.form.get('country_web')
    country_news = request.form.get('country_news')
    web_filter_type = request.form.get('web_filter_type')
    web_filter_sites = request.form.get('web_filter_sites')
    news_filter_type = request.form.get('news_filter_type')
    news_filter_sites = request.form.get('news_filter_sites')
    x_handles = request.form.get('x_handles')
    rss_links = request.form.get('rss_links')
    safe_search_web = request.form.get('safe_search_web', 'True')
    safe_search_news = request.form.get('safe_search_news', 'True')

    if not search_term or not xai_api_key:
        return "Search term and XAI API Key are mandatory.", 400

    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {xai_api_key}"
    }

    payload = {
        "messages": [{"role": "user", "content": search_term}],
        "search_parameters": {"mode": enable_search.lower()},
        "model": "grok-3-latest"
    }

    if return_citations == 'True':
        payload['search_parameters']['return_citations'] = True
    else:
        payload['search_parameters']['return_citations'] = False

    if from_date:
        payload['search_parameters']['from_date'] = from_date
    if to_date:
        payload['search_parameters']['to_date'] = to_date

    if max_search_results:
        payload['search_parameters']['max_search_results'] = int(max_search_results)

    sources = []
    if not data_sources:
        data_sources = ['web', 'x']

    for source_type in data_sources:
        source = {"type": source_type}
        if source_type == 'web':
            if country_web:
                source['country'] = country_web
            if web_filter_type == 'excluded' and web_filter_sites:
                source['excluded_websites'] = [site.strip() for site in web_filter_sites.split(',')]
            elif web_filter_type == 'allowed' and web_filter_sites:
                source['allowed_websites'] = [site.strip() for site in web_filter_sites.split(',')]
            
            if safe_search_web == 'False':
                source['safe_search'] = False
            else:
                source['safe_search'] = True
        elif source_type == 'news':
            if country_news:
                source['country'] = country_news
            if news_filter_type == 'excluded' and news_filter_sites:
                source['excluded_websites'] = [site.strip() for site in news_filter_sites.split(',')]
            elif news_filter_type == 'allowed' and news_filter_sites:
                source['allowed_websites'] = [site.strip() for site in news_filter_sites.split(',')]
            
            if safe_search_news == 'False':
                source['safe_search'] = False
            else:
                source['safe_search'] = True
        elif source_type == 'rss':
            if rss_links:
                source['links'] = [link.strip() for link in rss_links.split(',')]
        elif source_type == 'x':
            if x_handles:
                source['x_handles'] = [handle.strip() for handle in x_handles.split(',')]
        sources.append(source)

    if sources:
        payload['search_parameters']['sources'] = sources

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        response_data = response.json()
        content = response_data.get('choices', [{}])[0].get('message', {}).get('content', 'No content found.')
        html_content = markdown.markdown(content)
        citations = response_data.get('citations', [])
        return render_template('result.html', content=html_content, citations=citations)
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}", 500
    except (KeyError, IndexError):
        return "Invalid response format from API.", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
