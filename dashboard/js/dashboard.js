/* ══════════════════════════════════════════════════
   Dashboard JS — SPA routing, CRUD, UI logic
   ══════════════════════════════════════════════════ */

let currentPage = 'overview';

function toast(msg, type = 'success') {
  const c = document.getElementById('toastContainer');
  const t = document.createElement('div');
  t.className = `toast toast--${type}`;
  t.textContent = msg;
  c.appendChild(t);
  setTimeout(() => t.remove(), 3500);
}

function openModal(title, bodyHtml) {
  document.getElementById('modalTitle').textContent = title;
  document.getElementById('modalBody').innerHTML = bodyHtml;
  document.getElementById('modalOverlay').classList.add('open');
}

function closeModal() {
  document.getElementById('modalOverlay').classList.remove('open');
}

document.getElementById('modalClose').addEventListener('click', closeModal);
document.getElementById('modalOverlay').addEventListener('click', (e) => {
  if (e.target === e.currentTarget) closeModal();
});

// Mobile menu
document.getElementById('mobileMenuBtn').addEventListener('click', () => {
  document.getElementById('sidebar').classList.toggle('open');
});

// Nav routing
document.querySelectorAll('.nav-item').forEach(item => {
  item.addEventListener('click', (e) => {
    e.preventDefault();
    const page = item.dataset.page;
    navigateTo(page);
    document.getElementById('sidebar').classList.remove('open');
  });
});

function navigateTo(page) {
  currentPage = page;
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  const nav = document.querySelector(`[data-page="${page}"]`);
  if (nav) nav.classList.add('active');
  window.location.hash = `/${page}`;
  loadPage(page);
}

function initDashboard() {
  const hash = window.location.hash.replace('#/', '') || 'overview';
  navigateTo(hash);
  loadUnreadCount();
}

async function loadUnreadCount() {
  try {
    const res = await Auth.api('/api/contacts/count');
    if (res.ok) {
      const data = await res.json();
      const badge = document.getElementById('contactsBadge');
      if (data.unread_count > 0) {
        badge.textContent = data.unread_count;
        badge.style.display = 'inline';
      } else { badge.style.display = 'none'; }
    }
  } catch(e) {}
}

function loadPage(page) {
  const area = document.getElementById('contentArea');
  area.innerHTML = '<div class="loading" style="text-align:center;padding:3rem;color:var(--text-muted)">Loading…</div>';
  switch(page) {
    case 'overview': loadOverview(); break;
    case 'blog': loadBlog(); break;
    case 'contacts': loadContacts(); break;
    case 'events': loadEvents(); break;
    default: loadOverview();
  }
}

/* ── OVERVIEW ──────────────────────────────────── */
async function loadOverview() {
  const area = document.getElementById('contentArea');
  try {
    const res = await Auth.api('/api/dashboard/stats');
    const stats = await res.json();
    area.innerHTML = `
      <div class="page-header"><div><h1>Dashboard Overview</h1><p>Welcome back, ${Auth.admin?.full_name || 'Admin'}</p></div></div>
      <div class="stats-grid">
        <div class="stat-card stat-card--pink">
          <div class="stat-icon stat-icon--pink"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg></div>
          <div class="stat-value">${stats.blog.total}</div>
          <div class="stat-label">Blog Posts</div>
          <div class="stat-sub">${stats.blog.published} published · ${stats.blog.drafts} drafts</div>
        </div>
        <div class="stat-card stat-card--orange">
          <div class="stat-icon stat-icon--orange"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg></div>
          <div class="stat-value">${stats.contacts.unread}</div>
          <div class="stat-label">Unread Messages</div>
          <div class="stat-sub">${stats.contacts.total} total submissions</div>
        </div>
        <div class="stat-card stat-card--green">
          <div class="stat-icon stat-icon--green"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg></div>
          <div class="stat-value">${stats.events.total}</div>
          <div class="stat-label">Events</div>
          <div class="stat-sub">${stats.events.published} published</div>
        </div>
      </div>`;
  } catch(e) { area.innerHTML = '<p style="color:var(--danger);padding:2rem">Failed to load stats</p>'; }
}

