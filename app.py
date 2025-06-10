<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Collective Agreement Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
        }

        .header h1 {
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .header p {
            color: #7f8c8d;
            font-size: 1.2em;
        }

        .upload-section {
            background: #f8f9fa;
            border: 2px dashed #dee2e6;
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            margin-bottom: 30px;
            transition: all 0.3s ease;
        }

        .upload-section.dragover {
            border-color: #667eea;
            background: rgba(102, 126, 234, 0.1);
        }

        .file-input {
            margin: 10px;
            padding: 10px 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.3s ease;
        }

        .file-input:hover {
            background: #5a67d8;
        }

        .status {
            margin: 20px 0;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
        }

        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }

        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }

        .query-section {
            margin-bottom: 30px;
        }

        .query-input {
            width: 100%;
            padding: 15px;
            border: 2px solid #e1e5e9;
            border-radius: 10px;
            font-size: 16px;
            resize: vertical;
            min-height: 100px;
            font-family: inherit;
            transition: border-color 0.3s ease;
        }

        .query-input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .search-button {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 15px;
            transition: transform 0.2s ease;
        }

        .search-button:hover {
            transform: translateY(-2px);
        }

        .search-button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .results {
            background: #fff;
            border: 1px solid #e1e5e9;
            border-radius: 15px;
            padding: 25px;
            margin-top: 20px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
        }

        .results h3 {
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.5em;
        }

        .article {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            transition: transform 0.2s ease;
        }

        .article:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }

        .article-header {
            display: flex;
            justify-content: between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #dee2e6;
        }

        .article-number {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 14px;
        }

        .article-source {
            background: #6c757d;
            color: white;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 12px;
            margin-left: 10px;
        }

        .article-title {
            font-size: 1.3em;
            font-weight: bold;
            color: #2c3e50;
            flex-grow: 1;
            margin-left: 15px;
        }

        .article-content {
            line-height: 1.6;
            color: #495057;
        }

        .subsection {
            margin: 15px 0;
            padding-left: 20px;
        }

        .subsection-label {
            font-weight: bold;
            color: #667eea;
            margin-bottom: 8px;
        }

        .subsection-content {
            margin-left: 15px;
            line-height: 1.6;
        }

        .no-results {
            text-align: center;
            color: #6c757d;
            font-style: italic;
            padding: 40px;
        }

        .loading {
            text-align: center;
            padding: 40px;
            color: #667eea;
        }

        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .debug-info {
            background: #e9ecef;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
            font-family: monospace;
            font-size: 14px;
            color: #495057;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Collective Agreement Assistant</h1>
            <p>Direct JSON search - no indexing required</p>
        </div>

        <div class="upload-section" id="uploadSection">
            <h3>Upload Agreement Files</h3>
            <p>Upload your Local and Common Agreement JSON files</p>
            <div>
                <label for="localFile" class="file-input">Local Agreement JSON</label>
                <input type="file" id="localFile" accept=".json" style="display: none;">
                
                <label for="commonFile" class="file-input">Common Agreement JSON</label>
                <input type="file" id="commonFile" accept=".json" style="display: none;">
            </div>
        </div>

        <div id="status"></div>

        <div class="query-section">
            <textarea 
                id="queryInput" 
                class="query-input" 
                placeholder="Enter your question about the collective agreements (e.g., 'What is the vacation carryover limit?' or 'Show me Article 17.8')"
                disabled
            ></textarea>
            <button id="searchButton" class="search-button" disabled>Search Agreements</button>
        </div>

        <div id="results"></div>
    </div>

    <script>
        class CollectiveAgreementAssistant {
            constructor() {
                this.localAgreement = null;
                this.commonAgreement = null;
                this.setupEventListeners();
            }

            setupEventListeners() {
                document.getElementById('localFile').addEventListener('change', (e) => this.handleFileUpload(e, 'local'));
                document.getElementById('commonFile').addEventListener('change', (e) => this.handleFileUpload(e, 'common'));
                document.getElementById('searchButton').addEventListener('click', () => this.performSearch());
                document.getElementById('queryInput').addEventListener('keypress', (e) => {
                    if (e.key === 'Enter' && e.ctrlKey) {
                        this.performSearch();
                    }
                });

                // Drag and drop
                const uploadSection = document.getElementById('uploadSection');
                uploadSection.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    uploadSection.classList.add('dragover');
                });
                uploadSection.addEventListener('dragleave', () => {
                    uploadSection.classList.remove('dragover');
                });
                uploadSection.addEventListener('drop', (e) => {
                    e.preventDefault();
                    uploadSection.classList.remove('dragover');
                    this.handleDroppedFiles(e.dataTransfer.files);
                });
            }

            async handleFileUpload(event, type) {
                const file = event.target.files[0];
                if (!file) return;

                try {
                    const text = await file.text();
                    const data = JSON.parse(text);
                    
                    if (type === 'local') {
                        this.localAgreement = data;
                        this.showStatus(`Local Agreement loaded (${Object.keys(data).length} articles)`, 'success');
                    } else {
                        this.commonAgreement = data;
                        this.showStatus(`Common Agreement loaded (${Object.keys(data).length} articles)`, 'success');
                    }

                    this.checkReadyState();
                } catch (error) {
                    this.showStatus(`Error loading ${type} agreement: ${error.message}`, 'error');
                }
            }

            handleDroppedFiles(files) {
                Array.from(files).forEach(file => {
                    if (file.name.toLowerCase().includes('local')) {
                        this.handleFileUpload({target: {files: [file]}}, 'local');
                    } else if (file.name.toLowerCase().includes('common')) {
                        this.handleFileUpload({target: {files: [file]}}, 'common');
                    }
                });
            }

            checkReadyState() {
                const ready = this.localAgreement && this.commonAgreement;
                document.getElementById('queryInput').disabled = !ready;
                document.getElementById('searchButton').disabled = !ready;
                
                if (ready) {
                    this.showStatus('Both agreements loaded. Ready to search!', 'success');
                }
            }

            showStatus(message, type) {
                const status = document.getElementById('status');
                status.innerHTML = `<div class="status ${type}">${message}</div>`;
            }

            extractKeywords(query) {
                // Extract article numbers (e.g., "17.8", "Article 17.8")
                const articleMatches = query.match(/(?:article\s+)?(\d+(?:\.\d+)?)/gi);
                const articleNumbers = articleMatches ? articleMatches.map(match => 
                    match.replace(/article\s+/i, '').trim()
                ) : [];

                // Extract key terms
                const words = query.toLowerCase()
                    .replace(/[^\w\s\.]/g, ' ')
                    .split(/\s+/)
                    .filter(word => word.length > 2)
                    .filter(word => !['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 'did', 'did', 'she', 'use', 'her', 'now', 'him', 'way'].includes(word));

                return {
                    articleNumbers,
                    terms: words,
                    originalQuery: query.toLowerCase()
                };
            }

            scoreArticleRelevance(article, keywords, articleNumber) {
                let score = 0;
                const content = this.getArticleText(article).toLowerCase();
                const title = (article.title || '').toLowerCase();

                // Exact article number match (highest priority)
                if (keywords.articleNumbers.includes(articleNumber)) {
                    score += 1000;
                }

                // Title matches
                keywords.terms.forEach(term => {
                    if (title.includes(term)) {
                        score += 50;
                    }
                    const termCount = (content.match(new RegExp(term, 'g')) || []).length;
                    score += termCount * 10;
                });

                // Phrase matching
                if (content.includes(keywords.originalQuery)) {
                    score += 100;
                }

                return score;
            }

            getArticleText(article) {
                let text = article.title || '';
                
                if (typeof article.content === 'string') {
                    text += ' ' + article.content;
                }
                
                if (article.sections) {
                    Object.values(article.sections).forEach(section => {
                        if (typeof section === 'string') {
                            text += ' ' + section;
                        } else if (section.content) {
                            text += ' ' + section.content;
                        }
                        if (section.subsections) {
                            Object.values(section.subsections).forEach(subsection => {
                                text += ' ' + subsection;
                            });
                        }
                    });
                }
                
                // Handle direct subsections (like Article 17.8)
                if (article.subsections) {
                    Object.values(article.subsections).forEach(subsection => {
                        text += ' ' + subsection;
                    });
                }
                
                return text;
            }

            findRelevantArticles(query) {
                const keywords = this.extractKeywords(query);
                const results = [];

                // Search local agreement
                if (this.localAgreement) {
                    Object.entries(this.localAgreement).forEach(([articleNum, article]) => {
                        const score = this.scoreArticleRelevance(article, keywords, articleNum);
                        if (score > 0) {
                            results.push({
                                source: 'Local Agreement',
                                number: articleNum,
                                article: article,
                                score: score
                            });
                        }
                    });
                }

                // Search common agreement
                if (this.commonAgreement) {
                    Object.entries(this.commonAgreement).forEach(([articleNum, article]) => {
                        const score = this.scoreArticleRelevance(article, keywords, articleNum);
                        if (score > 0) {
                            results.push({
                                source: 'Common Agreement',
                                number: articleNum,
                                article: article,
                                score: score
                            });
                        }
                    });
                }

                // Sort by relevance score (highest first)
                results.sort((a, b) => b.score - a.score);

                // If no specific matches, return top 5 most relevant
                // If specific article requested, return top 10
                const limit = keywords.articleNumbers.length > 0 ? 10 : 5;
                return results.slice(0, limit);
            }

            renderArticle(result) {
                const { source, number, article } = result;
                let html = `
                    <div class="article">
                        <div class="article-header">
                            <span class="article-number">Article ${number}</span>
                            <span class="article-source">${source}</span>
                            <span class="article-title">${article.title || 'Untitled'}</span>
                        </div>
                        <div class="article-content">
                `;

                // Handle direct content
                if (typeof article.content === 'string') {
                    html += `<p>${article.content}</p>`;
                }

                // Handle direct subsections (like Article 17.8)
                if (article.subsections) {
                    Object.entries(article.subsections).forEach(([key, content]) => {
                        html += `
                            <div class="subsection">
                                <div class="subsection-label">(${key})</div>
                                <div class="subsection-content">${content}</div>
                            </div>
                        `;
                    });
                }

                // Handle sections with subsections
                if (article.sections) {
                    Object.entries(article.sections).forEach(([sectionKey, section]) => {
                        if (typeof section === 'string') {
                            html += `<p><strong>Section ${sectionKey}:</strong> ${section}</p>`;
                        } else {
                            if (section.title) {
                                html += `<h4>Section ${sectionKey}: ${section.title}</h4>`;
                            }
                            if (section.content) {
                                html += `<p>${section.content}</p>`;
                            }
                            if (section.subsections) {
                                Object.entries(section.subsections).forEach(([subKey, subContent]) => {
                                    html += `
                                        <div class="subsection">
                                            <div class="subsection-label">(${subKey})</div>
                                            <div class="subsection-content">${subContent}</div>
                                        </div>
                                    `;
                                });
                            }
                        }
                    });
                }

                html += `
                        </div>
                    </div>
                `;

                return html;
            }

            async performSearch() {
                const query = document.getElementById('queryInput').value.trim();
                if (!query) {
                    this.showStatus('Please enter a search query', 'error');
                    return;
                }

                const resultsDiv = document.getElementById('results');
                resultsDiv.innerHTML = `
                    <div class="loading">
                        <div class="spinner"></div>
                        <p>Searching agreements...</p>
                    </div>
                `;

                try {
                    const relevantArticles = this.findRelevantArticles(query);
                    
                    if (relevantArticles.length === 0) {
                        resultsDiv.innerHTML = `
                            <div class="results">
                                <div class="no-results">
                                    No relevant articles found for your query. Try different keywords or check your spelling.
                                </div>
                            </div>
                        `;
                        return;
                    }

                    let html = `
                        <div class="results">
                            <h3>Search Results (${relevantArticles.length} articles found)</h3>
                    `;

                    relevantArticles.forEach(result => {
                        html += this.renderArticle(result);
                    });

                    html += `
                            <div class="debug-info">
                                <strong>Search processed:</strong> Found ${relevantArticles.length} relevant articles<br>
                                <strong>Keywords extracted:</strong> ${this.extractKeywords(query).terms.join(', ')}<br>
                                <strong>Article numbers:</strong> ${this.extractKeywords(query).articleNumbers.join(', ') || 'None'}
                            </div>
                        </div>
                    `;

                    resultsDiv.innerHTML = html;
                } catch (error) {
                    resultsDiv.innerHTML = `
                        <div class="results">
                            <div class="status error">
                                Error performing search: ${error.message}
                            </div>
                        </div>
                    `;
                }
            }
        }

        // Initialize the application
        document.addEventListener('DOMContentLoaded', () => {
            new CollectiveAgreementAssistant();
        });
    </script>
</body>
</html>
