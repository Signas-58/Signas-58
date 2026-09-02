export default {
  async fetch(request) {
    const username = "Signas-58";

    // 1. Fetch current live view count
    let count = 1;
    try {
      const countRes = await fetch(`https://anime-counter.lulushu.workers.dev/@${username}?theme=naruto`, {
        headers: { "User-Agent": "Mozilla/5.0" }
      });
      const text = await countRes.text();
      const match = text.match(/>\s*(\d+)\s*</);
      if (match) {
        count = parseInt(match[1], 10);
      }
    } catch (e) {
      console.error("Count fetch error:", e);
    }

    // 2. 10-count theme rotation calculation
    // Index 0 (1-10, 51-60, 101-110...): moebooru
    // Index 1 (11-20, 61-70, 111-120...): naruto
    // Index 2 (21-30, 71-80, 121-130...): onepiece
    // Index 3 (31-40, 81-90, 131-140...): booru-helltaker
    // Index 4 (41-50, 91-100, 141-150...): gelbooru
    const themeIndex = Math.floor(Math.max(0, count - 1) / 10) % 5;

    let responseSvg = "";

    // 3. Handle theme rendering for each of the 5 themes
    if (themeIndex === 1) {
      // naruto
      const res = await fetch(`https://anime-counter.lulushu.workers.dev/@${username}?theme=naruto`, {
        headers: { "User-Agent": "Mozilla/5.0" }
      });
      responseSvg = await res.text();
    } else if (themeIndex === 2) {
      // onepiece
      const res = await fetch(`https://anime-counter.lulushu.workers.dev/@${username}?theme=onepiece`, {
        headers: { "User-Agent": "Mozilla/5.0" }
      });
      responseSvg = await res.text();
    } else {
      // moebooru (0), booru-helltaker (3), gelbooru (4)
      const themeNames = ["moebooru", "naruto", "onepiece", "booru-helltaker", "gelbooru"];
      const theme = themeNames[themeIndex];
      const digits = String(count).padStart(7, "0").split("");

      const imagePromises = digits.map(async (d) => {
        const url = `https://raw.githubusercontent.com/journey-ad/Moe-Counter/master/assets/theme/${theme}/${d}.gif`;
        const res = await fetch(url);
        const arrayBuffer = await res.arrayBuffer();
        const uint8Array = new Uint8Array(arrayBuffer);
        let binary = "";
        for (let i = 0; i < uint8Array.byteLength; i++) {
          binary += String.fromCharCode(uint8Array[i]);
        }
        const base64 = btoa(binary);
        return `data:image/gif;base64,${base64}`;
      });

      const base64Images = await Promise.all(imagePromises);
      const digitWidth = 45;
      const digitHeight = 100;
      const totalWidth = digitWidth * digits.length;

      let svgImages = "";
      base64Images.forEach((b64, i) => {
        svgImages += `<image x="${i * digitWidth}" y="0" width="${digitWidth}" height="${digitHeight}" href="${b64}" />\n  `;
      });

      responseSvg = `<?xml version="1.0" encoding="UTF-8"?>
<svg width="${totalWidth}" height="${digitHeight}" viewBox="0 0 ${totalWidth} ${digitHeight}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  ${svgImages.trim()}
</svg>`;
    }

    // 4. Return SVG response with strict anti-cache headers so GitHub Camo never caches stale theme
    return new Response(responseSvg, {
      headers: {
        "Content-Type": "image/svg+xml",
        "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0, s-maxage=0, proxy-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
        "Surrogate-Control": "no-store"
      }
    });
  }
};
