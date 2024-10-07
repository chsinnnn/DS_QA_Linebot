document.addEventListener('DOMContentLoaded', function() {
    const addUserForm = document.getElementById('add-user-form');
    const userSelect = document.getElementById('user-list');
    const deleteUserButton = document.getElementById('delete-user-button');

    // 函數: 載入使用者列表
    function loadUserList() {
        userSelect.innerHTML = '';  // 清空選項
        fetch('/get_users')  // 修改為從 /get_users 取得使用者資料
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                    return;
                }
                data.users.forEach(user => {
                    const option = document.createElement('option');
                    option.value = user._id;
                    option.textContent = user.username;
                    userSelect.appendChild(option);
                });
            })
            .catch(error => console.error('載入使用者失敗:', error));
    }

    // 初始化時載入使用者列表
    loadUserList();

    // 新增使用者表單提交
    addUserForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const formData = {
            username: document.getElementById('new-username').value,
            password: document.getElementById('new-password').value,
            role: document.getElementById('new-role').value
        };

        fetch('/add_user', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message || data.error);
            if (data.message) {
                addUserForm.reset();  // 重置表單
                loadUserList();  // 新增後重新載入使用者列表
            }
        })
        .catch(error => console.error('新增使用者失敗:', error));
    });

    // 刪除使用者按鈕點擊
    deleteUserButton.addEventListener('click', function() {
        const userId = userSelect.value;

        if (!userId) {
            alert('請選擇一個使用者進行刪除');
            return;
        }

        fetch('/delete_user?id=' + userId, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message || data.error);
            if (data.message) {
                loadUserList();  // 刪除後重新載入使用者列表
            }
        })
        .catch(error => console.error('刪除使用者失敗:', error));
    });
});
