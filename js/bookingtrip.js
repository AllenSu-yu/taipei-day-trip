// TapPay SDK 初始化
(function initTapPaySDK() {
  if (typeof TPDirect === 'undefined') {
    setTimeout(initTapPaySDK, 100);
    return;
  }
  
  try {
    TPDirect.setupSDK(166540, 'app_rkBfXxW6wxFAhI95Q0PtCJMqklm1MYHrPvH7copgBZqsZ9WlgrmZnh3E4Oc6', 'sandbox');
    
    (function checkCard() {
      if (TPDirect.card) {
        window.dispatchEvent(new Event('tappay-sdk-ready'));
      } else {
        setTimeout(checkCard, 100);
      }
    })();
  } catch (error) {
    console.error('TapPay 初始化失敗:', error);
  }
})();

//前往預定頁面
async function goto_bookingtrip() {
    check_auth();
    // 如果沒有 token，開啟註冊登入彈窗
    const token = localStorage.getItem('token');
    if (!token) {
      openLogin();
    } 
    // 如果是登入狀態，導去booking頁面
    if (token) {
        window.location.href = '/booking';
    }   
  }

//取得預定行程，並更新預定頁面
async function get_bookingtrip(userData = null) {
  const token = localStorage.getItem('token');
  if (!token) {
    return;
  } 
  
  // 如果沒有傳入用戶資訊，才去獲取
  let user_result = { data: userData };
  if (!userData) {
    let user_response = await fetch ("/api/user/auth",{
      method:"GET",
      headers:{
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
      }
    });
    user_result = await user_response.json();
  }
  
  if (user_result.data){
    let user_name = user_result.data.name;
    const welcomeElements = document.querySelectorAll(".welcome");
    welcomeElements.forEach(welcome => {
      welcome.textContent = ` 您好，${user_name}，待預定的行程如下：`;
    });
  }
      
  
  let response = await fetch ("/api/booking", {
    method: "GET",
    headers:{
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    }
  });
  let result = await response.json();
  
  const booking_trip_exist = document.getElementById("booking_trip_exist");
  const booking_trip_none = document.getElementById("booking_trip_none");
  
  if (result.data){
    booking_trip_exist.classList.remove("hidden");
    booking_trip_none.classList.add("hidden");
  }
  if (!result.data){
    booking_trip_exist.classList.add("hidden");
    booking_trip_none.classList.remove("hidden");
  }
  
  if (result.data){
    let attraction_id = result.data.attraction.id;
    let attraction_name = result.data.attraction.name;
    let attraction_address = result.data.attraction.address;
    let attraction_image = result.data.attraction.image;
    let date = result.data.date;
    let time = result.data.time;
    // 使用物件映射
    const booking_time = {
      'morning': '早上9點到下午4點',
      'afternoon': '下午2點到晚上9點'
    }[time] || '';
    let price = result.data.price;
    

    const booking_title = document.querySelector(".booking_title");
    if(booking_title){
      booking_title.textContent = `台北一日遊：${attraction_name}`;
    }

    const booking_img = document.querySelector(".booking_img");
    if (booking_img){
      booking_img.innerHTML = `<img src="${attraction_image}" alt="" class="booking_img-style">`
    }

    const booking_detail = document.querySelector(".booking_detail");
    if(booking_detail){
      booking_detail.innerHTML = `
        <div>日期：<span class="date"> ${date}</span></div>
        <div>時間：<span class="time"> ${booking_time}</span></div>
        <div>費用：<span class="price"> 新台幣${price}元</span></div>
        <div>地點：<span class="adress"> ${attraction_address}</span></div>
        <img src="/image/delete.png" alt="" id="mobile_delete" class="hidden" onclick="delete_bookingtrip()">`
    }

    const summary_information_cost = document.querySelector(".summary_information_cost");
    if (summary_information_cost){
      summary_information_cost.textContent = `總價：新台幣${price}元`;
    }


  }
}

//刪除預定行程
async function delete_bookingtrip() {
  const token = localStorage.getItem('token');
  if (!token) {
    alert("請先登入");
    return;
  }
  let response = await fetch ("/api/booking",{
    method: "DELETE",
    headers:{
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    }
  });
  let result = await response.json();
  if (result.ok){
    window.location.reload();
  }else if (result.error){
    alert(`錯誤：${result.message || "刪除失敗"}`);
  }
}

