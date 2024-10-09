document.addEventListener('DOMContentLoaded', function() {
    // 載入單元名稱
    fetch('/get_units')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('錯誤:', data.error);
                return;
            }
            const unitSelects = document.querySelectorAll('select[name="unit"]');
            unitSelects.forEach(select => {
                data.units.forEach(unit => {
                    const option = document.createElement('option');
                    option.value = unit;
                    option.textContent = unit;
                    select.appendChild(option);
                });
            });
        })
        .catch(error => console.error('網路錯誤:', error));

    // 當選擇單元名稱變更時，載入題目
    document.getElementById('del-unit').addEventListener('change', function() {
        const unit = this.value;
        fetch(`/get_questions?unit=${unit}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error('錯誤:', data.error);
                    return;
                }
                const questionSelect = document.getElementById('del-question');
                questionSelect.innerHTML = ''; // 清空之前的選項
                data.questions.forEach(question => {
                    const option = document.createElement('option');
                    option.value = question._id;
                    option.textContent = question.Question;
                    questionSelect.appendChild(option);
                });
            })
            .catch(error => console.error('網路錯誤:', error));

    });

    // 處理新增題目的表單提交
    document.getElementById('add-question-form').addEventListener('submit', function(event) {
        event.preventDefault();
        const formData = {
            unit: document.getElementById('unit').value,
            question: document.getElementById('question').value,
            answer: document.getElementById('answer').value,
            type: document.getElementById('type').value
        };

        fetch('/add_question', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => alert(data.message || data.error))
        .catch(error => console.error('網路錯誤:', error));
    });

    // 處理刪除題目的表單提交
    document.getElementById('delete-question-form').addEventListener('submit', function(event) {
        event.preventDefault();
        const unit = document.getElementById('del-unit').value;
        const questionId = document.getElementById('del-question').value;

        fetch(`/delete_question?unit=${unit}&id=${questionId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => alert(data.message || data.error))
        .catch(error => console.error('網路錯誤:', error));
    });
});