/* ── BLOG ──────────────────────────────────────── */
async function loadBlog() {
  const area = document.getElementById('contentArea');
  try {
    const res = await Auth.api('/api/blog/');
    const posts = await res.json();
    let rows = '';
    posts.forEach(p => {
      const status = p.is_published ? 'published' : 'draft';
      const date = new Date(p.created_at).toLocaleDateString('en-GB',{day:'numeric',month:'short',year:'numeric'});
      const thumb = p.cover_image ? `<img src="${esc(p.cover_image)}" style="width:40px;height:40px;object-fit:cover;border-radius:6px;margin-right:0.6rem;vertical-align:middle">` : `<span style="display:inline-block;width:40px;height:40px;border-radius:6px;background:var(--bg-input);margin-right:0.6rem;vertical-align:middle"></span>`;
      rows += `<tr>
        <td style="display:flex;align-items:center">${thumb}<div><strong>${esc(p.title)}</strong><br><span style="color:var(--text-muted);font-size:0.75rem">${esc(p.author)}</span></div></td>
        <td><span class="status-badge status-badge--${status}"><span class="status-dot"></span>${status}</span></td>
        <td style="color:var(--text-secondary)">${date}</td>
        <td><div class="action-btns">
          <button class="action-btn" onclick="editBlog(${p.id})" title="Edit"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg></button>
          <button class="action-btn" onclick="uploadBlogImage(${p.id})" title="Upload image">📷</button>
          <button class="action-btn action-btn--danger" onclick="deleteBlog(${p.id})" title="Delete"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg></button>
        </div></td>
      </tr>`;
    });
    area.innerHTML = `
      <div class="page-header"><div><h1>Blog Posts</h1><p>Manage your Rooted in Opulence articles</p></div>
        <div class="header-actions"><button class="btn-primary-dash" onclick="showBlogForm()">+ New Post</button></div></div>
      <div class="data-table-wrap"><table class="data-table"><thead><tr><th>Title / Author</th><th>Status</th><th>Date</th><th>Actions</th></tr></thead>
        <tbody>${rows || '<tr><td colspan="4" class="table-empty">No blog posts yet. Create your first post!</td></tr>'}</tbody></table></div>`;
  } catch(e) { area.innerHTML = '<p style="color:var(--danger);padding:2rem">Failed to load posts</p>'; }
}

