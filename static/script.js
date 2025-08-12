// Global variables
let currentSessionId = '';
let currentQuestion = null;
let currentAnswer = '';
let enhancedQuestions = [];
let assessmentAnswers = {};

// Function to update current answer in real-time
function updateCurrentAnswer(value) {
    currentAnswer = value;
    console.log('Current answer updated to:', currentAnswer);
}

// Tab switching functionality
function showTab(tabName) {
    // Hide all tab contents
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => content.classList.remove('active'));
    
    // Remove active class from all tab buttons
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => btn.classList.remove('active'));
    
    // Show selected tab content
    document.getElementById(tabName).classList.add('active');
    
    // Add active class to clicked button
    event.target.classList.add('active');
}

// Enhanced Assessment Functions
async function startEnhancedAssessment() {
    const sessionId = document.getElementById('session-id').value;
    if (!sessionId) {
        alert('Please enter a session ID');
        return;
    }
    
    currentSessionId = sessionId;
    
    try {
        // Load the enhanced questions
        const response = await fetch('/get-enhanced-questions', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('Enhanced questions response:', result);
            
            // Handle the BaseResponse structure
            if (result.data && result.data.questions) {
                enhancedQuestions = result.data.questions;
                console.log('Loaded questions:', enhancedQuestions.length);
                showEnhancedAssessment();
            } else if (result.questions) {
                // Direct response structure
                enhancedQuestions = result.questions;
                console.log('Loaded questions:', enhancedQuestions.length);
                showEnhancedAssessment();
            } else {
                console.error('Unexpected response structure:', result);
                alert('Error: Unexpected response structure from server');
            }
        } else {
            const error = await response.json();
            alert('Error loading questions: ' + (error.detail || error.message || 'Unknown error'));
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

function showEnhancedAssessment() {
    const container = document.getElementById('enhanced-assessment-container');
    const questionsContainer = document.getElementById('all-questions-container');
    
    console.log('Showing enhanced assessment with questions:', enhancedQuestions);
    
    // Check if questions are loaded
    if (!enhancedQuestions || !Array.isArray(enhancedQuestions) || enhancedQuestions.length === 0) {
        console.error('No questions loaded:', enhancedQuestions);
        alert('Error: No questions loaded. Please try again.');
        return;
    }
    
    // Hide the old question container
    document.getElementById('question-container').style.display = 'none';
    
    // Show the enhanced assessment container
    container.style.display = 'block';
    
    // Generate HTML for all questions
    let questionsHtml = '';
    
    enhancedQuestions.forEach((question, index) => {
        const questionId = `question-${index}`;
        const categoryName = question.category || 'General';
        
        questionsHtml += `
            <div class="question-section" data-category="${question.category_key}">
                <h4 class="category-title">${categoryName}</h4>
                <div class="question-card">
                    <div class="question-text">
                        <strong>${index + 1}. ${question.question}</strong>
                        ${question.required ? '<span class="required-mark">*</span>' : ''}
                    </div>
                    <div class="answer-input">
                        ${generateAnswerInput(question, questionId)}
                    </div>
                </div>
            </div>
        `;
    });
    
    questionsContainer.innerHTML = questionsHtml;
}

function generateAnswerInput(question, questionId) {
    if (question.type === 'multiple_choice' && question.options && question.options.length > 0) {
        let optionsHtml = '';
        question.options.forEach((option, optionIndex) => {
            const optionId = `${questionId}-option-${optionIndex}`;
            if (option.toLowerCase() === 'other') {
                optionsHtml += `
                    <div class="answer-option">
                        <label>
                            <input type="radio" name="${questionId}" value="other" onchange="handleOtherOption('${questionId}')">
                            Other
                        </label>
                        <div class="other-input" id="other-input-${questionId}" style="display: none;">
                            <input type="text" placeholder="Please specify..." class="form-control" oninput="updateAnswer('${questionId}', this.value)" onfocus="console.log('Other input focused for:', '${questionId}')">
                        </div>
                    </div>
                `;
            } else {
                optionsHtml += `
                    <div class="answer-option">
                        <label>
                            <input type="radio" name="${questionId}" value="${option}" onchange="handleRadioChange('${questionId}', '${option}')">
                            ${option}
                        </label>
                    </div>
                `;
            }
        });
        return `<div class="answer-options">${optionsHtml}</div>`;
    } else {
        return `<input type="text" class="form-control" placeholder="Enter your answer" oninput="updateAnswer('${questionId}', this.value)">`;
    }
}

function handleOtherOption(questionId) {
    console.log('Handling other option for:', questionId);
    console.log('Looking for element with ID:', `other-input-${questionId}`);
    
    const otherInput = document.getElementById(`other-input-${questionId}`);
    console.log('Found other input element:', otherInput);
    
    if (otherInput) {
        console.log('Setting display to block');
        otherInput.style.display = 'block';
        const textInput = otherInput.querySelector('input');
        console.log('Found text input:', textInput);
        if (textInput) {
            textInput.focus();
            // Clear any previous answer for this question
            assessmentAnswers[questionId] = '';
        }
    } else {
        console.error('Other input not found for:', questionId);
        // Let's also check if the element exists with a different approach
        const allOtherInputs = document.querySelectorAll('.other-input');
        console.log('All other inputs found:', allOtherInputs.length);
        allOtherInputs.forEach((input, index) => {
            console.log(`Other input ${index}:`, input.id);
        });
    }
}

function handleRadioChange(questionId, value) {
    console.log('Handling radio change for:', questionId, 'value:', value);
    
    // Hide any "Other" text input for this question
    const otherInput = document.getElementById(`other-input-${questionId}`);
    if (otherInput) {
        otherInput.style.display = 'none';
        // Clear the text input
        const textInput = otherInput.querySelector('input');
        if (textInput) {
            textInput.value = '';
        }
    }
    
    // Update the answer
    assessmentAnswers[questionId] = value;
}

function updateAnswer(questionId, value) {
    assessmentAnswers[questionId] = value;
    console.log('Updated answer for', questionId, ':', value);
}

async function completeAssessment() {
    // Collect all answers
    const answers = [];
    
    enhancedQuestions.forEach((question, index) => {
        const questionId = `question-${index}`;
        const answer = assessmentAnswers[questionId] || '';
        
        if (answer.trim() !== '') {
            answers.push({
                question_id: question.id || index.toString(),
                question: question.question,
                answer: answer,
                category: question.category,
                category_key: question.category_key
            });
        }
    });
    
    if (answers.length === 0) {
        alert('Please answer at least one question before completing the assessment.');
        return;
    }
    
    try {
        const response = await fetch('/complete-enhanced-assessment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: currentSessionId,
                answers: answers
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            showEnhancedResults(result);
        } else {
            const error = await response.json();
            alert('Error completing assessment: ' + error.detail);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

function showEnhancedResults(result) {
    console.log('Showing enhanced results:', result);
    
    const container = document.getElementById('enhanced-assessment-container');
    const questionsContainer = document.getElementById('all-questions-container');
    
    // Hide questions and show results
    questionsContainer.style.display = 'none';
    const assessmentActions = document.querySelector('.assessment-actions');
    if (assessmentActions) {
        assessmentActions.style.display = 'none';
    }
    
    // Handle the BaseResponse structure
    let assessmentText = 'Assessment results will be displayed here.';
    if (result.data && result.data.assessment) {
        assessmentText = result.data.assessment;
    } else if (result.assessment) {
        assessmentText = result.assessment;
    }
    
    const resultsHtml = `
        <div class="assessment-results">
            <h3>🎉 Enhanced Assessment Complete!</h3>
            <div class="results-content">
                ${assessmentText}
            </div>
            <div class="results-actions">
                <button onclick="downloadResults()" class="btn btn-info">📥 Download Results</button>
                <button onclick="resetAssessment()" class="btn btn-warning">🔄 Start New Assessment</button>
            </div>
        </div>
    `;
    
    container.innerHTML = resultsHtml;
}

function saveProgress() {
    localStorage.setItem('45q_assessment_progress', JSON.stringify({
        sessionId: currentSessionId,
        answers: assessmentAnswers,
        timestamp: new Date().toISOString()
    }));
    alert('Progress saved! You can continue later.');
}

function resetAssessment() {
    assessmentAnswers = {};
    enhancedQuestions = [];
    document.getElementById('enhanced-assessment-container').style.display = 'none';
    document.getElementById('eligibility-form').reset();
    localStorage.removeItem('45q_assessment_progress');
}

function downloadResults() {
    // Implementation for downloading results
    alert('Download functionality will be implemented here.');
}

// Original Assessment Functions
async function startAssessment() {
    const sessionId = document.getElementById('session-id').value;
    if (!sessionId) {
        alert('Please enter a session ID');
        return;
    }
    
    currentSessionId = sessionId;
    
    try {
        const response = await fetch('/assess-eligibility', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ session_id: sessionId })
        });
        
        if (response.ok) {
            const result = await response.json();
            showQuestion(result);
        } else {
            const error = await response.json();
            alert('Error starting assessment: ' + error.detail);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

function showQuestion(assessmentData) {
    const questionContainer = document.getElementById('question-container');
    const currentQuestionDiv = document.getElementById('current-question');
    const answerInputDiv = document.getElementById('answer-input');
    const questionNumberSpan = document.getElementById('question-number');
    const totalQuestionsSpan = document.getElementById('total-questions');
    
    if (assessmentData.current_question) {
        currentQuestion = assessmentData.current_question;
        
        // Show question container
        questionContainer.style.display = 'block';
        
        // Update question number display
        if (assessmentData.current_question_index !== undefined) {
            const questionIndex = assessmentData.current_question_index + 1; // +1 because index is 0-based
            questionNumberSpan.textContent = questionIndex;
            console.log('Updated question number to:', questionIndex, 'from index:', assessmentData.current_question_index);
        }
        
        // Update total questions if available
        if (assessmentData.total_questions) {
            totalQuestionsSpan.textContent = assessmentData.total_questions;
            console.log('Updated total questions to:', assessmentData.total_questions);
        }
        
        // Display question
        currentQuestionDiv.innerHTML = `
            <div class="question-card">
                <div class="question-text">${currentQuestion.question}</div>
                ${currentQuestion.help_text ? `<p class="help-text"><em>${currentQuestion.help_text}</em></p>` : ''}
            </div>
        `;
        
        // Create answer input based on question type
        if (currentQuestion.type === 'select' && currentQuestion.options) {
            let optionsHtml = '';
            
            // Add regular options
            currentQuestion.options.forEach(option => {
                if (option.toLowerCase() === 'other') {
                    // Add "Other" option with text input
                    optionsHtml += `
                        <div class="answer-option">
                            <label>
                                <input type="radio" name="answer" value="other" onchange="toggleOtherInput()">
                                Other
                            </label>
                        </div>
                        <div class="other-input" id="other-input">
                            <input type="text" id="other-text" placeholder="Please specify..." class="form-control" oninput="updateCurrentAnswer(this.value)">
                        </div>
                    `;
                } else {
                    optionsHtml += `
                        <div class="answer-option">
                            <label>
                                <input type="radio" name="answer" value="${option}" onchange="updateCurrentAnswer('${option}')">
                                ${option}
                            </label>
                        </div>
                    `;
                }
            });
            
            answerInputDiv.innerHTML = `
                <div class="answer-options">
                    ${optionsHtml}
                </div>
            `;
        } else if (currentQuestion.type === 'text') {
            answerInputDiv.innerHTML = `
                <input type="text" id="answer-field" placeholder="Enter your answer" class="form-control" oninput="updateCurrentAnswer(this.value)">
            `;
        } else if (currentQuestion.type === 'number') {
            answerInputDiv.innerHTML = `
                <input type="number" id="answer-field" placeholder="Enter number" class="form-control" oninput="updateCurrentAnswer(this.value)">
            `;
        } else if (currentQuestion.type === 'date') {
            answerInputDiv.innerHTML = `
                <input type="date" id="answer-field" class="form-control" oninput="updateCurrentAnswer(this.value)">
            `;
        } else if (currentQuestion.type === 'boolean') {
            answerInputDiv.innerHTML = `
                <div class="answer-options">
                    <div class="answer-option">
                        <label>
                            <input type="radio" name="answer" value="true" onchange="updateCurrentAnswer('true')">
                            Yes
                        </label>
                    </div>
                    <div class="answer-option">
                        <label>
                            <input type="radio" name="answer" value="false" onchange="updateCurrentAnswer('false')">
                            No
                        </label>
                    </div>
                </div>
            `;
        }
        
        // Update progress
        updateProgress(assessmentData.progress);
        
    } else {
        // Assessment complete
        showResults(assessmentData);
    }
}

function selectOption(option) {
    // Remove previous selection
    document.querySelectorAll('.answer-option').forEach(opt => opt.classList.remove('selected'));
    
    // Select current option
    event.target.classList.add('selected');
    currentAnswer = option;
}

async function submitAnswer() {
    // Get the answer based on question type
    if (currentQuestion.type === 'text' || currentQuestion.type === 'number' || currentQuestion.type === 'date') {
        const answerField = document.getElementById('answer-field');
        if (answerField) {
            currentAnswer = answerField.value;
        }
    }
    
    if (!currentAnswer || currentAnswer.trim() === '') {
        alert('Please provide an answer');
        return;
    }
    
    console.log('Submitting answer:', currentAnswer, 'for question:', currentQuestion.id);
    
    try {
        const response = await fetch('/submit-answer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: currentSessionId,
                question_id: currentQuestion.id,
                answer: currentAnswer
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            currentAnswer = '';
            
            if (result.is_complete) {
                showResults(result);
            } else {
                // Get the current question to display
                const currentQuestionResponse = await fetch(`/assessment-progress/${currentSessionId}`);
                if (currentQuestionResponse.ok) {
                    const progressData = await currentQuestionResponse.json();
                    // Update the question display with progress information
                    const questionData = {
                        current_question: result.current_question,
                        current_question_index: progressData.data.current_question_index,
                        total_questions: progressData.data.total_questions,
                        progress: progressData.data.progress
                    };
                    showQuestion(questionData);
                }
            }
        } else {
            const error = await response.json();
            alert('Error submitting answer: ' + error.detail);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

function showResults(assessmentData) {
    document.getElementById('question-container').style.display = 'none';
    document.getElementById('eligibility-results').style.display = 'block';
    
    const resultsContent = document.getElementById('results-content');
    resultsContent.innerHTML = `
        <div class="results-card">
            <h4>Assessment Complete!</h4>
            <p>Session ID: ${assessmentData.session_id}</p>
            <p>Progress: 100%</p>
        </div>
    `;
}

async function getDetailedGuidance() {
    try {
        const response = await fetch(`/detailed-guidance/${currentSessionId}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            const result = await response.json();
            displayDetailedGuidance(result.data);
        } else {
            const error = await response.json();
            alert('Error getting guidance: ' + error.detail);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

function displayDetailedGuidance(guidance) {
    const resultsContent = document.getElementById('results-content');
    
    let guidanceHtml = '<div class="results-card">';
    
    if (guidance.rag_guidance && guidance.rag_guidance.answer) {
        guidanceHtml += `
            <h4>🤖 AI Analysis</h4>
            <p>${guidance.rag_guidance.answer}</p>
            <div class="confidence-score">Confidence: ${(guidance.rag_guidance.confidence_score * 100).toFixed(1)}%</div>
        `;
    }
    
    if (guidance.facility_info) {
        guidanceHtml += `
            <h4>🏭 Facility Information</h4>
            <p><strong>Name:</strong> ${guidance.facility_info.facility_name}</p>
            <p><strong>Type:</strong> ${guidance.facility_info.facility_type}</p>
            <p><strong>Location:</strong> ${guidance.facility_info.location_state}</p>
            <p><strong>Annual CO2 Capture:</strong> ${guidance.facility_info.annual_co2_captured} metric tons</p>
        `;
    }
    
    guidanceHtml += '</div>';
    
    resultsContent.innerHTML = guidanceHtml;
}

function updateProgress(progress) {
    const progressFill = document.getElementById('progress-fill');
    const progressPercent = progress * 100;
    progressFill.style.width = progressPercent + '%';
}

// Credit Forecasting Functions
document.getElementById('forecast-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    console.log('Forecast form submitted');
    
    const formData = {
        session_id: currentSessionId || 'forecast-session',
        facility_info: {
            facility_type: document.getElementById('facility-type').value,
            location: 'Texas',
            ownership: 'Private',
            technology_ownership: 'Owned'
        },
        annual_co2_captured: parseFloat(document.getElementById('annual-co2').value),
        capture_efficiency: parseFloat(document.getElementById('capture-efficiency').value) / 100,
        sequestration_method: document.getElementById('sequestration-method').value,
        sequestration_location: 'Texas',
        start_date: document.getElementById('start-date').value,
        domestic_content_percentage: parseFloat(document.getElementById('domestic-content').value),
        energy_community_eligible: document.getElementById('energy-community').checked
    };
    
    console.log('Form data:', formData);
    
    try {
        console.log('Sending request to /forecast-credits');
        const response = await fetch('/forecast-credits', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        console.log('Response status:', response.status);
        
        if (response.ok) {
            const result = await response.json();
            console.log('Forecast result:', result);
            displayForecastResults(result);
        } else {
            const error = await response.json();
            console.error('Forecast error:', error);
            alert('Error calculating forecast: ' + error.detail);
        }
    } catch (error) {
        console.error('Forecast exception:', error);
        alert('Error: ' + error.message);
    }
});

function displayForecastResults(result) {
    const forecastResults = document.getElementById('forecast-results');
    const forecastContent = document.getElementById('forecast-content');
    
    if (result.forecast) {
        const forecast = result.forecast;
        forecastContent.innerHTML = `
            <div class="forecast-card">
                <h4>💰 Credit Forecast Results</h4>
                <p><strong>Total Credits (10 years):</strong> $${forecast.total_credits_10_years?.toLocaleString() || 'N/A'}</p>
                <p><strong>Total Value (10 years):</strong> $${forecast.total_value_10_years?.toLocaleString() || 'N/A'}</p>
                <p><strong>Total Credits (12 years):</strong> $${forecast.total_credits_12_years?.toLocaleString() || 'N/A'}</p>
                <p><strong>Total Value (12 years):</strong> $${forecast.total_value_12_years?.toLocaleString() || 'N/A'}</p>
                <p><strong>Average Annual Credits:</strong> $${forecast.average_annual_credits?.toLocaleString() || 'N/A'}</p>
                <p><strong>Average Annual Value:</strong> $${forecast.average_annual_value?.toLocaleString() || 'N/A'}</p>
            </div>
        `;
    } else {
        forecastContent.innerHTML = `
            <div class="forecast-card">
                <h4>❌ Forecast Calculation Failed</h4>
                <p>Unable to calculate credits. Please check your inputs.</p>
            </div>
        `;
    }
    
    forecastResults.style.display = 'block';
}

// Ask Questions Functions
async function askQuestion() {
    const question = document.getElementById('question-input').value;
    if (!question.trim()) {
        alert('Please enter a question');
        return;
    }
    
    try {
        const response = await fetch(`/ask-question?question=${encodeURIComponent(question)}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            const result = await response.json();
            displayQuestionResults(result);
        } else {
            const error = await response.json();
            alert('Error asking question: ' + error.detail);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}



function displayQuestionResults(result) {
    const questionResults = document.getElementById('question-results');
    const answerContent = document.getElementById('answer-content');
    const confidenceScore = document.getElementById('confidence-score');
    const sources = document.getElementById('sources');
    
    answerContent.innerHTML = `
        <div class="answer-card">
            <h4>🤖 AI Response</h4>
            <p>${result.answer}</p>
        </div>
    `;
    
    confidenceScore.innerHTML = `
        <div class="confidence-score">Confidence: ${(result.confidence_score * 100).toFixed(1)}%</div>
    `;
    
    if (result.sources && result.sources.length > 0) {
        sources.innerHTML = `
            <div class="sources">
                <h4>📚 Sources</h4>
                ${result.sources.map(source => `
                    <div class="source-item">
                        <p>${source.content.substring(0, 200)}...</p>
                        <div class="source-meta">
                            <strong>File:</strong> ${source.metadata.file_name} | 
                            <strong>Page:</strong> ${source.metadata.page || 'N/A'}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    } else {
        sources.innerHTML = '';
    }
    
    questionResults.style.display = 'block';
}

// Document Upload Functions
async function uploadDocuments() {
    const fileInput = document.getElementById('file-upload');
    const files = fileInput.files;
    
    if (files.length === 0) {
        alert('Please select files to upload');
        return;
    }
    
    const formData = new FormData();
    for (let file of files) {
        formData.append('files', file);
    }
    
    try {
        const response = await fetch('/upload-documents', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const result = await response.json();
            displayUploadResults(result);
            refreshStats();
        } else {
            const error = await response.json();
            alert('Error uploading documents: ' + error.detail);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

function displayUploadResults(result) {
    const uploadResults = document.getElementById('upload-results');
    const uploadContent = document.getElementById('upload-content');
    
    uploadContent.innerHTML = `
        <div class="results-card">
            <h4>📊 Upload Results</h4>
            <p><strong>Documents Processed:</strong> ${result.documents_processed}</p>
            <p><strong>Total Chunks Created:</strong> ${result.total_chunks}</p>
            <p><strong>Vector DB Updated:</strong> ${result.vector_db_updated ? 'Yes' : 'No'}</p>
        </div>
    `;
    
    uploadResults.style.display = 'block';
}

async function refreshStats() {
    try {
        const response = await fetch('/vector-store-stats');
        if (response.ok) {
            const result = await response.json();
            const stats = result.data;
            
            document.getElementById('doc-count').textContent = stats.total_documents || '0';
            document.getElementById('chunk-count').textContent = stats.total_documents || '0';
        }
    } catch (error) {
        console.error('Error refreshing stats:', error);
    }
}

// Function to analyze documents and generate better questions
async function analyzeDocumentsForQuestions() {
    const questionInput = document.getElementById('question-input');
    if (!questionInput) return;
    
    const analysisPrompt = `Based on the 45Q tax credit documents in your knowledge base, analyze what questions we should ask clients to determine their eligibility. 

Please provide:
1. A comprehensive list of eligibility criteria questions
2. Follow-up questions that might be needed based on different facility types
3. Questions about specific requirements for different provisions
4. Any additional questions that would help determine qualification

Focus on making this interactive and thorough.`;

    questionInput.value = analysisPrompt;
    
    try {
        const response = await fetch('/ask-question', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: analysisPrompt
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('Document analysis for questions:', result);
            
            // Store the analysis for use in eligibility assessment
            window.documentAnalysis = result;
            
            // Show the analysis results
            const questionResults = document.getElementById('question-results');
            const answerContent = document.getElementById('answer-content');
            const confidenceScore = document.getElementById('confidence-score');
            const sources = document.getElementById('sources');
            
            if (questionResults) {
                questionResults.style.display = 'block';
                answerContent.innerHTML = `<div class="analysis-result">${result.answer}</div>`;
                
                if (result.confidence_score) {
                    confidenceScore.innerHTML = `<p><strong>Confidence:</strong> ${(result.confidence_score * 100).toFixed(1)}%</p>`;
                }
                
                if (result.sources && result.sources.length > 0) {
                    sources.innerHTML = `
                        <h4>Sources:</h4>
                        <ul>
                            ${result.sources.map(source => `<li>${source}</li>`).join('')}
                        </ul>
                    `;
                }
            }
        }
    } catch (error) {
        console.error('Error analyzing documents:', error);
    }
}

// Interactive eligibility assessment using LLM
async function startInteractiveAssessment() {
    const sessionId = document.getElementById('session-id').value;
    if (!sessionId) {
        alert('Please enter a session ID');
        return;
    }
    
    currentSessionId = sessionId;
    
    // Load the improved assessment prompt
    let assessmentPrompt = await loadAssessmentPrompt();
    
    // Start with a general question about the facility
    const initialQuestion = "I'm helping you determine eligibility for 45Q tax credits. To get started, can you tell me about your facility or project? What type of operation is this?";
    
    // Display the interactive chat interface
    showInteractiveChat(initialQuestion);
    
                    // Store the conversation and assessment prompt
                window.assessmentConversation = [{
                    role: 'assistant',
                    content: initialQuestion
                }];
                
                window.assessmentPrompt = assessmentPrompt;
                window.assessmentComplete = false; // Reset assessment complete flag
}

// Load the improved assessment prompt
async function loadAssessmentPrompt() {
    try {
        const response = await fetch('/assessment-prompt');
        if (response.ok) {
            const data = await response.json();
            return data.prompt;
        }
    } catch (error) {
        console.log('Could not load custom prompt, using default');
    }
    
    // Fallback to default improved prompt
    return `You are an expert 45Q tax credit eligibility assessor. Your job is to determine if a company qualifies for 45Q credits and provide a complete assessment.

IMPORTANT RULES:
- NEVER refer users to tax professionals or external consultants
- ALWAYS provide complete eligibility assessments when you have enough information
- Ask specific, targeted questions based on the 45Q regulations
- Continue asking questions until you can make a definitive determination
- Give comprehensive assessments with clear yes/no eligibility and reasoning

ASSESSMENT PROCESS:
1. Start with general facility information
2. Ask targeted follow-up questions based on responses
3. Continue until you have enough information for a complete assessment
4. Provide a definitive eligibility determination with:
   - Eligible: Yes/No
   - Reasoning based on 45Q regulations
   - Specific provisions that apply
   - Estimated credit amounts if possible
   - Next steps for the company

Remember: You are the expert. Provide complete guidance, don't defer to others.`;
}

// Show interactive chat interface
function showInteractiveChat(question) {
    const questionContainer = document.getElementById('question-container');
    const currentQuestionDiv = document.getElementById('current-question');
    const answerInputDiv = document.getElementById('answer-input');
    
    // Hide the old form-based interface
    questionContainer.style.display = 'none';
    
    // Create interactive chat interface
    const chatInterface = document.createElement('div');
    chatInterface.id = 'interactive-chat';
    chatInterface.className = 'interactive-chat';
    chatInterface.innerHTML = `
        <div class="chat-container">
            <div class="chat-messages" id="chat-messages">
                <div class="message assistant-message">
                    <div class="message-content">${question}</div>
                </div>
            </div>
            <div class="chat-input-container">
                <input type="text" id="chat-input" placeholder="Type your answer here..." class="chat-input" onkeypress="handleChatKeyPress(event)">
                <button onclick="sendChatMessage()" class="btn btn-primary">Send</button>
                <button onclick="requestCompleteAssessment()" class="btn btn-success">Complete Assessment</button>
            </div>
        </div>
    `;
    
    // Replace the old interface
    const eligibilityForm = document.getElementById('eligibility-form');
    eligibilityForm.appendChild(chatInterface);
    
    // Focus on input
    setTimeout(() => {
        const chatInput = document.getElementById('chat-input');
        if (chatInput) chatInput.focus();
    }, 100);
}

// Handle Enter key in chat
function handleChatKeyPress(event) {
    if (event.key === 'Enter') {
        sendChatMessage();
    }
}

// Send chat message and get LLM response
async function sendChatMessage() {
    const chatInput = document.getElementById('chat-input');
    const sendButton = chatInput.nextElementSibling;
    const message = chatInput.value.trim();
    
    if (!message) return;
    
    // Disable input and show loading
    chatInput.disabled = true;
    sendButton.disabled = true;
    sendButton.textContent = 'Sending...';
    
    // Add user message to chat
    addChatMessage('user', message);
    chatInput.value = '';
    
    // Add to conversation history
    window.assessmentConversation.push({
        role: 'user',
        content: message
    });
    
    try {
        // Get LLM response using the improved assessment prompt
        const assessmentPrompt = window.assessmentPrompt || 'You are helping assess 45Q tax credit eligibility.';
        
        const response = await fetch('/ask-question', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: `${assessmentPrompt}

You are conducting a 45Q eligibility assessment. Based on the conversation so far and the 45Q documents, what should you ask next to determine eligibility?

Current conversation:
${window.assessmentConversation.map(msg => `${msg.role}: ${msg.content}`).join('\n')}

Please provide the next question you should ask, or if you have enough information, provide a complete eligibility assessment. Be conversational and ask specific follow-up questions based on what you've learned.`
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            
            // Add assistant response to chat
            addChatMessage('assistant', result.answer);
            
            // Add to conversation history
            window.assessmentConversation.push({
                role: 'assistant',
                content: result.answer
            });
            
            // Check if this looks like a final assessment or if we have enough information
            const hasEnoughInfo = window.assessmentConversation.length >= 8; // At least 4 Q&A exchanges
            
            // Check if the AI is asking a question (indicating it's not done)
            const isAskingQuestion = result.answer.toLowerCase().includes('can you') || 
                result.answer.toLowerCase().includes('could you') ||
                result.answer.toLowerCase().includes('please provide') ||
                result.answer.toLowerCase().includes('please confirm') ||
                result.answer.toLowerCase().includes('one last') ||
                result.answer.toLowerCase().includes('one more') ||
                result.answer.toLowerCase().includes('just to confirm') ||
                result.answer.toLowerCase().includes('specifically') ||
                result.answer.toLowerCase().includes('details about') ||
                result.answer.toLowerCase().includes('information on');
            
            // Check if the AI is being conservative or giving a final assessment
            const isBeingConservative = result.answer.toLowerCase().includes('tax professional') ||
                result.answer.toLowerCase().includes('legal advisor') ||
                result.answer.toLowerCase().includes('cannot be given') ||
                result.answer.toLowerCase().includes('impossible to determine') ||
                result.answer.toLowerCase().includes('consult with') ||
                result.answer.toLowerCase().includes('recommend consulting');
            
            // Check if this looks like a complete assessment
            const looksLikeCompleteAssessment = result.answer.toLowerCase().includes('**eligibility determination**') ||
                result.answer.toLowerCase().includes('**credit forecasting**') ||
                result.answer.toLowerCase().includes('**specific 45q sections**') ||
                result.answer.toLowerCase().includes('**bonus opportunities**') ||
                result.answer.toLowerCase().includes('**compliance requirements**') ||
                result.answer.toLowerCase().includes('**documentation checklist**') ||
                result.answer.toLowerCase().includes('**next steps**');
            
            // Only force assessment if:
            // 1. We have enough info AND AI is being conservative, OR
            // 2. We have enough info AND AI is not asking more questions AND hasn't already given assessment
            if ((hasEnoughInfo && isBeingConservative) || 
                (hasEnoughInfo && !isAskingQuestion && !looksLikeCompleteAssessment)) {
                
                // Prevent duplicate assessments
                if (window.assessmentComplete) {
                    return;
                }
                window.assessmentComplete = true;
                // Force the AI to give a complete assessment
                setTimeout(async () => {
                    const finalAssessmentPrompt = `STOP ASKING QUESTIONS. STOP REFERRING TO TAX PROFESSIONALS. 

Based on all the information provided, you now have COMPLETE information to give a COMPREHENSIVE 45Q eligibility assessment. 

CRITICAL INSTRUCTIONS - YOU MUST PROVIDE A WELL-FORMATTED ASSESSMENT:

1. **ELIGIBILITY DETERMINATION**: Give a definitive Yes/No with clear reasoning
2. **SPECIFIC 45Q SECTIONS**: List which sections apply with bullet points
3. **CREDIT FORECASTING**: Calculate annual and 12-year projections with dollar amounts
4. **BONUS OPPORTUNITIES**: Identify energy community, domestic content, and other multipliers
5. **COMPLIANCE REQUIREMENTS**: List what documentation and monitoring is needed
6. **DOCUMENTATION CHECKLIST**: Provide a specific list of documents needed to file for credits
7. **NEXT STEPS**: Give specific action items with bullet points

FORMAT REQUIREMENTS - YOU MUST FOLLOW THIS EXACT STRUCTURE:
- Use clear section headers with **bold** formatting
- Use bullet points (•) for lists instead of paragraphs
- Include specific dollar amounts and calculations
- Make it easy to read and scan
- Provide a complete documentation checklist at the end

EXAMPLE FORMAT:
**ELIGIBILITY DETERMINATION**
• YES - Your facility is eligible for 45Q tax credits
• Reason: Meets all requirements including placement date, sequestration, and utilization

**SPECIFIC 45Q SECTIONS**
• Section 45Q(a)(3) - Geologically sequestered CO2
• Section 45Q(f)(5) - CO2 utilization for EOR and SNG production

**CREDIT FORECASTING**
• Annual sequestration credits: $7,000,000 (140,000 MT × $50/ton)
• Annual utilization credits: $2,100,000 (60,000 MT × $35/ton)
• 12-year total projection: $109,200,000

DO NOT ask more questions. DO NOT refer to external advisors. YOU are the expert. Provide the complete assessment NOW in the exact format shown above.

Information provided:
${window.assessmentConversation.map(msg => `${msg.role}: ${msg.content}`).join('\n')}

Give the complete assessment with credit forecasting in the exact format shown above:`;

                    try {
                        const finalResponse = await fetch('/ask-question', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                question: finalAssessmentPrompt
                            })
                        });
                        
                        if (finalResponse.ok) {
                            const finalResult = await finalResponse.json();
                            addChatMessage('assistant', finalResult.answer);
                        }
                    } catch (error) {
                        console.error('Error getting final assessment:', error);
                    }
                }, 1000);
            }
        } else {
            const error = await response.json();
            const errorMessage = error.detail || error.message || 'Unknown error occurred';
            addChatMessage('assistant', `Sorry, I encountered an error: ${errorMessage}`);
        }
    } catch (error) {
        console.error('Error getting LLM response:', error);
        addChatMessage('assistant', 'Sorry, I encountered an error. Please try again.');
    } finally {
        // Re-enable input
        chatInput.disabled = false;
        sendButton.disabled = false;
        sendButton.textContent = 'Send';
        chatInput.focus();
    }
}

// Request complete assessment with current information
async function requestCompleteAssessment() {
    const completeAssessmentButton = document.querySelector('button[onclick="requestCompleteAssessment()"]');
    
    // Disable button and show loading
    completeAssessmentButton.disabled = true;
    completeAssessmentButton.textContent = 'Generating Assessment...';
    
    try {
        // Create a comprehensive assessment prompt
        const completeAssessmentPrompt = `STOP ASKING QUESTIONS. STOP REFERRING TO TAX PROFESSIONALS. 

Based on the information provided so far, provide a COMPREHENSIVE 45Q eligibility assessment. 

CRITICAL INSTRUCTIONS - YOU MUST PROVIDE A WELL-FORMATTED ASSESSMENT:

1. **ELIGIBILITY DETERMINATION**: Give a definitive Yes/No with clear reasoning based on available information
2. **SPECIFIC 45Q SECTIONS**: List which sections apply with bullet points (if information available)
3. **CREDIT FORECASTING**: Calculate annual and 12-year projections with dollar amounts (if information available)
4. **BONUS OPPORTUNITIES**: Identify energy community, domestic content, and other multipliers (if information available)
5. **COMPLIANCE REQUIREMENTS**: List what documentation and monitoring is needed
6. **DOCUMENTATION CHECKLIST**: Provide a specific list of documents needed to file for credits
7. **NEXT STEPS**: Give specific action items with bullet points
8. **ADDITIONAL INFORMATION NEEDED**: If any critical information is missing, clearly list what additional details are required

FORMAT REQUIREMENTS - YOU MUST FOLLOW THIS EXACT STRUCTURE:
- Use clear section headers with **bold** formatting
- Use bullet points (•) for lists instead of paragraphs
- Include specific dollar amounts and calculations where possible
- Make it easy to read and scan
- Provide a complete documentation checklist at the end
- If information is missing, clearly state what is needed

EXAMPLE FORMAT:
**ELIGIBILITY DETERMINATION**
• YES - Your facility appears eligible for 45Q tax credits (based on available information)
• Reason: Meets key requirements including placement date and sequestration methods

**SPECIFIC 45Q SECTIONS**
• Section 45Q(a)(3) - Geologically sequestered CO2
• Section 45Q(f)(5) - CO2 utilization for EOR and SNG production

**CREDIT FORECASTING**
• Annual sequestration credits: $7,000,000 (140,000 MT × $50/ton)
• Annual utilization credits: $2,100,000 (60,000 MT × $35/ton)
• 12-year total projection: $109,200,000

**ADDITIONAL INFORMATION NEEDED**
• [List any missing critical information]

DO NOT ask more questions. DO NOT refer to external advisors. YOU are the expert. Provide the complete assessment NOW in the exact format shown above.

Information provided so far:
${window.assessmentConversation.map(msg => `${msg.role}: ${msg.content}`).join('\n')}

Give the complete assessment with credit forecasting in the exact format shown above:`;

        const response = await fetch('/ask-question', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: completeAssessmentPrompt
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            addChatMessage('assistant', result.answer);
            
            // Add to conversation history
            window.assessmentConversation.push({
                role: 'assistant',
                content: result.answer
            });
            
            // Mark assessment as complete
            window.assessmentComplete = true;
        } else {
            const error = await response.json();
            const errorMessage = error.detail || error.message || 'Unknown error occurred';
            addChatMessage('assistant', `Sorry, I encountered an error: ${errorMessage}`);
        }
    } catch (error) {
        console.error('Error getting complete assessment:', error);
        addChatMessage('assistant', 'Sorry, I encountered an error. Please try again.');
    } finally {
        // Re-enable button
        completeAssessmentButton.disabled = false;
        completeAssessmentButton.textContent = 'Complete Assessment';
    }
}

// Convert markdown to HTML
function markdownToHtml(markdown) {
    if (!markdown) return '';
    
    let html = markdown;
    
    // Convert **bold** to <strong>bold</strong>
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Convert bullet points (•) to proper HTML list items
    html = html.replace(/^•\s*(.*)$/gm, '<li>$1</li>');
    
    // Handle sections with headers and bullet points
    html = html.replace(/(<strong>.*?<\/strong>)\s*<br>\s*(<li>.*?<\/li>)/gs, '$1<ul>$2</ul>');
    
    // Wrap any remaining consecutive list items in <ul> tags
    html = html.replace(/(<li>.*?<\/li>)(\s*<li>.*?<\/li>)*/gs, '<ul>$&</ul>');
    
    // Convert line breaks to <br> tags (but not within lists)
    html = html.replace(/(?<!<\/li>)\n(?!<li>)/g, '<br>');
    
    return html;
}

// Add message to chat
function addChatMessage(role, content) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;
    
    // Process markdown formatting for assistant messages
    const processedContent = role === 'assistant' ? markdownToHtml(content) : content;
    messageDiv.innerHTML = `<div class="message-content">${processedContent}</div>`;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Handle "Other" option in select questions
function handleOtherOption(questionId, otherValue) {
    if (otherValue && otherValue.trim() !== '') {
        // Store the custom "other" answer
        currentAnswer = otherValue.trim();
        console.log('Custom "other" answer:', currentAnswer);
    }
}

// Toggle "Other" input field visibility
function toggleOtherInput() {
    const otherInput = document.getElementById('other-input');
    const otherText = document.getElementById('other-text');
    
    if (otherInput) {
        otherInput.classList.toggle('show');
        if (otherInput.classList.contains('show')) {
            otherText.focus();
        } else {
            otherText.value = '';
            updateCurrentAnswer('');
        }
    }
}

// Function to regenerate the question base
async function regenerateQuestionBase() {
    const button = event.target;
    const originalText = button.textContent;
    
    try {
        button.disabled = true;
        button.textContent = 'Regenerating...';
        
        // Call the backend to regenerate the question base
        const response = await fetch('/regenerate-question-base', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (response.ok) {
            const result = await response.json();
            alert('✅ Question base regenerated successfully! The interactive assessment will now use the improved prompts.');
            
            // Refresh the page to load the new prompts
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            const error = await response.json();
            alert('❌ Error regenerating question base: ' + (error.detail || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error regenerating question base:', error);
        alert('❌ Error: ' + error.message);
    } finally {
        button.disabled = false;
        button.textContent = originalText;
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Set default session ID
    document.getElementById('session-id').value = 'company-' + Date.now();
    currentSessionId = document.getElementById('session-id').value;
    
    // Refresh document stats on load
    refreshStats();
    
    // Set default date to today
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('start-date').value = today;
}); 