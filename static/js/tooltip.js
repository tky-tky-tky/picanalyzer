document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.tooltip-wrap').forEach(el => {
      el.addEventListener('click', (e) => {
        e.stopPropagation(); // 他を閉じるのを防ぐ
        document.querySelectorAll('.tooltip-wrap').forEach(w => {
          if (w !== el) w.classList.remove('active');
        });
        el.classList.toggle('active');
      });
    });
  
    // 外部クリックで全部閉じる
    document.addEventListener('click', () => {
      document.querySelectorAll('.tooltip-wrap').forEach(el => el.classList.remove('active'));
    });
  });
  