function showBlogForm(post = null) {
  const isEdit = !!post;
  openModal(isEdit ? 'Edit Post' : 'New Blog Post', `
    <form class="modal-form" id="blogModalForm">
      <div class="form-group"><label>Title</label><input type="text" id="blogTitle" value="${esc(post?.title||'')}" required></div>
      <div class="form-row">
        <div class="form-group"><label>Author</label><input type="text" id="blogAuthor" value="${esc(post?.author||'')}" required></div>
        <div class="form-group"><label>Category</label><input type="text" id="blogCategory" value="${esc(post?.category||'')}" placeholder="e.g. Fashion, Sustainability"></div>
      </div>
      <div class="form-group"><label>Excerpt</label><textarea id="blogExcerpt" rows="2" placeholder="Short summary…">${esc(post?.excerpt||'')}</textarea></div>
      <div class="form-group"><label>Content</label><textarea id="blogContent" rows="8" required placeholder="Write your article…">${esc(post?.content||'')}</textarea></div>
      <div class="form-group"><label>Cover Image</label>
        <input type="hidden" id="blogCover" value="${esc(post?.cover_image||'')}">
        <div class="image-upload-area" id="blogDropZone">
          <input type="file" id="blogImageInput" accept="image/*">
          <div class="upload-icon"><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg></div>
          <p class="upload-text">Drag & drop or <strong>click to browse</strong></p>
        </div>
        <div id="blogImgPreview" class="image-preview" style="${post?.cover_image?'':'display:none'}">${post?.cover_image?`<img src="${esc(post.cover_image)}"><button type="button" class="image-preview-remove" onclick="removeBlogPreview()">&times;</button>`:''}</div>
      </div>
      <div class="form-group"><label>Tags</label><input type="text" id="blogTags" value="${esc(post?.tags||'')}" placeholder="e.g. fashion, sustainability, dmu"></div>
      <div class="form-group"><label>External Link</label><input type="url" id="blogExtLink" value="${esc(post?.external_link||'')}" placeholder="https://…"></div>
      <div class="form-group"><label><input type="checkbox" id="blogPublished" ${post?.is_published?'checked':''}> Publish immediately</label></div>
      <div class="modal-actions">
        <button type="button" class="btn-secondary" onclick="closeModal()">Cancel</button>
        <button type="submit" class="btn-primary-dash">${isEdit?'Update':'Create'} Post</button>
      </div>
    </form>`);
  document.getElementById('blogModalForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const body = {
      title: document.getElementById('blogTitle').value,
      author: document.getElementById('blogAuthor').value,
      category: document.getElementById('blogCategory').value || null,
      excerpt: document.getElementById('blogExcerpt').value || null,
      content: document.getElementById('blogContent').value,
      cover_image: document.getElementById('blogCover').value || null,
      tags: document.getElementById('blogTags').value || null,
      external_link: document.getElementById('blogExtLink').value || null,
      is_published: document.getElementById('blogPublished').checked,
    };
    try {
      const url = isEdit ? `/api/blog/${post.id}` : '/api/blog/';
      const res = await Auth.api(url, { method: isEdit?'PUT':'POST', body });
      if (res.ok) { closeModal(); toast(isEdit?'Post updated':'Post created'); loadBlog(); }
      else { const err = await res.json(); toast(err.detail||'Error','error'); }
    } catch(e) { toast('Network error','error'); }
  });

  // Inline image upload in form
  const blogFileInput = document.getElementById('blogImageInput');
  const blogDropZone = document.getElementById('blogDropZone');
  const blogPreview = document.getElementById('blogImgPreview');
  const blogCoverField = document.getElementById('blogCover');

  async function handleBlogFile(file) {
    if (!file || !file.type.startsWith('image/')) return;
    const fd = new FormData(); fd.append('file', file);
    blogDropZone.querySelector('.upload-text').innerHTML = 'Uploading…';
    try {
      const res = await Auth.api('/api/blog/upload-image', { method:'POST', body: fd });
      if (res.ok) {
        const data = await res.json();
        blogCoverField.value = data.image_url;
        blogPreview.innerHTML = `<img src="${data.image_url}"><button type="button" class="image-preview-remove" onclick="removeBlogPreview()">&times;</button>`;
        blogPreview.style.display = 'block';
        blogDropZone.querySelector('.upload-text').innerHTML = 'Image uploaded ✓ — drag another to replace';
      } else {
        blogDropZone.querySelector('.upload-text').innerHTML = 'Upload failed — try again';
      }
    } catch(e) {
      blogDropZone.querySelector('.upload-text').innerHTML = 'Upload failed — try again';
    }
  }
  if (blogFileInput) blogFileInput.addEventListener('change', (e) => handleBlogFile(e.target.files[0]));
  if (blogDropZone) {
    blogDropZone.addEventListener('dragover', (e) => { e.preventDefault(); blogDropZone.classList.add('dragover'); });
    blogDropZone.addEventListener('dragleave', () => blogDropZone.classList.remove('dragover'));
    blogDropZone.addEventListener('drop', (e) => { e.preventDefault(); blogDropZone.classList.remove('dragover'); handleBlogFile(e.dataTransfer.files[0]); });
  }
}

async function editBlog(id) {
  const res = await Auth.api(`/api/blog/${id}`);
  if (res.ok) { const post = await res.json(); showBlogForm(post); }
}

async function deleteBlog(id) {
  if (!confirm('Delete this post?')) return;
  const res = await Auth.api(`/api/blog/${id}`, { method:'DELETE' });
  if (res.ok) { toast('Post deleted'); loadBlog(); }
  else toast('Delete failed','error');
}

