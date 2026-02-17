(function() {
    'use strict';

    // State
    let currentInput = null;
    let selectedImage = null;
    let currentPage = 1;
    let currentCategory = '';
    let currentSearch = '';

    // Initialize
    document.addEventListener('DOMContentLoaded', function() {
        injectMediaButtons();
        createModal();
        
        // Observe DOM changes for dynamic formsets (inline admin)
        const observer = new MutationObserver(function(mutations) {
            injectMediaButtons();
        });
        observer.observe(document.body, { childList: true, subtree: true });
    });

    function injectMediaButtons() {
        // Find all file inputs that accept images
        const inputs = document.querySelectorAll('input[type="file"][accept*="image"]');
        inputs.forEach(input => {
            // Skip if already processed
            if (input.nextElementSibling && input.nextElementSibling.classList.contains('media-picker-btn')) return;
            
            // Create button
            const btn = document.createElement('span');
            btn.className = 'media-picker-btn';
            btn.innerHTML = '🖼️ 从素材库选择';
            btn.onclick = (e) => {
                e.preventDefault();
                openModal(input);
            };
            
            // Insert after input
            input.parentNode.insertBefore(btn, input.nextSibling);
        });
    }

    function createModal() {
        if (document.getElementById('mp-modal')) return;
        
        const html = `
        <div id="mp-modal" class="mp-modal">
            <div class="mp-content">
                <div class="mp-header">
                    <span class="mp-title">素材库</span>
                    <span class="mp-close" onclick="closeModal()">×</span>
                </div>
                <div class="mp-body">
                    <div class="mp-sidebar">
                        <button class="mp-cat-btn active" data-cat="" onclick="filterMedia('')">全部</button>
                        <button class="mp-cat-btn" data-cat="background" onclick="filterMedia('background')">背景</button>
                        <button class="mp-cat-btn" data-cat="icon" onclick="filterMedia('icon')">图标</button>
                        <button class="mp-cat-btn" data-cat="banner" onclick="filterMedia('banner')">横幅</button>
                        <button class="mp-cat-btn" data-cat="product" onclick="filterMedia('product')">商品</button>
                        <button class="mp-cat-btn" data-cat="other" onclick="filterMedia('other')">其他</button>
                    </div>
                    <div class="mp-main">
                        <div class="mp-search-bar">
                            <input type="text" class="mp-search-input" placeholder="搜索图片..." oninput="searchMedia(this.value)">
                        </div>
                        <div id="mp-grid" class="mp-grid"></div>
                        <div class="mp-pagination">
                            <button onclick="changePage(-1)">上一页</button>
                            <span id="mp-page-info">1</span>
                            <button onclick="changePage(1)">下一页</button>
                        </div>
                    </div>
                </div>
                <div class="mp-footer" style="padding:16px; border-top:1px solid #eee; text-align:right;">
                    <button onclick="confirmSelection()" style="padding:6px 20px; background:#1890ff; color:white; border:none; border-radius:4px; cursor:pointer;">确认选择</button>
                </div>
            </div>
        </div>
        `;
        document.body.insertAdjacentHTML('beforeend', html);
        
        // Expose global functions for onclick handlers
    window.closeModal = closeModal;
    window.filterMedia = filterMedia;
    window.searchMedia = searchMedia;
    window.changePage = changePage;
    window.confirmSelection = confirmSelection;
    window.selectItem = selectItem;
    // New: Expose openModal to allow external scripts to trigger it
    window.openMediaModal = (input) => {
        if (!input) return;
        openModal(input);
    };
    // New: Allow searching with predefined term
    window.setMediaSearch = (term) => {
        const input = document.querySelector('.mp-search-input');
        if (input) {
            input.value = term;
            searchMedia(term);
        }
    };
    }

    function openModal(input) {
        currentInput = input;
        document.getElementById('mp-modal').style.display = 'block';
        loadMedia();
    }

    function closeModal() {
        document.getElementById('mp-modal').style.display = 'none';
        selectedImage = null;
        currentInput = null;
    }

    function loadMedia() {
        fetch(`/api/media/?page=${currentPage}&category=${currentCategory}&search=${currentSearch}`)
            .then(res => res.json())
            .then(data => {
                const grid = document.getElementById('mp-grid');
                grid.innerHTML = '';
                data.results.forEach(item => {
                    const div = document.createElement('div');
                    div.className = 'mp-item';
                    div.dataset.id = item.id;
                    div.dataset.url = item.url; // Use original url for download
                    div.innerHTML = `<img src="${item.thumbnail_url || item.url}" loading="lazy" title="${item.name}">`;
                    div.onclick = () => selectItem(div, item);
                    grid.appendChild(div);
                });
                
                // Pagination info
                document.getElementById('mp-page-info').innerText = currentPage;
            });
    }

    function selectItem(el, item) {
        document.querySelectorAll('.mp-item').forEach(e => e.classList.remove('selected'));
        el.classList.add('selected');
        selectedImage = item;
    }

    async function confirmSelection() {
        if (!selectedImage || !currentInput) return;
        
        try {
            // Fetch the image as a blob
            const response = await fetch(selectedImage.url);
            const blob = await response.blob();
            
            // Create a File object
            // Get extension from url
            const ext = selectedImage.url.split('.').pop().split(/[?#]/)[0];
            const filename = selectedImage.name.endsWith('.' + ext) ? selectedImage.name : (selectedImage.name + '.' + ext);
            
            const file = new File([blob], filename, { type: blob.type });
            
            // Use DataTransfer to simulate file selection
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            currentInput.files = dataTransfer.files;
            
            // Trigger change event so Django Admin knows something changed (for previews etc)
            currentInput.dispatchEvent(new Event('change', { bubbles: true }));
            
            // Visual feedback
            const prevLabel = currentInput.parentNode.querySelector('.file-upload a');
            if (prevLabel) {
                prevLabel.innerText = "已选择: " + filename;
                prevLabel.href = selectedImage.url;
            } else {
                 // Try to find where to display selected file name
                 // Default django admin clearable file input style
            }
            
            closeModal();
            
        } catch (e) {
            console.error('Failed to process image selection', e);
            alert('选择图片失败，请重试');
        }
    }

    function filterMedia(cat) {
        currentCategory = cat;
        currentPage = 1;
        document.querySelectorAll('.mp-cat-btn').forEach(b => b.classList.remove('active'));
        document.querySelector(`.mp-cat-btn[data-cat="${cat}"]`).classList.add('active');
        loadMedia();
    }

    function searchMedia(val) {
        currentSearch = val;
        currentPage = 1;
        loadMedia();
    }

    function changePage(delta) {
        if (currentPage + delta < 1) return;
        currentPage += delta;
        loadMedia();
    }

})();
