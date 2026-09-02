export default {
  async fetch(request) {
    const username = "Signas-58";

    // 1. Fetch current live view count safely
    let count = 1;
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000);
      const countRes = await fetch(`https://anime-counter.lulushu.workers.dev/@${username}?theme=moebooru`, {
        headers: { "User-Agent": "Mozilla/5.0" },
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      if (countRes.ok) {
        const text = await countRes.text();
        const match = text.match(/>\s*(\d+)\s*</);
        if (match) {
          count = parseInt(match[1], 10);
        }
      }
    } catch (e) {
      console.error("Count fetch error/timeout:", e);
    }

    // 2. 10-count theme rotation calculation
    const themeIndex = Math.floor(Math.max(0, count - 1) / 10) % 5;
    const themeNames = ["moebooru", "naruto", "onepiece", "booru-helltaker", "gelbooru"];

    let responseSvg = "";

    try {
      if (themeIndex === 1) {
        // naruto
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000);
        const res = await fetch(`https://anime-counter.lulushu.workers.dev/@${username}?theme=naruto`, {
          headers: { "User-Agent": "Mozilla/5.0" },
          signal: controller.signal
        });
        clearTimeout(timeoutId);
        if (res.ok) responseSvg = await res.text();
      } else if (themeIndex === 2) {
        // onepiece
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000);
        const res = await fetch(`https://anime-counter.lulushu.workers.dev/@${username}?theme=onepiece`, {
          headers: { "User-Agent": "Mozilla/5.0" },
          signal: controller.signal
        });
        clearTimeout(timeoutId);
        if (res.ok) responseSvg = await res.text();
      } else {
        // moebooru (0), booru-helltaker (3), gelbooru (4)
        const theme = themeNames[themeIndex];
        const digits = String(count).padStart(7, "0").split("");

        const imagePromises = digits.map(async (d) => {
          try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 3000);
            const url = `https://raw.githubusercontent.com/journey-ad/Moe-Counter/master/assets/theme/${theme}/${d}.gif`;
            const res = await fetch(url, { signal: controller.signal });
            clearTimeout(timeoutId);
            if (res.ok) {
              const arrayBuffer = await res.arrayBuffer();
              const uint8Array = new Uint8Array(arrayBuffer);
              let binary = "";
              for (let i = 0; i < uint8Array.byteLength; i++) {
                binary += String.fromCharCode(uint8Array[i]);
              }
              return `data:image/gif;base64,${btoa(binary)}`;
            }
          } catch (e) {
            console.error(`Error loading digit ${d} for theme ${theme}:`, e);
          }
          return null;
        });

        const base64Images = await Promise.all(imagePromises);
        const digitWidth = 45;
        const digitHeight = 100;
        const totalWidth = digitWidth * digits.length;

        let svgImages = "";
        base64Images.forEach((b64, i) => {
          if (b64) {
            svgImages += `<image x="${i * digitWidth}" y="0" width="${digitWidth}" height="${digitHeight}" href="${b64}" />\n  `;
          }
        });

        if (svgImages.trim()) {
          responseSvg = `<?xml version="1.0" encoding="UTF-8"?>
<svg width="${totalWidth}" height="${digitHeight}" viewBox="0 0 ${totalWidth} ${digitHeight}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  ${svgImages.trim()}
</svg>`;
        }
      }
    } catch (e) {
      console.error("Theme render error:", e);
    }

    // 3. Fallback SVG if any theme fetch failed or timed out (NEVER show broken image)
    if (!responseSvg || !responseSvg.includes("<svg")) {
      responseSvg = `<svg width="180" height="30" viewBox="0 0 180 30" xmlns="http://www.w3.org/2000/svg">
  <rect width="180" height="30" rx="6" fill="#0d1117" stroke="#00F7FF" stroke-width="1.5"/>
  <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="#00F7FF" font-family="sans-serif" font-weight="bold" font-size="14">👀 Views: ${count}</text>
</svg>`;
    }

    // 4. Return SVG response with strict anti-cache headers
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