function uploadBlogImage(id) {
  openModal('Upload Blog Cover Image', `
    <div class="image-upload-area" id="dropZone">
      <input type="file" id="imageFileInput" accept="image/*">
      <div class="upload-icon"><svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg></div>
      <p class="upload-text">Drag & drop or <strong>click to browse</strong></p>
    </div>
    <div id="imgPreview" class="image-preview" style="display:none"></div>
    <div class="modal-actions" style="margin-top:1rem">
      <button class="btn-secondary" onclick="closeModal()">Cancel</button>
      <button class="btn-primary-dash" id="uploadBtn" disabled onclick="doBlogUpload(${id})">Upload</button>
    </div>`);
  let selectedFile = null;
  const fileInput = document.getElementById('imageFileInput');
  const dropZone = document.getElementById('dropZone');
  const preview = document.getElementById('imgPreview');
  function handleFile(file) {
    if (!file || !file.type.startsWith('image/')) return;
    selectedFile = file;
    const reader = new FileReader();
    reader.onload = (e) => { preview.innerHTML = `<img src="${e.target.result}">`; preview.style.display = 'block'; };
    reader.readAsDataURL(file);
    document.getElementById('uploadBtn').disabled = false;
  }
  fileInput.addEventListener('change', (e) => handleFile(e.target.files[0]));
  dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('dragover'); });
  dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
  dropZone.addEventListener('drop', (e) => { e.preventDefault(); dropZone.classList.remove('dragover'); handleFile(e.dataTransfer.files[0]); });
  window.doBlogUpload = async function(postId) {
    if (!selectedFile && !fileInput.files[0]) return;
    const f = selectedFile || fileInput.files[0];
    const fd = new FormData(); fd.append('file', f);
    const btn = document.getElementById('uploadBtn');
    btn.disabled = true; btn.textContent = 'Uploading…';
    const res = await Auth.api(`/api/blog/${postId}/upload-image`, { method:'POST', body: fd });
    if (res.ok) { closeModal(); toast('Cover image uploaded'); loadBlog(); }
    else { toast('Upload failed','error'); btn.disabled = false; btn.textContent = 'Upload'; }
  };
}

function removeBlogPreview() {
  document.getElementById('blogCover').value = '';
  const preview = document.getElementById('blogImgPreview');
  preview.innerHTML = ''; preview.style.display = 'none';
}

/* ── CONTACTS ──────────────────────────────────── */
let contactFilter = null;
async function loadContacts(filter) {
  if (filter !== undefined) contactFilter = filter;
  const area = document.getElementById('contentArea');
  try {
    let url = '/api/contacts/';
    if (contactFilter) url += `?filter=${contactFilter}`;
    const res = await Auth.api(url);
    const contacts = await res.json();
    let rows = '';
    contacts.forEach(c => {
      const status = c.is_archived ? 'archived' : (c.is_read ? 'read' : 'unread');
      const date = new Date(c.created_at).toLocaleDateString('en-GB',{day:'numeric',month:'short',year:'numeric'});
      rows += `<tr style="cursor:pointer" onclick="viewContact(${c.id})">
        <td><strong style="${!c.is_read?'color:var(--text-primary)':'color:var(--text-secondary)'}">${esc(c.name)}</strong></td>
        <td style="color:var(--text-secondary)">${esc(c.subject)}</td>
        <td><span class="status-badge status-badge--${status}"><span class="status-dot"></span>${status}</span></td>
        <td style="color:var(--text-secondary)">${date}</td>
        <td><div class="action-btns">
          ${!c.is_read?`<button class="action-btn" onclick="event.stopPropagation();markRead(${c.id})" title="Mark read">✓</button>`:''}
          ${!c.is_archived?`<button class="action-btn" onclick="event.stopPropagation();archiveContact(${c.id})" title="Archive">📥</button>`:''}
          <button class="action-btn action-btn--danger" onclick="event.stopPropagation();deleteContact(${c.id})" title="Delete">✕</button>
        </div></td>
      </tr>`;
    });
    const fBtn = (f,label) => `<button class="filter-btn ${contactFilter===f?'active':''}" onclick="loadContacts('${f}')">${label}</button>`;
    area.innerHTML = `
      <div class="page-header"><div><h1>Contact Submissions</h1><p>Messages from the website contact form</p></div></div>
      <div class="data-table-wrap">
        <div class="data-table-header"><h3>Messages</h3><div class="table-filters">
          <button class="filter-btn ${!contactFilter?'active':''}" onclick="loadContacts(null)">All</button>
          ${fBtn('unread','Unread')}${fBtn('read','Read')}${fBtn('archived','Archived')}
        </div></div>
        <table class="data-table"><thead><tr><th>Name</th><th>Subject</th><th>Status</th><th>Date</th><th>Actions</th></tr></thead>
        <tbody>${rows || '<tr><td colspan="5" class="table-empty">No messages found</td></tr>'}</tbody></table></div>`;
  } catch(e) { area.innerHTML = '<p style="color:var(--danger);padding:2rem">Failed to load contacts</p>'; }
}

