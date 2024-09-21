document.addEventListener('DOMContentLoaded', function() {
    // 登入表單提交事件
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(event) {
            event.preventDefault();  // 防止表單的預設提交行為
            
            const formData = {
                username: document.getElementById('username').value,
                password: document.getElementById('password').value
            };

            // 發送 POST 請求到 /login 進行登入
            fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    alert(data.message);  // 如果登入成功，顯示成功訊息
                    window.location.href = '/';  // 成功後跳轉到主頁
                } else {
                    alert(data.error);  // 如果登入失敗，顯示錯誤訊息
                }
            })
            .catch(error => console.error('登入時發生錯誤:', error));
        });
    }

    // 確保 logout-button 存在於 DOM 中
    const logoutButton = document.getElementById('logout-button');
    
    // 檢查是否找到登出按鈕
    if (logoutButton) {
        logoutButton.addEventListener('click', function() {
            console.log('Logout clicked');
            fetch('/logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                window.location.href = '/login';  // 成功後跳轉到登入頁面
            })
            .catch(error => console.error('登出時發生錯誤:', error));
        });
    } else {
        console.error('登出按鈕未找到，請檢查是否有正確的 ID');
    }
});