// 使用 TPDirect.card.setup 設定外觀
// 確保 TapPay SDK 載入完成後再執行
function setupTapPayCard() {
  // 檢查 TPDirect 是否已初始化
  if (typeof TPDirect === 'undefined') {
    console.error('TapPay SDK 尚未載入');
    return false;
  }
  
  if (!TPDirect.card) {
    console.error('TapPay.card 尚未可用，請確認 setupSDK 已執行');
    return false;
  }
  
  // 檢查元素是否存在
  const cardNumberEl = document.getElementById('card-number');
  const cardExpiryEl = document.getElementById('card-expiration-date');
  const cardCcvEl = document.getElementById('card-ccv');
  
 
  try {
    TPDirect.card.setup({
      fields: {
        number: {
          element: cardNumberEl,
          placeholder: '**** **** **** ****'
        },
        expirationDate: {
          element: cardExpiryEl,
          placeholder: 'MM / YY'
        },
        ccv: {
          element: cardCcvEl,
          placeholder: 'CVV'
        }
      },
      styles: {
        'input': { 'color': 'gray' },
        ':focus': { 'color': 'black' },
        '.valid': { 'color': 'green' },
        '.invalid': { 'color': 'red' },
        '::placeholder': { 
          'color': '#757575',
          'font-size': '16px',
          'opacity': '1',
          'font-weight':'500',
          'font-family': 'Noto Sans TC'     
        }
      },
      isMaskCreditCardNumber: true,
      maskCreditCardNumberRange: {
        beginIndex: 6,
        endIndex: 11
      }
    });

    console.log('TapPay 卡片欄位設定成功');
    
    // 標記欄位已初始化
    // cardNumberEl.setAttribute('data-tappay-initialized', 'true');
    
    // 在 setup 成功後才註冊 onUpdate 回調
    setupTapPayCardUpdate();
    
    // 設置按鈕初始狀態
    const submitButton = document.querySelector('#booking-form button[type="submit"]');
    if (submitButton) {
      submitButton.disabled = true;
      submitButton.style.opacity = '0.5';
      submitButton.style.cursor = 'not-allowed';
      submitButton.style.pointerEvents = 'none';
    }
    
    return true;
  } catch (error) {
    console.error('TapPay setup 失敗:', error);
    return false;
  }
}

// 設定 TapPay Fields 狀態更新處理
function setupTapPayCardUpdate() {
  if (typeof TPDirect === 'undefined' || !TPDirect.card) return;

  TPDirect.card.onUpdate(function (update) {
    const submitButton = document.querySelector('#booking-form button[type="submit"]');
    if (!submitButton) return;

    // 更新按鈕狀態
    if (update.canGetPrime) {
      submitButton.disabled = false;
      submitButton.style.opacity = '1';
      submitButton.style.cursor = 'pointer';
      submitButton.style.pointerEvents = 'auto';
    } else {
      submitButton.disabled = true;
      submitButton.style.opacity = '0.5';
      submitButton.style.cursor = 'not-allowed';
      submitButton.style.pointerEvents = 'none';
    }
  });
}


// 等待 TapPay SDK 準備完成後再設定卡片欄位
function initTapPayCardFields() {
  // 檢查 TPDirect 是否已載入且 setupSDK 已執行
  if (typeof TPDirect === 'undefined') {
    console.log('等待 TapPay SDK 載入...');
    return false;
  }
  
  // 檢查 TPDirect.card 是否可用（表示 setupSDK 已完成）
  if (!TPDirect.card) {
    console.log('等待 TapPay SDK 初始化完成...');
    return false;
  }
  
  // 檢查 DOM 元素是否存在
  const cardNumberEl = document.getElementById('card-number');
  const cardExpiryEl = document.getElementById('card-expiration-date');
  const cardCcvEl = document.getElementById('card-ccv');
  
  if (!cardNumberEl || !cardExpiryEl || !cardCcvEl) {
    console.log('等待 DOM 元素載入...');
    return false;
  }
  
  // 執行 card.setup
  const success = setupTapPayCard();
  if (!success) {
    console.warn('TapPay card.setup 失敗，將重試');
    return false;
  }
  
  return true;
}

// 監聽 TapPay SDK 準備完成事件
window.addEventListener('tappay-sdk-ready', function() {
  console.log('收到 TapPay SDK 準備完成事件');
  if (!initTapPayCardFields()) {
    // 如果失敗，稍後再試
    setTimeout(function() {
      initTapPayCardFields();
    }, 200);
  }
});