async function viewContact(id) {
  const res = await Auth.api(`/api/contacts/${id}`);
  if (!res.ok) return;
  const c = await res.json();
  const date = new Date(c.created_at).toLocaleString('en-GB');
  openModal('Message Details', `
    <div class="contact-view-header"><h3>${esc(c.subject)}</h3>
      <div class="contact-view-meta"><span>From: <strong>${esc(c.name)}</strong></span><span>${esc(c.email)}</span><span>${date}</span></div>
    </div><div class="contact-view-body">${esc(c.message)}</div>
    <div class="modal-actions" style="margin-top:1rem">
      <button class="btn-secondary" onclick="closeModal()">Close</button>
      <a href="mailto:${esc(c.email)}?subject=Re: ${encodeURIComponent(c.subject)}" class="btn-primary-dash" style="text-decoration:none">Reply via Email</a>
    </div>`);
  if (!c.is_read) { await Auth.api(`/api/contacts/${id}/read`, { method:'PUT' }); loadUnreadCount(); }
}

async function markRead(id) {
  await Auth.api(`/api/contacts/${id}/read`, { method:'PUT' });
  toast('Marked as read'); loadContacts(); loadUnreadCount();
}
async function archiveContact(id) {
  await Auth.api(`/api/contacts/${id}/archive`, { method:'PUT' });
  toast('Archived'); loadContacts(); loadUnreadCount();
}
async function deleteContact(id) {
  if (!confirm('Delete this message?')) return;
  await Auth.api(`/api/contacts/${id}`, { method:'DELETE' });
  toast('Deleted'); loadContacts(); loadUnreadCount();
}

/* ── EVENTS ────────────────────────────────────── */
async function loadEvents() {
  const area = document.getElementById('contentArea');
  try {
    const res = await Auth.api('/api/events/');
    const events = await res.json();
    let cards = '';
    events.forEach(ev => {
      const imgHtml = ev.image_url
        ? `<div class="event-dash-img"><img src="${esc(ev.image_url)}" alt="${esc(ev.title)}"></div>`
        : `<div class="event-dash-img">No image</div>`;
      const status = ev.is_published ? 'published' : 'draft';
      cards += `<div class="event-dash-card">
        ${imgHtml}
        <div class="event-dash-body">
          <h4>${esc(ev.title)}</h4>
          <p>${esc(ev.description)}</p>
          <div class="event-dash-meta">
            <span class="status-badge status-badge--${status}"><span class="status-dot"></span>${status}</span>
            <span class="event-dash-date">${esc(ev.event_date||'')}</span>
          </div>
          <div class="action-btns" style="margin-top:0.75rem">
            <button class="action-btn" onclick="editEvent(${ev.id})" title="Edit"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg></button>
            <button class="action-btn" onclick="uploadEventImage(${ev.id})" title="Upload image">📷</button>
            <button class="action-btn action-btn--danger" onclick="deleteEvent(${ev.id})" title="Delete">✕</button>
          </div>
        </div>
      </div>`;
    });
    area.innerHTML = `
      <div class="page-header"><div><h1>Events</h1><p>Manage fashion events, insights & opportunities</p></div>
        <div class="header-actions"><button class="btn-primary-dash" onclick="showEventForm()">+ New Event</button></div></div>
      <div class="events-card-grid">${cards || '<div class="table-empty" style="grid-column:1/-1">No events yet. Create your first event!</div>'}</div>`;
  } catch(e) { area.innerHTML = '<p style="color:var(--danger);padding:2rem">Failed to load events</p>'; }
}

