// Echo Language - Lesson Interaction

let currentQuestion = 0;
let score = 0;
let hearts = 5;
let answered = false;

// Initialize lesson
document.addEventListener('DOMContentLoaded', function() {
    if (typeof lessonContent !== 'undefined' && lessonContent.length > 0) {
        renderQuestion();
        updateProgress();
    }
});

function renderQuestion() {
    const container = document.getElementById('lessonContent');
    const question = lessonContent[currentQuestion];

    if (!question) {
        showResults();
        return;
    }

    answered = false;

    let html = '<div class="question-container">';

    switch (question.type) {
        case 'multiple_choice':
            html += renderMultipleChoice(question);
            break;
        case 'translate':
            html += renderTranslate(question);
            break;
        case 'fill_blank':
            html += renderFillBlank(question);
            break;
        case 'match':
            html += renderMatch(question);
            break;
        default:
            html += '<p>Unknown question type</p>';
    }

    html += '</div>';
    container.innerHTML = html;
}

function renderMultipleChoice(question) {
    let html = `<p class="question-text">${question.question}</p>`;
    html += '<div class="options-grid">';

    question.options.forEach((option, index) => {
        html += `<button class="option-btn" onclick="selectOption(this, ${index}, ${question.correct})">${option}</button>`;
    });

    html += '</div>';
    html += '<button class="btn btn-primary check-btn" onclick="checkAnswer()" id="checkBtn" style="display:none;">Continue</button>';

    return html;
}

function renderTranslate(question) {
    let html = `<p class="question-text">${question.question}</p>`;
    html += `<input type="text" class="answer-input" id="translateInput" placeholder="Type your answer..." autocomplete="off">`;
    html += '<button class="btn btn-primary check-btn" onclick="checkTranslation()">Check</button>';

    return html;
}

function renderFillBlank(question) {
    let html = `<p class="question-text">${question.question}</p>`;
    html += `<input type="text" class="answer-input" id="fillInput" placeholder="Fill in the blank..." autocomplete="off">`;
    if (question.hint) {
        html += `<p class="hint-text">Hint: ${question.hint}</p>`;
    }
    html += '<button class="btn btn-primary check-btn" onclick="checkFillBlank()">Check</button>';

    return html;
}

function renderMatch(question) {
    let html = '<p class="question-text">Match the pairs</p>';
    html += '<div class="match-container">';

    // Shuffle the right column
    const leftItems = question.pairs.map(p => p[0]);
    const rightItems = question.pairs.map(p => p[1]).sort(() => Math.random() - 0.5);

    html += '<div class="match-column" id="leftColumn">';
    leftItems.forEach((item, i) => {
        html += `<div class="match-item" data-index="${i}" data-value="${item}" onclick="selectMatchItem(this, 'left')">${item}</div>`;
    });
    html += '</div>';

    html += '<div class="match-column" id="rightColumn">';
    rightItems.forEach((item, i) => {
        html += `<div class="match-item" data-index="${i}" data-value="${item}" onclick="selectMatchItem(this, 'right')">${item}</div>`;
    });
    html += '</div>';

    html += '</div>';

    // Store pairs for checking
    window.matchPairs = question.pairs;
    window.matchedCount = 0;
    window.selectedLeft = null;
    window.selectedRight = null;

    return html;
}

function selectOption(btn, selected, correct) {
    if (answered) return;
    answered = true;

    const buttons = document.querySelectorAll('.option-btn');
    buttons.forEach(b => b.classList.remove('selected'));

    btn.classList.add('selected');

    if (selected === correct) {
        btn.classList.add('correct');
        score++;
    } else {
        btn.classList.add('incorrect');
        buttons[correct].classList.add('correct');
        hearts--;
        updateHearts();
    }

    document.getElementById('checkBtn').style.display = 'block';
}

function checkAnswer() {
    currentQuestion++;
    updateProgress();
    renderQuestion();
}

function checkTranslation() {
    if (answered) return;
    answered = true;

    const input = document.getElementById('translateInput');
    const userAnswer = input.value.trim().toLowerCase();
    const question = lessonContent[currentQuestion];
    const correctAnswer = question.answer.toLowerCase();
    const alternatives = question.alternatives ? question.alternatives.map(a => a.toLowerCase()) : [];

    if (userAnswer === correctAnswer || alternatives.includes(userAnswer)) {
        input.style.borderColor = '#58cc02';
        score++;
    } else {
        input.style.borderColor = '#ff4b4b';
        hearts--;
        updateHearts();
        // Show correct answer
        const hint = document.createElement('p');
        hint.className = 'hint-text';
        hint.style.color = '#58cc02';
        hint.textContent = `Correct answer: ${question.answer}`;
        input.parentNode.insertBefore(hint, input.nextSibling);
    }

    // Replace check button with continue
    const checkBtn = document.querySelector('.check-btn');
    checkBtn.textContent = 'Continue';
    checkBtn.onclick = checkAnswer;
}

