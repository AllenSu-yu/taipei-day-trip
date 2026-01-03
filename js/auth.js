//註冊會員
async function submitSignup() {
    let signupName = document.querySelector(".signupName").value;
    let signupUser = document.querySelector(".signupUser").value;
    let signupPass = document.querySelector(".signupPass").value;
    const signupResult = document.getElementById("signupResult");
    const modalsignup = document.getElementById("modal-signup");

    let response = await fetch ("/api/user",{
        method:"POST",
        headers: {
            "Content-Type": "application/json"
        },
        body:JSON.stringify({"name":signupName, "email":signupUser, "password":signupPass})
    });
    let result = await response.json();
    if (result.ok){
        signupResult.classList.remove("hidden");
        modalsignup.classList.add("enlarge");
        signupResult.textContent = "註冊成功，請登入系統";
        signupResult.style.color = "green";
    } else{
        signupResult.classList.remove("hidden");
        modalsignup.classList.add("enlarge");
        signupResult.textContent = result.message || "註冊失敗，Email格式錯誤";
        signupResult.style.color = "red";
    }
    setTimeout(() => {
        signupResult.textContent = "";
        modalsignup.classList.remove("enlarge");
    }, 1500);

}

//登入會員
async function submitLogin() {
    let loginUser = document.querySelector(".loginUser").value;
    let loginPass = document.querySelector(".loginPass").value;
    const loginResult = document.getElementById("loginResult");
    const modallogin = document.getElementById("modal-login");

    let response = await fetch ("/api/user/auth",{
        method:"PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body:JSON.stringify({"email":loginUser, "password":loginPass})
    });
    let result = await response.json();
    if (result.token){
         // 將 token 存到 localStorage
        localStorage.setItem('token', result.token);
        
        loginResult.classList.remove("hidden");
        modallogin.classList.add("enlarge");
        loginResult.textContent = "登入成功";
        loginResult.style.color = "green";

        // 延遲後恢復原本的介面高度，關閉 modal 並重新載入頁面
        setTimeout(() => {
            loginResult.textContent = "";
            modallogin.classList.remove("enlarge");
            closeLogin(); // 關閉登入 modal
            location.reload(); // 重新載入頁面
        }, 1500);
    } else {
        loginResult.classList.remove("hidden");
        modallogin.classList.add("enlarge");
        loginResult.textContent = result.message || "登入失敗，Email格式錯誤";
        loginResult.style.color = "red";

        // 延遲後隱藏錯誤訊息及恢復原本的介面高度
        setTimeout(() => {
            loginResult.textContent = "";
            modallogin.classList.remove("enlarge");
        }, 1500);
    }


}

//確認會員登入狀態
async function check_auth() {
    const login__btn = document.querySelector(".login__btn")

    // 如果沒有 token，直接設定為登入狀態
    const token = localStorage.getItem('token');
    if (!token) {
        login__btn.textContent = "登入/註冊";
      return;
    }

    let response = await fetch("/api/user/auth",{
      method: "GET",
      headers:{
        "Content-Type": "application/json",
        "Authorization":`Bearer ${token}`
      }
    });
    let result = await response.json();
    if (result.data){
      login__btn.textContent = "登出系統";
      login__btn.setAttribute('onclick', 'clearToken()');
    }
    else if (result.data == null) {
      login__btn.textContent = "登入/註冊";
      login__btn.setAttribute('onclick', 'openLogin()');
    }
  }


  //清除 token 並登出
function clearToken() {
    localStorage.removeItem('token');
    location.reload();
}