function showEventForm(ev = null) {
  const isEdit = !!ev;
  const badges = ['Featured','Past Event','Internal Spotlight','Upcoming'];
  const badgeOpts = badges.map(b => `<option value="${b}" ${ev?.badge===b?'selected':''}>${b}</option>`).join('');
  openModal(isEdit ? 'Edit Event' : 'New Event', `
    <form class="modal-form" id="eventModalForm">
      <div class="form-group"><label>Title</label><input type="text" id="evTitle" value="${esc(ev?.title||'')}" required></div>
      <div class="form-group"><label>Description</label><textarea id="evDesc" rows="3" required>${esc(ev?.description||'')}</textarea></div>
      <div class="form-row">
        <div class="form-group"><label>Date</label><input type="text" id="evDate" value="${esc(ev?.event_date||'')}" placeholder="e.g. Spring 2026"></div>
        <div class="form-group"><label>Badge</label><select id="evBadge"><option value="">None</option>${badgeOpts}</select></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>Author</label><input type="text" id="evAuthor" value="${esc(ev?.author||'')}"></div>
        <div class="form-group"><label>Location</label><input type="text" id="evLocation" value="${esc(ev?.location||'')}"></div>
      </div>
      <div class="form-group"><label>External Link</label><input type="url" id="evLink" value="${esc(ev?.external_link||'')}" placeholder="https://…"></div>
      <div class="form-group"><label>Link Text</label><input type="text" id="evLinkText" value="${esc(ev?.link_text||'View details')}"></div>
      <div class="form-group"><label>Event Image</label>
        <input type="hidden" id="evImageUrl" value="${esc(ev?.image_url||'')}">
        <div class="image-upload-area" id="evDropZone">
          <input type="file" id="evImageInput" accept="image/*">
          <div class="upload-icon"><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg></div>
          <p class="upload-text">Drag & drop or <strong>click to browse</strong></p>
        </div>
        <div id="evImgPreview" class="image-preview" style="${ev?.image_url?'':'display:none'}">${ev?.image_url?`<img src="${esc(ev.image_url)}"><button type="button" class="image-preview-remove" onclick="removeEvPreview()">&times;</button>`:''}</div>
      </div>
      <div class="form-group"><label><input type="checkbox" id="evPublished" ${ev?.is_published?'checked':''}> Publish</label></div>
      <div class="modal-actions">
        <button type="button" class="btn-secondary" onclick="closeModal()">Cancel</button>
        <button type="submit" class="btn-primary-dash">${isEdit?'Update':'Create'} Event</button>
      </div>
    </form>`);
  document.getElementById('eventModalForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const body = {
      title: document.getElementById('evTitle').value,
      description: document.getElementById('evDesc').value,
      event_date: document.getElementById('evDate').value || null,
      badge: document.getElementById('evBadge').value || null,
      author: document.getElementById('evAuthor').value || null,
      location: document.getElementById('evLocation').value || null,
      external_link: document.getElementById('evLink').value || null,
      link_text: document.getElementById('evLinkText').value || 'View details',
      image_url: document.getElementById('evImageUrl').value || null,
      is_published: document.getElementById('evPublished').checked,
    };
    const url = isEdit ? `/api/events/${ev.id}` : '/api/events/';
    const res = await Auth.api(url, { method: isEdit?'PUT':'POST', body });
    if (res.ok) { closeModal(); toast(isEdit?'Event updated':'Event created'); loadEvents(); }
    else { const err = await res.json(); toast(err.detail||'Error','error'); }
  });

  // Inline image upload in event form
  const evFileInput = document.getElementById('evImageInput');
  const evDropZone = document.getElementById('evDropZone');
  const evPreview = document.getElementById('evImgPreview');
  const evImgField = document.getElementById('evImageUrl');

  async function handleEvFile(file) {
    if (!file || !file.type.startsWith('image/')) return;
    const fd = new FormData(); fd.append('file', file);
    evDropZone.querySelector('.upload-text').innerHTML = 'Uploading…';
    try {
      const res = await Auth.api('/api/events/upload-image', { method:'POST', body: fd });
      if (res.ok) {
        const data = await res.json();
        evImgField.value = data.image_url;
        evPreview.innerHTML = `<img src="${data.image_url}"><button type="button" class="image-preview-remove" onclick="removeEvPreview()">&times;</button>`;
        evPreview.style.display = 'block';
        evDropZone.querySelector('.upload-text').innerHTML = 'Image uploaded ✓ — drag another to replace';
      } else {
        evDropZone.querySelector('.upload-text').innerHTML = 'Upload failed — try again';
      }
    } catch(e) {
      evDropZone.querySelector('.upload-text').innerHTML = 'Upload failed — try again';
    }
  }
  if (evFileInput) evFileInput.addEventListener('change', (e) => handleEvFile(e.target.files[0]));
  if (evDropZone) {
    evDropZone.addEventListener('dragover', (e) => { e.preventDefault(); evDropZone.classList.add('dragover'); });
    evDropZone.addEventListener('dragleave', () => evDropZone.classList.remove('dragover'));
    evDropZone.addEventListener('drop', (e) => { e.preventDefault(); evDropZone.classList.remove('dragover'); handleEvFile(e.dataTransfer.files[0]); });
  }
}

