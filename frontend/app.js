// Configuration
const API_BASE_URL = 'http://localhost:5000';

// DOM Elements
const tabBtns = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');
const imageInput = document.getElementById('imageInput');
const imageUploadBtn = document.getElementById('imageUploadBtn');
const uploadArea = document.getElementById('uploadArea');
const imagePreview = document.getElementById('imagePreview');
const previewImg = document.getElementById('previewImg');
const removeImageBtn = document.getElementById('removeImageBtn');
const generateFromImage = document.getElementById('generateFromImage');
const generateImageText = document.getElementById('generateImageText');
const imageSpinner = document.getElementById('imageSpinner');

const textBrief = document.getElementById('textBrief');
const charCount = document.getElementById('charCount');
const generateFromText = document.getElementById('generateFromText');
const generateTextText = document.getElementById('generateTextText');
const textSpinner = document.getElementById('textSpinner');

const resultsSection = document.getElementById('resultsSection');
const newGenerationBtn = document.getElementById('newGenerationBtn');
const contentTypeBadge = document.getElementById('contentTypeBadge');
const contentTypeText = document.getElementById('contentTypeText');
const captionsGrid = document.getElementById('captionsGrid');
const hashtagsGrid = document.getElementById('hashtagsGrid');
const postingTimeCard = document.getElementById('postingTimeCard');
const toast = document.getElementById('toast');
const toastMessage = document.getElementById('toastMessage');

// State
let selectedImage = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    checkServerHealth();
});

// Setup Event Listeners
function setupEventListeners() {
    // Tab switching
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });
    
    // Image upload
    imageUploadBtn.addEventListener('click', () => imageInput.click());
    imageInput.addEventListener('change', handleImageSelect);
    removeImageBtn.addEventListener('click', removeImage);
    
    // Drag and drop
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    // Generate buttons
    generateFromImage.addEventListener('click', generateCaptionsFromImage);
    generateFromText.addEventListener('click', generateCaptionsFromText);
    
    // Text input
    textBrief.addEventListener('input', updateCharCount);
    
    // New generation
    newGenerationBtn.addEventListener('click', resetForm);
}

// Tab switching
function switchTab(tabName) {
    tabBtns.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });
    
    tabContents.forEach(content => {
        content.classList.toggle('active', content.id === `${tabName}-tab`);
    });
}

// Check server health
async function checkServerHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (!response.ok) {
            showToast('Cannot connect to server. Please ensure the backend is running.', 'error');
        }
    } catch (error) {
        showToast('Cannot connect to server. Please start the backend on port 5000.', 'error');
    }
}

// Image handling
function handleImageSelect(e) {
    const file = e.target.files[0];
    if (file && file.type.startsWith('image/')) {
        selectedImage = file;
        displayImagePreview(file);
    } else {
        showToast('Please select a valid image file.', 'error');
    }
}

function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
        selectedImage = file;
        imageInput.files = e.dataTransfer.files;
        displayImagePreview(file);
    } else {
        showToast('Please select a valid image file.', 'error');
    }
}

function displayImagePreview(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImg.src = e.target.result;
        uploadArea.style.display = 'none';
        imagePreview.style.display = 'block';
        generateFromImage.style.display = 'block';
    };
    reader.readAsDataURL(file);
}

function removeImage() {
    selectedImage = null;
    imageInput.value = '';
    previewImg.src = '';
    uploadArea.style.display = 'block';
    imagePreview.style.display = 'none';
    generateFromImage.style.display = 'none';
}

// Text handling
function updateCharCount() {
    const count = textBrief.value.length;
    charCount.textContent = count;
    charCount.style.color = count > 950 ? 'var(--error-color)' : 'var(--text-secondary)';
}

// Generate captions from image
async function generateCaptionsFromImage() {
    if (!selectedImage) {
        showToast('Please select an image first.', 'error');
        return;
    }
    
    setLoadingState(true, 'image');
    
    const formData = new FormData();
    formData.append('file', selectedImage);
    
    try {
        const response = await fetch(`${API_BASE_URL}/generate/image`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayResults(data);
        } else {
            showToast(data.error || 'Failed to generate captions.', 'error');
        }
    } catch (error) {
        showToast('Error: ' + error.message, 'error');
    } finally {
        setLoadingState(false, 'image');
    }
}

