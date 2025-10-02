// Global variables
let currentCategories = [];

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    initializeMasonryLayout();
    initializeImageLoading();
});

// Event Listeners
function initializeEventListeners() {
    // Card click events
    document.addEventListener('click', function(e) {
        const promptCard = e.target.closest('.prompt-card');
        const sponsorCard = e.target.closest('.sponsor-card');
        
        if (promptCard && !e.target.closest('.btn, .unsave-btn')) {
            const promptId = promptCard.closest('[data-prompt-id]').dataset.promptId;
            viewPrompt(promptId);
        } else if (sponsorCard && !e.target.closest('.btn')) {
            const sponsorshipId = sponsorCard.closest('[data-sponsorship-id]').dataset.sponsorshipId;
            viewSponsorship(sponsorshipId);
        }
    });

    // Modal events
    const promptModal = document.getElementById('promptModal');
    if (promptModal) {
        promptModal.addEventListener('hidden.bs.modal', function() {
            document.getElementById('promptModalContent').innerHTML = '';
        });
    }

    // Edit modal events
    const editModal = document.getElementById('editPromptModal');
    if (editModal) {
        editModal.addEventListener('shown.bs.modal', function() {
            populateCategorySelect();
        });
    }
}

// Initialize masonry layout (CSS-only approach, but we can add JavaScript enhancements)
function initializeMasonryLayout() {
    // Add any JavaScript enhancements to the CSS masonry layout if needed
    const masonryContainer = document.querySelector('.masonry-container');
    if (masonryContainer) {
        // Force reflow to ensure proper layout
        masonryContainer.style.columnFill = 'balance';
    }
}

// Initialize image loading with lazy loading support
function initializeImageLoading() {
    const images = document.querySelectorAll('img[loading="lazy"]');
    
    images.forEach(img => {
        img.addEventListener('load', function() {
            this.style.animation = 'none';
        });
        
        img.addEventListener('error', function() {
            this.style.animation = 'none';
            this.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZGRkIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNHB4IiBmaWxsPSIjOTk5IiBkb21pbmFudC1iYXNlbGluZT0ibWlkZGxlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj5JbWFnZSBub3QgZm91bmQ8L3RleHQ+PC9zdmc+';
        });
    });
}

// View prompt details
async function viewPrompt(promptId) {
    try {
        const response = await fetch(`/get_prompt/${promptId}`);
        const data = await response.json();
        
        showPromptModal(data);
    } catch (error) {
        console.error('Error fetching prompt details:', error);
        showAlert('Error loading prompt details', 'danger');
    }
}