function removeEvPreview() {
  document.getElementById('evImageUrl').value = '';
  const preview = document.getElementById('evImgPreview');
  preview.innerHTML = ''; preview.style.display = 'none';
}

async function editEvent(id) {
  const res = await Auth.api(`/api/events/${id}`);
  if (res.ok) showEventForm(await res.json());
}

async function deleteEvent(id) {
  if (!confirm('Delete this event?')) return;
  const res = await Auth.api(`/api/events/${id}`, { method:'DELETE' });
  if (res.ok) { toast('Event deleted'); loadEvents(); }
}

function uploadEventImage(id) {
  openModal('Upload Event Image', `
    <div class="image-upload-area" id="dropZone">
      <input type="file" id="imageFileInput" accept="image/*">
      <div class="upload-icon"><svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg></div>
      <p class="upload-text">Drag & drop or <strong>click to browse</strong></p>
    </div>
    <div id="imgPreview" class="image-preview" style="display:none"></div>
    <div class="modal-actions" style="margin-top:1rem">
      <button class="btn-secondary" onclick="closeModal()">Cancel</button>
      <button class="btn-primary-dash" id="uploadBtn" disabled onclick="doUpload(${id})">Upload</button>
    </div>`);
  let selectedFile = null;
  const fileInput = document.getElementById('imageFileInput');
  const dropZone = document.getElementById('dropZone');
  const preview = document.getElementById('imgPreview');

  function handleFile(file) {
    if (!file || !file.type.startsWith('image/')) return;
    selectedFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      preview.innerHTML = `<img src="${e.target.result}">`;
      preview.style.display = 'block';
    };
    reader.readAsDataURL(file);
    document.getElementById('uploadBtn').disabled = false;
  }

  fileInput.addEventListener('change', (e) => handleFile(e.target.files[0]));
  dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('dragover'); });
  dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
  dropZone.addEventListener('drop', (e) => { e.preventDefault(); dropZone.classList.remove('dragover'); handleFile(e.dataTransfer.files[0]); });

  window._uploadFile = selectedFile;
  window.doUpload = async function(eventId) {
    if (!selectedFile && !fileInput.files[0]) return;
    const f = selectedFile || fileInput.files[0];
    const fd = new FormData();
    fd.append('file', f);
    const btn = document.getElementById('uploadBtn');
    btn.disabled = true; btn.textContent = 'Uploading…';
    const res = await Auth.api(`/api/events/${eventId}/upload-image`, { method:'POST', body: fd });
    if (res.ok) { closeModal(); toast('Image uploaded'); loadEvents(); }
    else { toast('Upload failed','error'); btn.disabled = false; btn.textContent = 'Upload'; }
  };
}

function esc(str) {
  if (!str) return '';
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// Init on load
document.addEventListener('DOMContentLoaded', () => {
  if (Auth.isLoggedIn()) initDashboard();
});
window.addEventListener('hashchange', () => {
  const page = window.location.hash.replace('#/', '') || 'overview';
  if (page !== currentPage) navigateTo(page);
});
