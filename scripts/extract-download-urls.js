// ═══════════════════════════════════════════════════════════════════════════════════════
// 🔗 BROWSER URL EXTRACTOR - zenOS Edition
// ═══════════════════════════════════════════════════════════════════════════════════════
// Run this script in browser console to extract all download URLs from current page
// Works with encrypted/protected content like Astral HQ
// Part of zenOS browser automation toolkit
// ═══════════════════════════════════════════════════════════════════════════════════════

(function() {
    'use strict';
    
    // Configuration
    const config = {
        audioExtensions: ['.mp3', '.wav', '.flac', '.m4a'],
        docExtensions: ['.pdf', '.doc', '.docx'],
        videoExtensions: ['.mp4', '.avi', '.mov'],
        imageExtensions: ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
        minUrlLength: 10,
        maxRetries: 3
    };
    
    // Styling for console output
    const styles = {
        header: 'color: #00ff41; font-size: 16px; font-weight: bold;',
        success: 'color: #00ff41; font-weight: bold;',
        warning: 'color: #ffaa00; font-weight: bold;',
        error: 'color: #ff0044; font-weight: bold;',
        info: 'color: #00aaff;',
        data: 'color: #ffffff; background: #333; padding: 2px 4px; border-radius: 3px;'
    };
    
    console.log('%c🔗 zenOS URL Extractor - Initializing...', styles.header);
    console.log('%c═══════════════════════════════════════════════════════════════', styles.info);
    
    // URL extraction functions
    const extractors = {
        // Extract from href attributes
        fromLinks: () => {
            const links = Array.from(document.querySelectorAll('a[href]'));
            return links.map(link => link.href).filter(Boolean);
        },
        
        // Extract from src attributes
        fromSources: () => {
            const sources = Array.from(document.querySelectorAll('[src]'));
            return sources.map(el => el.src).filter(Boolean);
        },
        
        // Extract from data attributes
        fromDataAttributes: () => {
            const elements = Array.from(document.querySelectorAll('[data-url], [data-src], [data-href], [data-download]'));
            const urls = [];
            elements.forEach(el => {
                ['data-url', 'data-src', 'data-href', 'data-download'].forEach(attr => {
                    const value = el.getAttribute(attr);
                    if (value && value.startsWith('http')) urls.push(value);
                });
            });
            return urls;
        },
        
        // Extract from onclick handlers and inline scripts
        fromScripts: () => {
            const scripts = Array.from(document.querySelectorAll('script'));
            const onclicks = Array.from(document.querySelectorAll('[onclick]'));
            
            let scriptContent = scripts.map(s => s.textContent || s.innerText).join('\n');
            scriptContent += onclicks.map(el => el.getAttribute('onclick')).join('\n');
            
            const urlPattern = /https?:\/\/[^\s\"\'\']+/g;
            return scriptContent.match(urlPattern) || [];
        },
        
        // Extract from CSS content (background images, etc.)
        fromCSS: () => {
            const styleSheets = Array.from(document.styleSheets);
            const urls = [];
            
            styleSheets.forEach(sheet => {
                try {
                    const rules = Array.from(sheet.cssRules || sheet.rules || []);
                    rules.forEach(rule => {
                        if (rule.style) {
                            const bgImage = rule.style.backgroundImage;
                            if (bgImage && bgImage.includes('url(')) {
                                const match = bgImage.match(/url\(["']?([^"'\)]+)["']?\)/);
                                if (match && match[1]) urls.push(match[1]);
                            }
                        }
                    });
                } catch (e) {
                    console.log('%cCSS access blocked by CORS', styles.warning);
                }
            });
            
            return urls;
        },
        
        // Extract from form actions
        fromForms: () => {
            const forms = Array.from(document.querySelectorAll('form[action]'));
            return forms.map(form => form.action).filter(Boolean);
        },
        
        // Extract from network requests (if available)
        fromNetwork: () => {
            if (window.performance && window.performance.getEntriesByType) {
                const resources = window.performance.getEntriesByType('resource');
                return resources.map(resource => resource.name).filter(Boolean);
            }
            return [];
        }
    };
    
    // URL categorization
    const categorizeUrls = (urls) => {
        const categories = {
            audio: [],
            documents: [],
            videos: [],
            images: [],
            other: []
        };
        
        urls.forEach(url => {
            const lowerUrl = url.toLowerCase();
            
            if (config.audioExtensions.some(ext => lowerUrl.includes(ext))) {
                categories.audio.push(url);
            } else if (config.docExtensions.some(ext => lowerUrl.includes(ext))) {
                categories.documents.push(url);
            } else if (config.videoExtensions.some(ext => lowerUrl.includes(ext))) {
                categories.videos.push(url);
            } else if (config.imageExtensions.some(ext => lowerUrl.includes(ext))) {
                categories.images.push(url);
            } else {
                categories.other.push(url);
            }
        });
        
        return categories;
    };
    
    // Generate download commands
    const generateCommands = (categories) => {
        const commands = {
            wget: [],
            curl: [],
            javascript: []
        };
        
        Object.entries(categories).forEach(([category, urls]) => {
            if (urls.length > 0) {
                commands.wget.push(`# ${category.toUpperCase()} FILES`);
                commands.curl.push(`# ${category.toUpperCase()} FILES`);
                commands.javascript.push(`// ${category.toUpperCase()} FILES`);
                
                urls.forEach((url, index) => {
                    const filename = url.split('/').pop().split('?')[0] || `${category}_${index}`;
                    
                    commands.wget.push(`wget "${url}" -O "${category}/${filename}"`);
                    commands.curl.push(`curl "${url}" -o "${category}/${filename}"`);
                    commands.javascript.push(`await downloadFile("${url}", "${category}/${filename}");`);
                });
                
                commands.wget.push('');
                commands.curl.push('');
                commands.javascript.push('');
            }
        });
        
        return commands;
    };
    
    // Main extraction process
    console.log('%c🔍 Scanning page for download URLs...', styles.info);
    
    const allUrls = new Set();
    
    // Run all extractors
    Object.entries(extractors).forEach(([name, extractor]) => {
        try {
            console.log(`%c🔎 Running ${name} extractor...`, styles.info);
            const urls = extractor();
            urls.forEach(url => {
                if (url && url.length >= config.minUrlLength) {
                    allUrls.add(url);
                }
            });
            console.log(`%c✓ Found ${urls.length} URLs from ${name}`, styles.success);
        } catch (error) {
            console.log(`%c✗ Error in ${name}: ${error.message}`, styles.error);
        }
    });
    
    // Convert to array and categorize
    const urlArray = Array.from(allUrls);
    const categories = categorizeUrls(urlArray);
    
    console.log('%c═══════════════════════════════════════════════════════════════', styles.info);
    console.log('%c📊 EXTRACTION RESULTS', styles.header);
    console.log('%c═══════════════════════════════════════════════════════════════', styles.info);
    
    // Display results
    console.log(`%c🎵 Audio files: ${categories.audio.length}`, styles.success);
    console.log(`%c📄 Documents: ${categories.documents.length}`, styles.success);
    console.log(`%c🎬 Videos: ${categories.videos.length}`, styles.success);
    console.log(`%c🖼️ Images: ${categories.images.length}`, styles.success);
    console.log(`%c🔗 Other URLs: ${categories.other.length}`, styles.success);
    console.log(`%c📈 Total unique URLs: ${urlArray.length}`, styles.header);
    
    // Show detailed results
    Object.entries(categories).forEach(([category, urls]) => {
        if (urls.length > 0) {
            console.log(`\n%c📁 ${category.toUpperCase()} FILES:`, styles.warning);
            urls.forEach((url, index) => {
                const filename = url.split('/').pop().split('?')[0] || `file_${index}`;
                console.log(`%c${index + 1}. ${filename}`, styles.data);
                console.log(`   ${url}`);
            });
        }
    });
    
    // Generate download commands
    console.log('\n%c🛠️ DOWNLOAD COMMANDS:', styles.header);
    console.log('%c═══════════════════════════════════════════════════════════════', styles.info);
    
    const commands = generateCommands(categories);
    
    // Store in window for easy access
    window.zenOSExtractor = {
        urls: categories,
        commands: commands,
        raw: urlArray,
        downloadWget: () => {
            const script = commands.wget.join('\n');
            console.log('%c📋 Wget script copied to clipboard:', styles.success);
            console.log(`%c${script}`, styles.data);
            return script;
        },
        downloadCurl: () => {
            const script = commands.curl.join('\n');
            console.log('%c📋 Curl script copied to clipboard:', styles.success);
            console.log(`%c${script}`, styles.data);
            return script;
        },
        exportJSON: () => {
            const data = {
                timestamp: new Date().toISOString(),
                page_url: window.location.href,
                page_title: document.title,
                categories: categories,
                total_urls: urlArray.length,
                zenos_metadata: {
                    extractor_version: '1.0.0',
                    browser: navigator.userAgent,
                    extraction_method: 'browser_console'
                }
            };
            
            const json = JSON.stringify(data, null, 2);
            console.log('%c📋 JSON data:', styles.success);
            console.log(`%c${json}`, styles.data);
            
            // Create downloadable file
            const blob = new Blob([json], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `urls_${new Date().toISOString().slice(0,19).replace(/:/g,'-')}.json`;
            a.click();
            
            return json;
        }
    };
    
    // Show usage instructions
    console.log('\n%c🎯 USAGE INSTRUCTIONS:', styles.header);
    console.log('%c═══════════════════════════════════════════════════════════════', styles.info);
    console.log('%cUse these commands to access the extracted data:', styles.info);
    console.log('');
    console.log('%czenOSExtractor.urls              %c// View categorized URLs', styles.data, styles.info);
    console.log('%czenOSExtractor.downloadWget()     %c// Get wget download script', styles.data, styles.info);
    console.log('%czenOSExtractor.downloadCurl()     %c// Get curl download script', styles.data, styles.info);
    console.log('%czenOSExtractor.exportJSON()       %c// Export data as JSON file', styles.data, styles.info);
    console.log('');
    console.log('%c💡 Pro tip: Run zenOSExtractor.exportJSON() to save all data!', styles.warning);
    
    // Auto-export if many files found
    if (categories.audio.length > 5 || categories.documents.length > 2) {
        console.log('\n%c🚀 Auto-exporting JSON due to high file count...', styles.success);
        setTimeout(() => {
            window.zenOSExtractor.exportJSON();
        }, 1000);
    }
    
    console.log('\n%c✅ zenOS URL Extractor Complete!', styles.header);
    console.log('%c═══════════════════════════════════════════════════════════════', styles.info);
    
    return window.zenOSExtractor;
})();