// Show prompt details in modal
function showPromptModal(prompt) {
    const modal = new bootstrap.Modal(document.getElementById('promptModal'));
    const title = document.getElementById('promptModalTitle');
    const content = document.getElementById('promptModalContent');
    
    title.textContent = prompt.title;
    
    // Check if user is authenticated and subscribed
    const isAuthenticated = document.querySelector('.user-info') !== null;
    const isSubscribed = document.querySelector('.badge.bg-success') !== null;
    
    let contentHTML = `
        <div class="row">
            <div class="col-md-6">
                <img src="${prompt.image_url}" alt="${prompt.title}" class="img-fluid rounded mb-3">
            </div>
            <div class="col-md-6">
                <div class="prompt-details">
                    <div class="detail-section">
                        <h6>${feather.icons['folder'].toSvg()} Category</h6>
                        <p>${prompt.category}</p>
                    </div>
                    
                    <div class="detail-section">
                        <h6>${feather.icons['user'].toSvg()} Creator</h6>
                        <div class="d-flex align-items-center">

                            <img src="${prompt.creator_profile_pic || '/static/images/default-profile.svg'}" 
                                 alt="${prompt.creator}" 
                                 class="rounded-circle me-2" 
                                 width="40" height="35" 
                                 style="object-fit: cover;">
                            <div>
                                <div>${prompt.creator}</div>
                                <a href='https://instagram.com/${prompt.creator_instagram}' target='_blank'>${prompt.creator_instagram ? `<small class="text-muted">${feather.icons['instagram'].toSvg({width:14,height:14})} @${prompt.creator_instagram}</small>` : ''}</a>
                            </div>
                        </div>
                    </div>
                    
                    <div class="detail-section">
                        <h6>${feather.icons['calendar'].toSvg()} Created</h6>
                        <p>${prompt.created_at}</p>
                    </div>
                    
                   <!-- MODELS USED -->
                    <div class="detail-section">
                    <h6 class="text-muted d-flex align-items-center gap-2">
                        ${feather.icons['cpu'].toSvg()} Models Used
                    </h6>

                    <div class="d-flex gap-4 mt-2 flex-wrap justify-content-start align-items-center">
                        <!-- Gemini -->
                        <a href="https://gemini.google.com/" target="_blank" rel="noopener" class="model-item text-center">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/1/1d/Google_Gemini_icon_2025.svg" 
                            alt="Gemini" class="model-icon white-icon"/>
                        <div class="model-name">Gemini</div>
                        </a>

                        <!-- ChatGPT -->
                        <a href="https://chat.openai.com/" target="_blank" rel="noopener" class="model-item text-center">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/e/ef/ChatGPT-Logo.svg" 
                            alt="ChatGPT" class="model-icon white-icon"/>
                        <div class="model-name">ChatGPT</div>
                        </a>

                        <!-- LMArena -->
                        <a href="https://lmarena.ai/" target="_blank" rel="noopener" class="model-item text-center">
                        <img src="https://uxwing.com/wp-content/themes/uxwing/download/brands-and-social-media/lmarena-ai-icon.svg" 
                            alt="LMArena" class="model-icon white-icon"/>
                        <div class="model-name">LMArena</div>
                        </a>

                        <!-- MidJourney -->
                        <a href="https://www.midjourney.com/" target="_blank" rel="noopener" class="model-item text-center">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/Midjourney_Emblem.svg/960px-Midjourney_Emblem.svg.png?20230928155157
                            alt="MidJourney" class="model-icon white-icon"/>
                        <div class="model-name">MidJourney</div>
                        </a>
                    </div>
                    </div>
                    <!-- END MODELS USED -->
                </div>
            </div>
        </div>
        
        <div class="detail-section mt-3">
            <h6>${feather.icons['info'].toSvg()} Description</h6>
            <p>${prompt.description}</p>
        </div>
    `;
    
    // Show prompt text only for subscribed users
    if (prompt.can_view_details) {
        contentHTML += `
            <div class="detail-section">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <!-- Left side: Title -->
                    <h6 class="d-flex align-items-center mb-0">
                        ${feather.icons['file-text'].toSvg()} Prompt Text
                    </h6>

                    <!-- Right side: Buttons -->
                    <div>
                        <button class="btn btn-sm btn-outline-secondary me-1" onclick="copyPromptText('${prompt.id}')" id="copyBtn_${prompt.id}">
                            ${feather.icons['copy'].toSvg()} Copy
                        </button>
                        <button class="btn btn-sm btn-outline-primary" onclick="sharePromptText('${prompt.id}')" id="shareBtn_${prompt.id}">
                            ${feather.icons['share-2'].toSvg()} Share
                        </button>
                    </div>
                </div>
                <p class="font-monospace bg-body-secondary p-3 rounded" id="promptText_${prompt.id}">${prompt.prompt_text}</p>
            </div>
        `;
        
        // Show action buttons for authenticated users
        let actionButtons = '';
        if (!prompt.is_saved) {
            actionButtons += `<button class="btn btn-outline-primary me-2" onclick="savePrompt(this, ${prompt.id})">
                <i class="fa-regular fa-bookmark"></i> Save Prompt
            </button>`;
        } else {
            actionButtons += `<button class="btn btn-outline-secondary me-2" onclick="unsavePrompt(this, ${prompt.id})">
                <i class="fa-solid fa-bookmark"></i> Unsave Prompt
            </button>`;
        }

        
        if (prompt.can_edit) {
            actionButtons += `
                <button class="btn btn-outline-secondary me-2" onclick="editPrompt(${prompt.id})">
                    ${feather.icons['edit'].toSvg()} Edit
                </button>
                <button class="btn btn-outline-danger" onclick="deletePrompt(${prompt.id})">
                    ${feather.icons['trash-2'].toSvg()} Delete
                </button>
            `;
        }
        
        if (actionButtons) {
            contentHTML += `<div class="mt-3">${actionButtons}</div>`;
        }
    } else if (isAuthenticated && !isSubscribed) {
        // Show subscription prompt for non-subscribed users
        contentHTML += `
            <div class="subscription-prompt">
                <div class="icon">🔒</div>
                <h4>Premium Content</h4>
                <p>Upgrade to Premium to view full prompt details and access all features.</p>
                <form action="/subscription" method="POST" style="display: inline;">
                    <button type="submit" class="btn btn-warning">Upgrade to Premium</button>
                </form>
            </div>
        `;
    } else {
        // Show login prompt for non-authenticated users
        contentHTML += `
            <div class="subscription-prompt">
                <div class="icon">🔐</div>
                <h4>Login Required</h4>
                <p>Please login to view full prompt details and access all features.</p>
                <a href="/login" class="btn btn-primary">Login</a>
                <a href="/register" class="btn btn-outline-primary ms-2">Register</a>
            </div>
        `;
    }
    
    content.innerHTML = contentHTML;
    
    // Re-initialize feather icons
    // feather.replace();
    
    modal.show();
}

