def remove_dynamic_elements(page):
    page.evaluate("""
    () => {
        const selectors = [
            '[id*="cookie"]',
            '[class*="cookie"]',
            '[id*="popup"]',
            '[class*="popup"]',
            '[id*="modal"]',
            '[class*="modal"]',
            '[id*="chat"]',
            '[class*="chat"]',
            '[id*="advert"]',
            '[class*="advert"]',
            '[id*="banner"]',
            '[class*="banner"]',
            '[class*="newsletter"]',
            '[class*="subscribe"]',
            '[class*="gdpr"]',
            '[class*="consent"]',
            'iframe',
            'video'
        ];

        selectors.forEach(sel => {
            document.querySelectorAll(sel).forEach(el => el.remove());
        });

        document.querySelectorAll('*').forEach(el => {
            const style = window.getComputedStyle(el);
            if (style.position === 'fixed' || style.position === 'sticky') {
                el.remove();
            }
            el.style.animation = 'none';
            el.style.transition = 'none';
            el.style.scrollBehavior = 'auto';
        });
    }
    """)