export default {
  async fetch(request) {
    const username = "Signas-58";

    // 1. Fetch current live view count
    let count = 1;
    try {
      const res = await fetch(`https://anime-counter.lulushu.workers.dev/@${username}?theme=moebooru`, {
        headers: { "User-Agent": "Mozilla/5.0" }
      });
      const text = await res.text();
      const match = text.match(/>\s*(\d+)\s*</);
      if (match) {
        count = parseInt(match[1], 10);
      }
    } catch (e) {
      console.error("Count fetch error:", e);
    }

    // 2. Calculate 10-count rotation theme index
    // 1-10: index 0 (moebooru)
    // 11-20: index 1 (asoul)
    // 21-30: index 2 (booru-helltaker)
    // 31-40: index 3 (gelbooru)
    // 41-50: index 4 (rule34)
    // 51-60: index 0 (moebooru) ...
    const themeIndex = Math.floor(Math.max(0, count - 1) / 10) % 5;
    const themeNames = ["moebooru", "asoul", "booru-helltaker", "gelbooru", "rule34"];
    const theme = themeNames[themeIndex];

    const digits = String(count).padStart(7, "0").split("");

    // 3. Fetch raw pixel character digit GIFs from GitHub CDN and convert to base64
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

    // 4. Construct SVG containing pixel character digits holding numbers
    const digitWidth = 45;
    const digitHeight = 100;
    const totalWidth = digitWidth * digits.length;

    let svgImages = "";
    base64Images.forEach((b64, i) => {
      svgImages += `<image x="${i * digitWidth}" y="0" width="${digitWidth}" height="${digitHeight}" href="${b64}" />\n  `;
    });

    const svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg width="${totalWidth}" height="${digitHeight}" viewBox="0 0 ${totalWidth} ${digitHeight}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  ${svgImages.trim()}
</svg>`;

    return new Response(svg, {
      headers: {
        "Content-Type": "image/svg+xml",
        "Cache-Control": "max-age=0, no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
      }
    });
  }
};