function checkFillBlank() {
    if (answered) return;
    answered = true;

    const input = document.getElementById('fillInput');
    const userAnswer = input.value.trim().toLowerCase();
    const question = lessonContent[currentQuestion];
    const correctAnswer = question.answer.toLowerCase();

    if (userAnswer === correctAnswer) {
        input.style.borderColor = '#58cc02';
        score++;
    } else {
        input.style.borderColor = '#ff4b4b';
        hearts--;
        updateHearts();
        // Show correct answer
        const hint = document.createElement('p');
        hint.className = 'hint-text';
        hint.style.color = '#58cc02';
        hint.textContent = `Correct answer: ${question.answer}`;
        input.parentNode.insertBefore(hint, input.nextSibling);
    }

    // Replace check button with continue
    const checkBtn = document.querySelector('.check-btn');
    checkBtn.textContent = 'Continue';
    checkBtn.onclick = checkAnswer;
}

function selectMatchItem(element, side) {
    if (element.classList.contains('matched')) return;

    const column = side === 'left' ? 'leftColumn' : 'rightColumn';
    const items = document.querySelectorAll(`#${column} .match-item`);
    items.forEach(item => item.classList.remove('selected'));

    element.classList.add('selected');

    if (side === 'left') {
        window.selectedLeft = element;
    } else {
        window.selectedRight = element;
    }

    // Check if we have a pair
    if (window.selectedLeft && window.selectedRight) {
        checkMatchPair();
    }
}

function checkMatchPair() {
    const leftValue = window.selectedLeft.dataset.value;
    const rightValue = window.selectedRight.dataset.value;

    // Check if this is a valid pair
    const isMatch = window.matchPairs.some(pair =>
        pair[0] === leftValue && pair[1] === rightValue
    );

    if (isMatch) {
        window.selectedLeft.classList.add('matched');
        window.selectedRight.classList.add('matched');
        window.matchedCount++;

        // Check if all matched
        if (window.matchedCount === window.matchPairs.length) {
            score++;
            setTimeout(checkAnswer, 500);
        }
    } else {
        // Wrong match - flash red
        window.selectedLeft.style.borderColor = '#ff4b4b';
        window.selectedRight.style.borderColor = '#ff4b4b';
        setTimeout(() => {
            window.selectedLeft.style.borderColor = '';
            window.selectedRight.style.borderColor = '';
        }, 300);
    }

    window.selectedLeft.classList.remove('selected');
    window.selectedRight.classList.remove('selected');
    window.selectedLeft = null;
    window.selectedRight = null;
}

function updateProgress() {
    const progress = (currentQuestion / lessonContent.length) * 100;
    document.getElementById('progressFill').style.width = `${progress}%`;
}

function updateHearts() {
    document.getElementById('heartsDisplay').textContent = hearts;

    if (hearts <= 0) {
        // Game over - still show results but with lower score
        showResults();
    }
}

async function showResults() {
    const container = document.getElementById('lessonContent');
    container.classList.add('hidden');

    const resultDiv = document.getElementById('lessonResult');
    resultDiv.classList.remove('hidden');

    const percentage = Math.round((score / lessonContent.length) * 100);
    document.getElementById('resultScore').textContent = `${percentage}%`;

    // Calculate XP earned
    const xpEarned = percentage >= 70 ? xpReward : 0;
    document.getElementById('resultXP').textContent = `+${xpEarned}`;

    // Set result title based on score
    const titleEl = document.getElementById('resultTitle');
    if (percentage >= 90) {
        titleEl.textContent = 'Excellent!';
    } else if (percentage >= 70) {
        titleEl.textContent = 'Lesson Complete!';
    } else {
        titleEl.textContent = 'Keep Practicing!';
    }

    // Send completion to server
    try {
        const response = await fetch(`/api/lesson/${lessonId}/complete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ score: percentage })
        });

        const data = await response.json();

        if (data.leveled_up) {
            titleEl.textContent = `Level Up! Now Level ${data.new_level}`;
        }
    } catch (error) {
        console.error('Error saving progress:', error);
    }
}

function restartLesson() {
    currentQuestion = 0;
    score = 0;
    hearts = 5;
    answered = false;

    document.getElementById('heartsDisplay').textContent = hearts;
    document.getElementById('lessonResult').classList.add('hidden');
    document.getElementById('lessonContent').classList.remove('hidden');

    updateProgress();
    renderQuestion();
}
