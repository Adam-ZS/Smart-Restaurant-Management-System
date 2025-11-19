// ---- PAGE NAVIGATION ----
window.showPage = function (page) {
    document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
    document.getElementById(page).classList.add("active");
};

// ---- MENU DATA WITH IMAGES ----
const MENU = [
    { id: 1, name: "Karak Tea", price: 6, img: "https://i.imgur.com/b5j8F4X.jpeg" },
    { id: 2, name: "Pizza", price: 32, img: "https://i.imgur.com/QHZQhsm.jpeg" },
    { id: 3, name: "Chicken Biryani", price: 28, img: "https://i.imgur.com/kXzmD3q.jpeg" },
    { id: 4, name: "Rice Plate", price: 15, img: "https://i.imgur.com/GxW0w2v.jpeg" },
    { id: 5, name: "Mandi", price: 30, img: "https://i.imgur.com/3htmqJx.jpeg" },
    { id: 6, name: "French Fries", price: 12, img: "https://i.imgur.com/Pm1y1ys.jpeg" },
    { id: 7, name: "Chocolate Cake", price: 22, img: "https://i.imgur.com/BN0PqQE.jpeg" }
];

// ---- RENDER MENU ----
function loadMenu() {
    const grid = document.getElementById("menuGrid");
    grid.innerHTML = "";

    MENU.forEach(item => {
        const card = document.createElement("div");
        card.className = "menu-card";
        card.innerHTML = `
            <img src="${item.img}" />
            <h3>${item.name}</h3>
            <p>AED ${item.price}</p>
            <button onclick="addToCart(${item.id})">Add to Cart</button>
        `;
        grid.appendChild(card);
    });
}
loadMenu();

// ---- CART SYSTEM ----
let cart = [];

window.addToCart = function (id) {
    const item = MENU.find(m => m.id === id);
    cart.push(item);
    alert(item.name + " added to cart!");
    renderCart();
};

function renderCart() {
    const list = document.getElementById("cartItems");
    list.innerHTML = "";

    let total = 0;

    cart.forEach((item, i) => {
        total += item.price;
        list.innerHTML += `
            <div class="cart-item">
                <b>${item.name}</b> — AED ${item.price}
                <button onclick="removeItem(${i})">Remove</button>
            </div>
        `;
    });

    document.getElementById("cartTotal").innerText = total;
}

window.removeItem = function (i) {
    cart.splice(i, 1);
    renderCart();
};

// ---- RESERVATIONS ----
let reservations = [];

window.submitReservation = function () {
    const res = {
        name: document.getElementById("resName").value,
        date: document.getElementById("resDate").value,
        time: document.getElementById("resTime").value,
        size: document.getElementById("resSize").value
    };

    reservations.push(res);
    renderReservations();
    alert("Reservation Confirmed!");
};

function renderReservations() {
    const box = document.getElementById("reservationList");
    box.innerHTML = "";

    reservations.forEach(r => {
        box.innerHTML += `
            <div class="cart-item">
                <b>${r.name}</b><br>
                ${r.date} — ${r.time} — Party of ${r.size}
            </div>
        `;
    });
}

// ---- ANALYTICS ----
const ctx1 = document.getElementById("chartSales");
new Chart(ctx1, {
    type: "bar",
    data: {
        labels: ["Mon", "Tue", "Wed", "Thu", "Fri"],
        datasets: [{
            label: "Daily Sales (AED)",
            data: [200, 350, 300, 500, 650],
            backgroundColor: "#2196f3"
        }]
    }
});

const ctx2 = document.getElementById("chartPopular");
new Chart(ctx2, {
    type: "pie",
    data: {
        labels: ["Pizza", "Biryani", "Mandi", "Fries"],
        datasets: [{
            data: [40, 25, 20, 15],
            backgroundColor: ["#ff7043", "#42a5f5", "#66bb6a", "#ffee58"]
        }]
    }
});
