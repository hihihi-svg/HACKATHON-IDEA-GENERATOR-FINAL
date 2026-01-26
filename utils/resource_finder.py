import streamlit as st

def find_relevant_resources(query, top_n=5):
    """
    Generates relevant literature survey sources and resource links based on the query.
    Provides academic papers, documentation, datasets, and learning resources.
    """
    # Extract keywords from query
    keywords = query.lower()
    
    # Determine technology/domain category
    categories = {
        'ai': ['artificial intelligence', 'machine learning', 'deep learning', 'neural', 'ai'],
        'blockchain': ['blockchain', 'cryptocurrency', 'web3', 'smart contract', 'defi'],
        'iot': ['iot', 'internet of things', 'sensor', 'embedded', 'arduino', 'raspberry'],
        'web': ['web', 'frontend', 'backend', 'fullstack', 'api', 'rest'],
        'data': ['data science', 'analytics', 'visualization', 'big data', 'database'],
        'mobile': ['mobile', 'android', 'ios', 'app development', 'flutter', 'react native'],
        'cloud': ['cloud', 'aws', 'azure', 'gcp', 'devops', 'kubernetes'],
        'security': ['security', 'cybersecurity', 'encryption', 'privacy', 'authentication'],
        'health': ['healthcare', 'medical', 'health', 'telemedicine', 'diagnosis'],
        'sustainability': ['sustainability', 'green', 'climate', 'environment', 'energy']
    }
    
    # Detect primary category
    detected_category = 'general'
    for cat, terms in categories.items():
        if any(term in keywords for term in terms):
            detected_category = cat
            break
    
    resources = []
    
    # Base resource templates with real, useful sites
    resource_templates = {
        'academic': [
            {
                'name': 'Google Scholar',
                'url': f'https://scholar.google.com/scholar?q={query.replace(" ", "+")}',
                'description': f'Academic papers and research articles on {query}',
                'type': '📚 Research Papers'
            },
            {
                'name': 'arXiv.org',
                'url': f'https://arxiv.org/search/?query={query.replace(" ", "+")}&searchtype=all',
                'description': f'Latest preprints and research papers in {query}',
                'type': '📚 Research Papers'
            },
            {
                'name': 'IEEE Xplore',
                'url': f'https://ieeexplore.ieee.org/search/searchresult.jsp?queryText={query.replace(" ", "+")}',
                'description': f'IEEE technical literature on {query}',
                'type': '📚 Research Papers'
            }
        ],
        'documentation': [
            {
                'name': 'Medium Articles',
                'url': f'https://medium.com/search?q={query.replace(" ", "+")}',
                'description': f'Developer articles and tutorials on {query}',
                'type': '📖 Documentation'
            },
            {
                'name': 'Dev.to Community',
                'url': f'https://dev.to/search?q={query.replace(" ", "+")}',
                'description': f'Community tutorials and guides on {query}',
                'type': '📖 Documentation'
            }
        ],
        'datasets': [
            {
                'name': 'Kaggle Datasets',
                'url': f'https://www.kaggle.com/search?q={query.replace(" ", "+")}',
                'description': f'Datasets and competitions related to {query}',
                'type': '💾 Datasets'
            },
            {
                'name': 'UCI ML Repository',
                'url': 'https://archive.ics.uci.edu/ml/index.php',
                'description': f'Machine learning datasets for {query}',
                'type': '💾 Datasets'
            },
            {
                'name': 'Data.gov',
                'url': f'https://data.gov/search/?q={query.replace(" ", "+")}',
                'description': f'Government datasets related to {query}',
                'type': '💾 Datasets'
            }
        ],
        'learning': [
            {
                'name': 'YouTube Tutorials',
                'url': f'https://www.youtube.com/results?search_query={query.replace(" ", "+")}+tutorial',
                'description': f'Video tutorials and courses on {query}',
                'type': '🎓 Learning Resources'
            },
            {
                'name': 'Coursera',
                'url': f'https://www.coursera.org/search?query={query.replace(" ", "+")}',
                'description': f'Online courses on {query}',
                'type': '🎓 Learning Resources'
            }
        ],
        'code': [
            {
                'name': 'GitHub Topics',
                'url': f'https://github.com/topics/{query.replace(" ", "-").lower()}',
                'description': f'Open-source projects related to {query}',
                'type': '💻 Code Examples'
            },
            {
                'name': 'Stack Overflow',
                'url': f'https://stackoverflow.com/search?q={query.replace(" ", "+")}',
                'description': f'Q&A and solutions for {query}',
                'type': '💻 Code Examples'
            }
        ]
    }
    
    # Category-specific resources
    category_resources = {
        'ai': [
            {
                'name': 'Papers With Code',
                'url': f'https://paperswithcode.com/search?q_meta=&q_type=&q={query.replace(" ", "+")}',
                'description': f'ML papers with implementation code for {query}',
                'type': '🤖 AI/ML Resources'
            },
            {
                'name': 'Hugging Face',
                'url': f'https://huggingface.co/models?search={query.replace(" ", "+")}',
                'description': f'Pre-trained models and datasets for {query}',
                'type': '🤖 AI/ML Resources'
            }
        ],
        'blockchain': [
            {
                'name': 'Etherscan',
                'url': 'https://etherscan.io/',
                'description': 'Ethereum blockchain explorer and smart contracts',
                'type': '⛓️ Blockchain Resources'
            },
            {
                'name': 'CoinDesk Research',
                'url': f'https://www.coindesk.com/search?s={query.replace(" ", "+")}',
                'description': f'Blockchain research and articles on {query}',
                'type': '⛓️ Blockchain Resources'
            }
        ],
        'health': [
            {
                'name': 'PubMed',
                'url': f'https://pubmed.ncbi.nlm.nih.gov/?term={query.replace(" ", "+")}',
                'description': f'Medical research papers on {query}',
                'type': '🏥 Healthcare Resources'
            },
            {
                'name': 'WHO Database',
                'url': 'https://www.who.int/data',
                'description': 'Global health data and statistics',
                'type': '🏥 Healthcare Resources'
            }
        ],
        'iot': [
            {
                'name': 'Arduino Project Hub',
                'url': f'https://create.arduino.cc/projecthub/search?q={query.replace(" ", "+")}',
                'description': f'IoT projects and tutorials on {query}',
                'type': '🔌 IoT Resources'
            },
            {
                'name': 'Hackster.io',
                'url': f'https://www.hackster.io/search?q={query.replace(" ", "+")}',
                'description': f'Hardware projects related to {query}',
                'type': '🔌 IoT Resources'
            }
        ]
    }
    
    # Build balanced resource list (Variety over Quantity)
    
    # 1. Academic (Strictly 1)
    resources.extend(resource_templates['academic'][:1])
    
    # 2. Code / GitHub (Strictly 1)
    resources.extend(resource_templates['code'][:1])
    
    # 3. Documentation / Articles (Strictly 1)
    resources.extend(resource_templates['documentation'][:1])
    
    # 4. Category Specific (1, if available)
    if detected_category in category_resources:
        resources.extend(category_resources[detected_category][:1])
    
    # 5. Datasets (1)
    resources.extend(resource_templates['datasets'][:1])

    # Fill remaining slots if top_n > len(resources)
    if len(resources) < top_n:
        # Add a second academic paper if needed
        resources.extend(resource_templates['academic'][1:2])
    
    if len(resources) < top_n:
        # Add a second code resource or learning resource
        resources.extend(resource_templates['learning'][:1])

    return resources[:top_n]


def format_resource_card(resource):
    """
    Formats a resource as a nice display card.
    """
    return f"""
**{resource['type']}** - [{resource['name']}]({resource['url']})  
{resource['description']}
"""


# Backward compatibility - rename function to match old usage
def search_github_repos(query, top_n=5, token=None):
    """
    Wrapper function for backward compatibility.
    Now returns literature and resource links instead of GitHub repos.
    """
    return find_relevant_resources(query, top_n)