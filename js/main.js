(function () {
  "use strict";

  const body = document.body;
  const cover = document.getElementById("cover");
  const inner = document.getElementById("inner");
  const openBtn = document.getElementById("openBtn");
  const replayBtn = document.getElementById("replayBtn");
  const musicBtn = document.getElementById("musicBtn");
  const bgm = document.getElementById("bgm");
  const nameEl = document.getElementById("name");

  let musicOn = false;
  let opening = false;

  /* 从 URL 读取收件人姓名：?name=xx 或 ?to=xx */
  const params = new URLSearchParams(location.search);
  const fromUrl = params.get("name") || params.get("to");
  if (fromUrl && fromUrl.trim()) {
    nameEl.textContent = decodeURIComponent(fromUrl.trim()).slice(0, 20);
  }

  /* ---------- 背景元素生成 ---------- */
  function rand(min, max) {
    return Math.random() * (max - min) + min;
  }

  function makeStars(container, count) {
    const frag = document.createDocumentFragment();
    for (let i = 0; i < count; i++) {
      const s = document.createElement("i");
      s.className = "star";
      const size = rand(1.5, 3.6);
      s.style.cssText = [
        "left:" + rand(0, 100) + "%",
        "top:" + rand(0, 100) + "%",
        "width:" + size + "px",
        "height:" + size + "px",
        "--tw:" + rand(2, 4.5).toFixed(2) + "s",
        "--td:" + rand(0, 5).toFixed(2) + "s",
      ].join(";");
      frag.appendChild(s);
    }
    container.appendChild(frag);
  }

  const HEART_GLYPHS = ["♥", "♡", "❤", "💗", "🎈", "✦"];
  function makeFloaters(container, count, sizes) {
    const frag = document.createDocumentFragment();
    for (let i = 0; i < count; i++) {
      const f = document.createElement("span");
      f.className = "floater";
      f.textContent = HEART_GLYPHS[i % HEART_GLYPHS.length];
      const size = rand(sizes[0], sizes[1]);
      f.style.cssText = [
        "left:" + rand(2, 92) + "%",
        "font-size:" + size.toFixed(0) + "px",
        "--dur:" + rand(7, 15).toFixed(1) + "s",
        "--dl:" + rand(0, 12).toFixed(1) + "s",
        "--sway:" + rand(-40, 40).toFixed(0) + "px",
        "--op:" + rand(0.4, 0.9).toFixed(2),
      ].join(";");
      frag.appendChild(f);
    }
    container.appendChild(frag);
  }

  function makeSparkles(container, count) {
    const frag = document.createDocumentFragment();
    for (let i = 0; i < count; i++) {
      const s = document.createElement("i");
      s.className = "sparkle";
      s.style.cssText = [
        "left:" + rand(0, 100) + "%",
        "top:" + rand(0, 100) + "%",
        "--tw:" + rand(1.6, 3.4).toFixed(2) + "s",
        "--td:" + rand(0, 4).toFixed(2) + "s",
      ].join(";");
      frag.appendChild(s);
    }
    container.appendChild(frag);
  }

  makeStars(document.getElementById("stars"), 90);
  makeFloaters(document.getElementById("coverHearts"), 14, [16, 30]);
  makeFloaters(document.getElementById("innerHearts"), 12, [14, 26]);
  makeSparkles(document.getElementById("sparkles"), 34);

  /* ---------- 彩带动效 ---------- */
  const CONFETTI_COLORS = ["#ff5d8f", "#ffd77a", "#a94ad6", "#7be0ad", "#6ec3ff", "#ff9e7d"];

  function burstConfetti(count) {
    const frag = document.createDocumentFragment();
    for (let i = 0; i < count; i++) {
      const p = document.createElement("i");
      p.className = "confetti-piece";
      const size = rand(7, 13);
      p.style.cssText = [
        "left:" + rand(0, 100) + "%",
        "width:" + size.toFixed(0) + "px",
        "height:" + size * rand(0.5, 1.4) + "px",
        "background:" + CONFETTI_COLORS[i % CONFETTI_COLORS.length],
        "--fd:" + rand(2.4, 4).toFixed(2) + "s",
        "--fdl:" + rand(0, 0.8).toFixed(2) + "s",
        "--fr:" + rand(420, 760).toFixed(0) + "deg",
      ].join(";");
      frag.appendChild(p);
    }
    body.appendChild(frag);
    setTimeout(function () {
      body.querySelectorAll(".confetti-piece").forEach(function (n) { n.remove(); });
    }, 5200);
  }

  /* ---------- 音乐 ---------- */
  function toggleMusic(forcePlay) {
    if (bgm.paused || !musicOn) {
      bgm.volume = 0.55;
      bgm.play().then(function () {
        musicOn = true;
        musicBtn.textContent = "⏸ 暂停音乐";
        musicBtn.setAttribute("aria-pressed", "true");
      }).catch(function () {
        musicOn = false;
        musicBtn.textContent = "🎵 播放音乐";
        musicBtn.setAttribute("aria-pressed", "false");
      });
    } else {
      bgm.pause();
      musicOn = false;
      musicBtn.textContent = "🎵 播放音乐";
      musicBtn.setAttribute("aria-pressed", "false");
    }
    void forcePlay;
  }

  /* ---------- 开卡 / 重开 ---------- */
  function openCard() {
    if (opening) return;
    opening = true;
    body.classList.remove("replay");
    body.classList.add("open");
    inner.setAttribute("aria-hidden", "false");
    burstConfetti(64);
    toggleMusic(true);
    setTimeout(function () { opening = false; }, 950);
  }

  function replay() {
    body.classList.remove("open");
    body.classList.add("replay");
    inner.setAttribute("aria-hidden", "true");
    if (musicOn) {
      bgm.pause();
      musicOn = false;
      musicBtn.textContent = "🎵 播放音乐";
      musicBtn.setAttribute("aria-pressed", "false");
    }
    setTimeout(function () { body.classList.remove("replay"); }, 1000);
  }

  openBtn.addEventListener("click", openCard);
  cover.addEventListener("click", openCard);
  replayBtn.addEventListener("click", replay);
  musicBtn.addEventListener("click", function () { toggleMusic(false); });

  /* 键盘可达性 */
  document.addEventListener("keydown", function (e) {
    if (e.key === "Enter" || e.key === " ") {
      if (document.activeElement === openBtn) openCard();
    }
  });
})();