// Edit prompt
async function editPrompt(promptId) {
    try {
        const response = await fetch(`/get_prompt/${promptId}`);
        const data = await response.json();
        
        if (!data.can_edit) {
            showAlert('You can only edit your own prompts', 'danger');
            return;
        }
        
        // Populate the edit form
        document.getElementById('editPromptId').value = promptId;
        document.getElementById('editTitle').value = data.title;
        document.getElementById('editDescription').value = data.description;
        document.getElementById('editPromptText').value = data.prompt_text;
        document.getElementById('editImageUrl').value = data.image_url;
        
        // Show the edit modal
        const modal = new bootstrap.Modal(document.getElementById('editPromptModal'));
        modal.show();
    } catch (error) {
        console.error('Error fetching prompt for edit:', error);
        showAlert('Error loading prompt for editing', 'danger');
    }
}

// Save prompt changes
async function savePromptChanges() {
    const form = document.getElementById('editPromptForm');
    const formData = new FormData(form);
    const promptId = document.getElementById('editPromptId').value;
    
    try {
        const response = await fetch(`/edit_prompt/${promptId}`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            bootstrap.Modal.getInstance(document.getElementById('editPromptModal')).hide();
            // Reload the page to show updated content
            window.location.reload();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        console.error('Error saving prompt changes:', error);
        showAlert('Error saving changes', 'danger');
    }
}

// Delete prompt
async function deletePrompt(promptId) {
    if (!confirm('Are you sure you want to delete this prompt? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch(`/delete_prompt/${promptId}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            // Remove the prompt card from the page
            const promptElement = document.querySelector(`[data-prompt-id="${promptId}"]`);
            if (promptElement) {
                promptElement.remove();
            }
            
            // Close any open modals
            const modals = ['promptModal', 'editPromptModal'];
            modals.forEach(modalId => {
                const modalElement = document.getElementById(modalId);
                if (modalElement) {
                    const modal = bootstrap.Modal.getInstance(modalElement);
                    if (modal) {
                        modal.hide();
                    }
                }
            });
            window.location.reload();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        console.error('Error deleting prompt:', error);
        showAlert('Error deleting prompt', 'danger');
    }
}

//save prompt
async function savePrompt(button, promptId) {
    try {
        const response = await fetch(`/save_prompt/${promptId}`, { method: 'POST' });
        const result = await response.json();

        if (result.success) {
            showAlert(result.message, 'success');
            button.innerHTML = '<i class="fa-solid fa-bookmark"></i> Unsave Prompt';
            button.className = 'btn btn-outline-secondary me-2';
            button.setAttribute("onclick", `unsavePrompt(this, ${promptId})`);
            // feather.replace();
        } else {
            showAlert(result.message, 'warning');
        }
    } catch (error) {
        console.error('Error saving prompt:', error);
        showAlert('Error saving prompt', 'danger');
    }
}

//unsave prompt
async function unsavePrompt(button, promptId) {
    try {
        const response = await fetch(`/unsave_prompt/${promptId}`, { method: 'POST' });
        const result = await response.json();

        if (result.success) {
            showAlert(result.message, 'success');

            if (window.location.pathname === '/saved_prompts') {
                const promptElement = document.querySelector(`[data-prompt-id="${promptId}"]`);
                if (promptElement) promptElement.remove();
            } else {
                button.innerHTML ='<i class="fa-regular fa-bookmark"></i> Save Prompt';
                button.className = 'btn btn-outline-primary me-2';
                button.setAttribute("onclick", `savePrompt(this, ${promptId})`);
                // feather.replace();
            }
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        console.error('Error unsaving prompt:', error);
        showAlert('Error removing saved prompt', 'danger');
    }
}

// Populate category select in edit modal
async function populateCategorySelect() {
    const select = document.getElementById('editCategory');
    if (!select || select.children.length > 1) return; // Already populated
    
    try {
        // Get categories from the dropdown in the page (if available)
        const categoryDropdown = document.querySelector('.dropdown-menu');
        if (categoryDropdown) {
            const categoryLinks = categoryDropdown.querySelectorAll('.dropdown-item[href*="category="]');
            categoryLinks.forEach(link => {
                const url = new URL(link.href);
                const categoryId = url.searchParams.get('category');
                const categoryName = link.textContent;
                
                if (categoryId && categoryName) {
                    const option = document.createElement('option');
                    option.value = categoryId;
                    option.textContent = categoryName;
                    select.appendChild(option);
                }
            });
        }
    } catch (error) {
        console.error('Error populating category select:', error);
    }
}

// Show alert message
function showAlert(message, type = 'info') {
    // Create alert element
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Find or create alert container
    let alertContainer = document.querySelector('.alert-container');
    if (!alertContainer) {
        alertContainer = document.createElement('div');
        alertContainer.className = 'alert-container';
        alertContainer.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 1050; max-width: 350px;';
        document.body.appendChild(alertContainer);
    }
    
    // Add alert to container
    alertContainer.appendChild(alert);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

// Utility function to handle form submissions
function handleFormSubmit(formId, callback) {
    const form = document.getElementById(formId);
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            callback(new FormData(form));
        });
    }
}

// Mobile sidebar toggle
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    
    if (sidebar && overlay) {
        sidebar.classList.toggle('show');
        overlay.classList.toggle('show');
        
        // Prevent body scroll when sidebar is open
        if (sidebar.classList.contains('show')) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
    }
}

