function openModal(wrapper) {
    const modal = document.getElementById("imgModal");
    const modalImg = document.getElementById("modalImage");
  
    const img = wrapper.querySelector("img");  // ← ここで <img> を取得
    if (img && modal && modalImg) {
      modalImg.src = img.src;
      modal.style.display = "block";
    }
  }
    
    function closeModal() {
      document.getElementById("imgModal").style.display = "none";
    }
    