// Generate captions from text
async function generateCaptionsFromText() {
    const text = textBrief.value.trim();
    
    if (!text || text.length < 10) {
        showToast('Please enter at least 10 characters.', 'error');
        return;
    }
    
    setLoadingState(true, 'text');
    
    try {
        const response = await fetch(`${API_BASE_URL}/generate/text`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text_brief: text })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayResults(data);
        } else {
            showToast(data.error || 'Failed to generate captions.', 'error');
        }
    } catch (error) {
        showToast('Error: ' + error.message, 'error');
    } finally {
        setLoadingState(false, 'text');
    }
}

// Display results
function displayResults(data) {
    // Update content type
    contentTypeText.textContent = data.content_type;
    
    // Display captions
    captionsGrid.innerHTML = '';
    data.captions.forEach((caption, index) => {
        const captionCard = createCaptionCard(caption, index);
        captionsGrid.appendChild(captionCard);
    });
    
    // Display hashtags
    hashtagsGrid.innerHTML = '';
    data.hashtag_sets.forEach((set, index) => {
        const hashtagCard = createHashtagCard(set, index);
        hashtagsGrid.appendChild(hashtagCard);
    });
    
    // Display posting time
    postingTimeCard.innerHTML = createPostingTimeContent(data.posting_time);
    
    // Show results section
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Create caption card
function createCaptionCard(caption, index) {
    const card = document.createElement('div');
    card.className = 'caption-card';
    card.innerHTML = `
        <span class="caption-tone">${caption.tone}</span>
        <div class="caption-text">${caption.caption}</div>
        <button class="copy-btn" onclick="copyToClipboard('${escapeHtml(caption.caption)}', 'Caption')">
            📋 Copy Caption
        </button>
    `;
    return card;
}

// Create hashtag card
function createHashtagCard(set, index) {
    const card = document.createElement('div');
    card.className = 'hashtag-card';
    
    const hashtagsText = set.hashtags.join(' ');
    
    card.innerHTML = `
        <span class="hashtag-category">${set.category}</span>
        <div class="hashtag-list">
            ${set.hashtags.map(tag => `<span class="hashtag-tag">${tag}</span>`).join('')}
        </div>
        <button class="copy-btn" onclick="copyToClipboard('${escapeHtml(hashtagsText)}', 'Hashtags')">
            📋 Copy All Hashtags
        </button>
    `;
    return card;
}

// Create posting time content
function createPostingTimeContent(postingTime) {
    return `
        <div class="time-info">
            <div class="time-icon">⏰</div>
            <div class="time-details">
                <h4>Best Time</h4>
                <div class="time-value">${postingTime.time}</div>
            </div>
        </div>
        <div class="time-info">
            <div class="time-icon">📅</div>
            <div class="time-details">
                <h4>Best Days</h4>
                <div class="time-value">${postingTime.day}</div>
            </div>
        </div>
        <div class="time-reason">
            <strong>Why?</strong> ${postingTime.reason}
        </div>
    `;
}

// Copy to clipboard
function copyToClipboard(text, type) {
    // Unescape HTML entities
    const textarea = document.createElement('textarea');
    textarea.innerHTML = text;
    const unescapedText = textarea.value;
    
    navigator.clipboard.writeText(unescapedText).then(() => {
        showToast(`${type} copied to clipboard! ✓`, 'success');
    }).catch(err => {
        showToast('Failed to copy. Please try again.', 'error');
    });
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML.replace(/'/g, '&#39;');
}

// Set loading state
function setLoadingState(loading, type) {
    if (type === 'image') {
        generateFromImage.disabled = loading;
        generateImageText.style.display = loading ? 'none' : 'inline';
        imageSpinner.style.display = loading ? 'block' : 'none';
    } else if (type === 'text') {
        generateFromText.disabled = loading;
        generateTextText.style.display = loading ? 'none' : 'inline';
        textSpinner.style.display = loading ? 'block' : 'none';
    }
}

// Show toast notification
function showToast(message, type = 'success') {
    toastMessage.textContent = message;
    toast.style.background = type === 'error' ? 'var(--error-color)' : 'var(--success-color)';
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Reset form
function resetForm() {
    removeImage();
    textBrief.value = '';
    updateCharCount();
    resultsSection.style.display = 'none';
    window.scrollTo({ top: 0, behavior: 'smooth' });
}