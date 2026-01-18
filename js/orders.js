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

//取得訂單資訊，並更新頁面
async function get_orders(userData = null) {
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
      welcome.textContent = ` 您好，${user_name}，訂單資訊如下：`;
    });
  }
      
  // 從 URL 參數取得訂單號碼
  const urlParams = new URLSearchParams(window.location.search);
  const orderNumber = urlParams.get('number');
  
  if (!orderNumber) {
    console.error('找不到訂單號碼');
    return;
  }

  //取得訂單資訊
  let response = await fetch (`/api/order/${orderNumber}`, {
    method: "GET",
    headers:{
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    }
  });
  let result = await response.json();
  
  if (result.data && result.data.status === 1){
    let number = result.data.number;
    let price = result.data.price;
    let attraction_id = result.data.trip.attraction.id;
    let attraction_name = result.data.trip.attraction.name;
    let attraction_address = result.data.trip.attraction.address;
    let attraction_image = result.data.trip.attraction.image;
    let date = result.data.trip.date;
    let time = result.data.trip.time;
    // 使用物件映射
    const booking_time = {
      'morning': '早上9點到下午4點',
      'afternoon': '下午2點到晚上9點'
    }[time] || '';
    let contact_name = result.data.contact.name;
    let contact_email = result.data.contact.email;
    let contact_phone = result.data.contact.phone;

    const orders_information = document.querySelector(".orders_information");
    if(orders_information){
      orders_information.innerHTML = `
        <div class="order-item">訂購成功，您的訂單編號為：<span class="date"> ${number}</span></div>
        <div class="order-item">日期：<span class="date"> ${date}</span></div>
        <div class="order-item">時間：<span class="time"> ${booking_time}</span></div>
        <div class="order-item">費用：<span class="price"> 新台幣${price}元</span></div>
        <div class="order-item">地點：<span class="adress"> ${attraction_address}</span></div>`
    }
  }

  if (result.data && result.data.status === 0){
    let number = result.data.number;
    let price = result.data.price;
    let attraction_id = result.data.trip.attraction.id;
    let attraction_name = result.data.trip.attraction.name;
    let attraction_address = result.data.trip.attraction.address;
    let attraction_image = result.data.trip.attraction.image;
    let date = result.data.trip.date;
    let time = result.data.trip.time;
    // 使用物件映射
    const booking_time = {
      'morning': '早上9點到下午4點',
      'afternoon': '下午2點到晚上9點'
    }[time] || '';
    let contact_name = result.data.contact.name;
    let contact_email = result.data.contact.email;
    let contact_phone = result.data.contact.phone;

    const orders_information = document.querySelector(".orders_information");
    if(orders_information){
      orders_information.innerHTML = `
        <div class="order-item">付款失敗，您的訂單編號為：<span class="date"> ${number}</span></div>
        <div class="order-item">日期：<span class="date"> ${date}</span></div>
        <div class="order-item">時間：<span class="time"> ${booking_time}</span></div>
        <div class="order-item">費用：<span class="price"> 新台幣${price}元</span></div>
        <div class="order-item">地點：<span class="adress"> ${attraction_address}</span></div>`
    }
  }




}