// 備用方案：如果事件沒有觸發，使用 load 事件
window.addEventListener('load', function() {
  // 等待一段時間後再嘗試（備用方案）
  setTimeout(function() {
    // 只有在還沒有成功初始化時才執行
    if (typeof TPDirect !== 'undefined' && TPDirect.card) {
      const cardNumberEl = document.getElementById('card-number');
      if (cardNumberEl && !cardNumberEl.hasAttribute('data-tappay-initialized')) {
        console.log('使用備用方案初始化 TapPay 卡片欄位');
        initTapPayCardFields();
      }
    }
  }, 1000);
});

// 重置提交按鈕狀態
function resetSubmitButton(button) {
  if (button) {
    button.disabled = false;
    button.textContent = '確認訂購並付款';
  }
}

async function onSubmit(event) {
  event.preventDefault();

  const form = event.target;
  const formData = new FormData(form);
  const contactInfo = {
    name: formData.get('name'),
    email: formData.get('email'),
    phone: formData.get('phone')
  };

  // 驗證聯絡資訊
  if (!contactInfo.name || !contactInfo.email || !contactInfo.phone) {
    alert('請填寫完整的聯絡資訊');
    return;
  }

  // 檢查 TPDirect 是否可用
  if (typeof TPDirect === 'undefined' || !TPDirect.card) {
    alert('付款系統尚未準備完成，請稍候再試');
    return;
  }

  // 取得 TapPay Fields 的 status
  const tappayStatus = TPDirect.card.getTappayFieldsStatus();

  // 確認是否可以 getPrime
  if (!tappayStatus || !tappayStatus.canGetPrime) {
    const status = tappayStatus?.status || {};
    const messages = [];
    
    if (status.number === 1) messages.push('請輸入卡片號碼');
    else if (status.number === 2) messages.push('卡片號碼格式錯誤');
    
    if (status.expiry === 1) messages.push('請輸入過期日期（MM/YY）');
    else if (status.expiry === 2) messages.push('過期日期格式錯誤');
    
    if (status.ccv === 1) messages.push('請輸入 CCV 驗證碼');
    else if (status.ccv === 2) messages.push('CCV 驗證碼格式錯誤');
    
    alert('請確認信用卡資訊是否正確\n\n' + (messages.length ? messages.join('\n') : 'TapPay 欄位尚未初始化完成'));
    return;
  }

  // 禁用提交按鈕，防止重複提交
  const submitButton = form.querySelector('button[type="submit"]');
  if (submitButton) {
    submitButton.disabled = true;
    submitButton.textContent = '處理中...';
  }

  // 再次檢查狀態
  const finalStatus = TPDirect.card.getTappayFieldsStatus();
  if (!finalStatus?.canGetPrime) {
    alert('信用卡資訊驗證失敗，請重新檢查後再試');
    resetSubmitButton(submitButton);
    return;
  }

  // Get prime
  TPDirect.card.getPrime(async (result) => {
    if (result.status !== 0) {
      alert('取得付款資訊失敗：' + result.msg);
      resetSubmitButton(submitButton);
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const bookingResponse = await fetch('/api/booking', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });
      const bookingData = await bookingResponse.json();
      
      if (!bookingData.data) {
        alert('無法取得訂單資訊，請重新整理頁面後再試');
        resetSubmitButton(submitButton);
        return;
      }

      const response = await fetch('/api/orders', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          prime: result.card.prime,
          order: {
            price: bookingData.data.price,
            trip: {
              attraction: bookingData.data.attraction,
              date: bookingData.data.date,
              time: bookingData.data.time
            },
            contact: contactInfo
          }
        })
      });

      const responseData = await response.json();
      
      if (response.ok && responseData.data) {
        // 檢查付款狀態
        if (responseData.data.payment.status === 0) {
          // 付款成功，跳轉到感謝頁面
          window.location.href = `/thankyou?number=${responseData.data.number}`;
        } else {
          // 付款失敗，顯示錯誤訊息
          alert('付款失敗：' + (responseData.data.payment.message || '未知錯誤'));
          resetSubmitButton(submitButton);
        }
      } else {
        // 訂單建立失敗
        alert('訂單建立失敗：' + (responseData.message || '未知錯誤'));
        resetSubmitButton(submitButton);
      }
    } catch (error) {
      console.error('付款處理錯誤:', error);
      alert('付款處理時發生錯誤，請稍候再試');
      resetSubmitButton(submitButton);
    }
  });
}

// 綁定表單提交事件
document.addEventListener('DOMContentLoaded', function() {
  const bookingForm = document.getElementById('booking-form');
  if (bookingForm) {
    bookingForm.addEventListener('submit', onSubmit);
  }
});
