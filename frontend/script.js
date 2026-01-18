// Constants
const API_BASE = '/api' // Relative to current host
let currentTaskId = null
let statusInterval = null

// DOM Elements
const loginView = document.getElementById('login-view')
const dashboardView = document.getElementById('dashboard-view')
const loginForm = document.getElementById('login-form')
const authTypeSelect = document.getElementById('auth-type')
const emailFields = document.getElementById('email-fields')
const phoneFields = document.getElementById('phone-fields')
const submitBtn = document.getElementById('submit-btn')
const refreshBtn = document.getElementById('refresh-btn')
const cancelBtn = document.getElementById('cancel-btn')
const backBtn = document.getElementById('back-btn')

// Status elements
const statusIcon = document.getElementById('status-icon')
const statusText = document.getElementById('status-text')
const progressBar = document.getElementById('progress-bar')
const progressText = document.getElementById('progress-text')
const taskIdSpan = document.getElementById('task-id')
const stageSpan = document.getElementById('stage')
const appliedSpan = document.getElementById('applied')
const totalSpan = document.getElementById('total')
const statusError = document.getElementById('status-error')

// Initialize
document.addEventListener('DOMContentLoaded', () => {
	setupEventListeners()
	showView('login-view')
})

// Event Listeners
function setupEventListeners() {
	authTypeSelect.addEventListener('change', toggleAuthFields)
	loginForm.addEventListener('submit', handleSubmit)
	refreshBtn.addEventListener('click', () => getStatus(currentTaskId))
	cancelBtn.addEventListener('click', () => cancelJob(currentTaskId))
	backBtn.addEventListener('click', () => {
		clearInterval(statusInterval)
		showView('login-view')
		resetForm()
	})
}

// View Management
function showView(viewId) {
	document
		.querySelectorAll('.view')
		.forEach((view) => view.classList.remove('active'))
	document.getElementById(viewId).classList.add('active')
}

function toggleAuthFields() {
	const authType = authTypeSelect.value
	if (authType === 'email') {
		emailFields.classList.remove('hidden')
		phoneFields.classList.add('hidden')
	} else {
		emailFields.classList.add('hidden')
		phoneFields.classList.remove('hidden')
	}
}

// Form Handling
function handleSubmit(e) {
	e.preventDefault()
	if (!validateForm()) return

	const formData = getFormData()
	submitJob(formData)
}

function validateForm() {
	let isValid = true
	const authType = authTypeSelect.value

	// Clear previous errors
	document.querySelectorAll('.error-message').forEach((el) => {
		el.style.display = 'none'
		el.textContent = ''
	})

	// Validate required fields
	const requiredFields = ['password', 'search-query', 'max-applications']
	if (authType === 'email') {
		requiredFields.push('email')
	} else {
		requiredFields.push('phone')
	}

	requiredFields.forEach((field) => {
		const element = document.getElementById(field)
		if (!element.value.trim()) {
			showError(`${field}-error`, 'This field is required')
			isValid = false
		}
	})

	// Validate email format
	if (authType === 'email') {
		const email = document.getElementById('email').value
		const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
		if (!emailRegex.test(email)) {
			showError('email-error', 'Please enter a valid email address')
			isValid = false
		}
	}

	// Validate phone format
	if (authType === 'phone') {
		const phone = document.getElementById('phone').value
		const phoneRegex = /^\d{9,12}$/
		if (!phoneRegex.test(phone)) {
			showError('phone-error', 'Phone must be 9-12 digits')
			isValid = false
		}
	}

	// Validate password length
	const password = document.getElementById('password').value
	if (password.length < 2) {
		showError('password-error', 'Password must be at least 2 characters')
		isValid = false
	}

	// Validate max applications
	const maxApps = parseInt(document.getElementById('max-applications').value)
	if (maxApps < 1 || maxApps > 200) {
		showError('max-error', 'Must be between 1 and 200')
		isValid = false
	}

	return isValid
}

function getFormData() {
	const authType = authTypeSelect.value
	const data = {
		search_query: document.getElementById('search-query').value,
		max_applications: parseInt(
			document.getElementById('max-applications').value,
		),
		answer_req: document.getElementById('answer-req').value,
	}

	if (authType === 'email') {
		data.email = document.getElementById('email').value
		data.password = document.getElementById('password').value
	} else {
		data.phone = document.getElementById('phone').value
		data.country = document.getElementById('country').value
		data.password = document.getElementById('password').value
	}

	return data
}

function resetForm() {
	loginForm.reset()
	toggleAuthFields()
	document.querySelectorAll('.error-message').forEach((el) => {
		el.style.display = 'none'
	})
}

