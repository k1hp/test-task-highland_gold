const API_URL = 'http://localhost:8000';
let currentProjectId = null;

// load projects on page load
document.addEventListener('DOMContentLoaded', loadProjects);

async function loadProjects() {
    try {
        const response = await fetch(`${API_URL}/projects/`);
        const projects = await response.json();
        displayProjects(projects);
    } catch (error) {
        console.error('Error loading projects:', error);
        showError('Failed to load projects');
    }
}

function displayProjects(projects) {
    const container = document.getElementById('projectsList');
    container.innerHTML = '';

    if (projects.length === 0) {
        container.innerHTML = '<p class="text-muted">No projects yet</p>';
        return;
    }

    projects.forEach(project => {
        const projectDiv = document.createElement('div');
        projectDiv.className = 'project-item card mb-2 p-3';
        projectDiv.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <strong>${project.name}</strong>
                    <div class="text-muted small">${new Date(project.created_at).toLocaleDateString()}</div>
                </div>
                <div>
                    <button class="btn btn-sm btn-outline-primary" onclick="viewProject(${project.project_id}, '${project.name}')">
                        View
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteProject(${project.project_id})">
                        Delete
                    </button>
                </div>
            </div>
            <div class="small text-muted mt-1">Images: ${project.images?.length || 0}</div>
        `;
        container.appendChild(projectDiv);
    });
}

async function createProject() {
    const nameInput = document.getElementById('projectName');
    const name = nameInput.value.trim();

    if (!name) {
        alert('Please enter project name');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/projects/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name })
        });

        if (response.ok) {
            nameInput.value = '';
            loadProjects();
            showSuccess('Project created');
        } else {
            const error = await response.json();
            alert(error.detail || 'Failed to create project');
        }
    } catch (error) {
        console.error('Error creating project:', error);
        showError('Failed to create project');
    }
}

async function viewProject(projectId, projectName) {
    currentProjectId = projectId;

    // update UI
    document.getElementById('currentProject').innerHTML = `
        Project: <strong>${projectName}</strong>
        <button class="btn btn-sm btn-outline-secondary float-end" onclick="closeProject()">
            Close
        </button>
    `;
    document.getElementById('currentProject').style.display = 'block';
    document.getElementById('uploadSection').style.display = 'block';

    // load images
    await loadProjectImages(projectId);
}

function closeProject() {
    currentProjectId = null;
    document.getElementById('currentProject').style.display = 'none';
    document.getElementById('uploadSection').style.display = 'none';
    document.getElementById('imagesList').innerHTML = '';
}

async function loadProjectImages(projectId) {
    try {
        const response = await fetch(`${API_URL}/projects/${projectId}/images/`);
        const images = await response.json();
        displayImages(images);
    } catch (error) {
        console.error('Error loading images:', error);
        showError('Failed to load images');
    }
}

function displayImages(images) {
    const container = document.getElementById('imagesList');
    container.innerHTML = '';

    if (images.length === 0) {
        container.innerHTML = '<p class="text-muted">No images yet</p>';
        return;
    }

    images.forEach(image => {
        const col = document.createElement('div');
        col.className = 'col-md-4 col-sm-6';
        col.innerHTML = `
            <div class="image-card">
                <img src="${API_URL}${image.public_url}" 
                     alt="${image.original_filename}"
                     onclick="previewImage('${API_URL}${image.public_url}', '${image.original_filename}')"
                     class="img-thumbnail">
                <div class="image-actions">
                    <button class="btn btn-sm btn-danger" onclick="deleteImage(${image.image_id})">
                        ✕
                    </button>
                </div>
                <div class="small text-truncate mt-1">${image.original_filename}</div>
            </div>
        `;
        container.appendChild(col);
    });
}

async function uploadImages() {
    const input = document.getElementById('imageUpload');
    const files = input.files;

    if (!files.length || !currentProjectId) {
        alert('Please select files and open a project');
        return;
    }

    for (let file of files) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${API_URL}/projects/${currentProjectId}/images/`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                console.error('Upload failed:', error);
            }
        } catch (error) {
            console.error('Error uploading:', error);
        }
    }

    // clear input and refresh
    input.value = '';
    await loadProjectImages(currentProjectId);
    showSuccess('Images uploaded');
}

async function deleteProject(projectId) {
    if (!confirm('Delete this project and all its images?')) return;

    try {
        const response = await fetch(`${API_URL}/projects/${projectId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            if (currentProjectId === projectId) closeProject();
            loadProjects();
            showSuccess('Project deleted');
        }
    } catch (error) {
        console.error('Error deleting project:', error);
        showError('Failed to delete project');
    }
}

async function deleteImage(imageId) {
    if (!confirm('Delete this image?')) return;

    try {
        const response = await fetch(`${API_URL}/images/${imageId}`, {
            method: 'DELETE'
        });

        if (response.ok && currentProjectId) {
            await loadProjectImages(currentProjectId);
            showSuccess('Image deleted');
        }
    } catch (error) {
        console.error('Error deleting image:', error);
        showError('Failed to delete image');
    }
}

function previewImage(imageUrl, filename) {
    const modal = new bootstrap.Modal(document.getElementById('imageModal'));
    document.getElementById('modalImage').src = imageUrl;

    // set download link
    const downloadLink = document.getElementById('downloadLink');
    downloadLink.href = imageUrl;
    downloadLink.download = filename;

    modal.show();
}

function showSuccess(message) {
    alert(message); // Simple alert for MVP
}

function showError(message) {
    alert('Error: ' + message);
}