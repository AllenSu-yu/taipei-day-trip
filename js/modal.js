// js/modal.js
function openLogin() {
    document.getElementById("loginModal").classList.remove("hidden");
    // 確保登入表單顯示，註冊表單隱藏
    document.getElementById("modal-login").classList.remove("hidden");
    document.getElementById("modal-signup").classList.add("hidden");
    }
  
function closeLogin() {
    document.getElementById("loginModal").classList.add("hidden");
    }


function openSignup(){
    document.getElementById("modal-login").classList.add("hidden")
    document.getElementById("modal-signup").classList.remove("hidden")
}

function reopenLogin(){
    document.getElementById("modal-login").classList.remove("hidden")
    document.getElementById("modal-signup").classList.add("hidden")
}