// API Calls
async function submitJob(data) {
	submitBtn.disabled = true
	submitBtn.textContent = 'Submitting...'

	try {
		const endpoint = data.email ? '/jobs/submit/email' : '/jobs/submit/phone'
		const response = await fetch(`${API_BASE}${endpoint}`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify(data),
		})

		const result = await response.json()

		if (response.ok) {
			currentTaskId = result.task_id
			showView('dashboard-view')
			startStatusPolling()
		} else {
			showError('query-error', result.detail || 'Submission failed')
		}
	} catch (error) {
		console.error('Submit error:', error)
		showError('query-error', 'Network error. Please try again.')
	} finally {
		submitBtn.disabled = false
		submitBtn.textContent = 'Start Parsing'
	}
}

async function getStatus(taskId) {
	if (!taskId) return

	try {
		const response = await fetch(`${API_BASE}/jobs/${taskId}`)
		const data = await response.json()

		if (response.ok) {
			updateStatus(data)
		} else {
			showStatusError(data.detail || 'Failed to get status')
		}
	} catch (error) {
		console.error('Status error:', error)
		showStatusError('Network error')
	}
}

async function cancelJob(taskId) {
	if (!taskId) return

	try {
		const response = await fetch(`${API_BASE}/jobs/${taskId}/cancel`, {
			method: 'POST',
		})
		const data = await response.json()

		if (response.ok) {
			clearInterval(statusInterval)
			updateStatus({ state: 'CANCELLED', progress: 0 })
		} else {
			showStatusError(data.detail || 'Failed to cancel')
		}
	} catch (error) {
		console.error('Cancel error:', error)
		showStatusError('Network error')
	}
}

// Status Management
function startStatusPolling() {
	getStatus(currentTaskId)
	statusInterval = setInterval(() => getStatus(currentTaskId), 2000) // Poll every 2 seconds
}

function updateStatus(data) {
	statusError.style.display = 'none'
	taskIdSpan.textContent = data.task_id

	// Check if result contains error status
	const isErrorStatus =
		data.result &&
		['captcha required', 'invalid credentials', 'error'].includes(
			data.result.status,
		)

	if (isErrorStatus) {
		statusText.textContent = getStatusText(data.result.status)
		updateStatusIcon(data.result.status)
		showStatusError(
			data.result.message || 'An error occurred during processing',
		)
		clearInterval(statusInterval)
	} else {
		statusText.textContent = getStatusText(data.state)
		updateStatusIcon(data.state)
	}

	const progress = data.progress || 0
	progressBar.style.width = `${progress}%`
	progressText.textContent = `${Math.round(progress)}%`

	if (data.stage) stageSpan.textContent = data.stage
	if (data.applied !== undefined) appliedSpan.textContent = data.applied
	if (data.total !== undefined) totalSpan.textContent = data.total

	if (data.state === 'SUCCESS' || data.state === 'FAILURE' || isErrorStatus) {
		clearInterval(statusInterval)
	}
}

function getStatusText(state) {
	switch (state) {
		case 'PENDING':
			return 'In Queue'
		case 'PROGRESS':
			return 'Processing'
		case 'SUCCESS':
			return 'Completed'
		case 'FAILURE':
			return 'Failed'
		case 'captcha required':
			return 'Captcha Required'
		case 'invalid credentials':
			return 'Invalid Credentials'
		case 'error':
			return 'Error'
		default:
			return state
	}
}

function updateStatusIcon(state) {
	statusIcon.className = 'status-icon fas'
	switch (state) {
		case 'PENDING':
			statusIcon.classList.add('fa-clock')
			statusIcon.style.color = '#f39c12'
			break
		case 'PROGRESS':
			statusIcon.classList.add('fa-spinner', 'fa-spin')
			statusIcon.style.color = '#3498db'
			break
		case 'SUCCESS':
			statusIcon.classList.add('fa-check-circle')
			statusIcon.style.color = '#27ae60'
			break
		case 'FAILURE':
		case 'captcha required':
		case 'invalid credentials':
		case 'error':
			statusIcon.classList.add('fa-times-circle')
			statusIcon.style.color = '#e74c3c'
			break
		default:
			statusIcon.classList.add('fa-question-circle')
			statusIcon.style.color = '#95a5a6'
	}
}

function showError(elementId, message) {
	const element = document.getElementById(elementId)
	element.textContent = message
	element.style.display = 'block'
}

function showStatusError(message) {
	statusError.textContent = message
	statusError.style.display = 'block'
}