// Close sidebar
function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    
    if (sidebar && overlay) {
        sidebar.classList.remove('show');
        overlay.classList.remove('show');
        document.body.style.overflow = '';
    }
}

// Close sidebar when clicking nav links on mobile
document.addEventListener('DOMContentLoaded', function() {
    const navLinks = document.querySelectorAll('.sidebar .nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth < 768) {
                closeSidebar();
            }
        });
    });
});

// Initialize tooltips and popovers
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// Handle window resize for responsive layout
window.addEventListener('resize', function() {
    // Recalculate masonry layout if needed
    const masonryContainer = document.querySelector('.masonry-container');
    if (masonryContainer) {
        // Force reflow
        masonryContainer.style.columnFill = 'balance';
    }
});

// Copy prompt text function
async function copyPromptText(promptId) {
    const textElement = document.getElementById(`promptText_${promptId}`);
    const copyBtn = document.getElementById(`copyBtn_${promptId}`);
    
    if (textElement) {
        try {
            await navigator.clipboard.writeText(textElement.textContent);
            
            // Update button to show success
            const originalContent = copyBtn.innerHTML;
            copyBtn.innerHTML = feather.icons['check'].toSvg() + " Copied!";
            copyBtn.classList.remove('btn-outline-secondary');
            copyBtn.classList.add('btn-success');
            
            // Replace feather icons
            // feather.replace();
            
            // Reset button after 2 seconds
            setTimeout(() => {
                copyBtn.innerHTML = originalContent;
                copyBtn.classList.remove('btn-success');
                copyBtn.classList.add('btn-outline-secondary');
                // feather.replace();
            }, 2000);
            
        } catch (err) {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = textElement.textContent;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            
            showAlert('Prompt text copied to clipboard!', 'success');
        }
    }
}

// Share prompt text function
function sharePromptText(promptId) {
    // Pehle prompt data fetch karo
    fetch(`/get_prompt/${promptId}`)
        .then(res => res.json())
        .then(prompt => {
            const shareUrl = `${window.location.origin}/?prompt=${promptId}`;
            // Dynamic share text: title + creator
            const shareText = `${prompt.title} by ${prompt.creator}\nCheck it out here: `;

            if (navigator.share) {
                navigator.share({
                    title: prompt.title,
                    text: shareText,
                    url: shareUrl
                }).then(() => console.log('Prompt shared successfully'))
                  .catch(err => console.error('Error sharing:', err));
            } else {
                // Fallback: copy to clipboard
                navigator.clipboard.writeText(shareText)
                    .then(() => alert('Prompt details copied to clipboard!'));
            }
        })
        .catch(err => {
            console.error('Error fetching prompt for share:', err);
            alert('Unable to share prompt.');
        });
}

document.addEventListener("DOMContentLoaded", () => {
    const urlParams = new URLSearchParams(window.location.search);
    const promptId = urlParams.get('prompt');
    if (promptId) {
        // Agar prompt param hai, modal open karo
        viewPrompt(promptId);
    }
});

// View sponsorship details
function viewSponsorship(sponsorshipId) {
    // Open sponsorship detail page in new tab
    window.location.href=(`/sponsorship/${sponsorshipId}`);
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Escape key to close modals
    if (e.key === 'Escape') {
        const openModals = document.querySelectorAll('.modal.show');
        openModals.forEach(modal => {
            const modalInstance = bootstrap.Modal.getInstance(modal);
            if (modalInstance) {
                modalInstance.hide();
            }
        });
    }
});
