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
    booking_trip_exist.classList.remove("hidden")
    booking_trip_none.classList.add("hidden")
  }
  if (!result.data){
    booking_trip_exist.classList.add("hidden")
    booking_trip_none.classList.remove("hidden")
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