export default {
  async fetch(request) {
    const username = "Signas-58";

    // 1. Fetch current live view count
    let count = 1;
    try {
      const res = await fetch(`https://anime-counter.lulushu.workers.dev/@${username}?theme=moebooru`, {
        headers: { "User-Agent": "Mozilla/5.0" }
      });
      const svgText = await res.text();
      const match = svgText.match(/>\s*(\d+)\s*</);
      if (match) {
        count = parseInt(match[1], 10);
      }
    } catch (e) {
      console.error("Error fetching view count:", e);
    }

    // 2. Calculate 10-count rotation theme index
    // (1-10 -> 0, 11-20 -> 1, 21-30 -> 2, 31-40 -> 3, 41-50 -> 4, 51-60 -> 0, etc.)
    const themeIndex = Math.floor(Math.max(0, count - 1) / 10) % 5;

    // 3. Define the 5 target theme URLs
    const themes = [
      `https://count.getloli.com/get/@${username}?theme=moebooru`,
      `https://anime-counter.lulushu.workers.dev/@${username}?theme=naruto`,
      `https://anime-counter.lulushu.workers.dev/@${username}?theme=onepiece`,
      `https://count.getloli.com/get/@${username}?theme=booru-helltaker`,
      `https://count.getloli.com/get/@${username}?theme=gelbooru`
    ];

    const targetUrl = themes[themeIndex];

    // 4. Proxy the active theme SVG back to GitHub with no-cache headers
    try {
      const imageRes = await fetch(targetUrl, {
        headers: { "User-Agent": "Mozilla/5.0" }
      });
      return new Response(imageRes.body, {
        headers: {
          "Content-Type": "image/svg+xml",
          "Cache-Control": "max-age=0, no-cache, no-store, must-revalidate",
          "Pragma": "no-cache",
          "Expires": "0"
        }
      });
    } catch (e) {
      return new Response("Error fetching counter SVG", { status: 500 });
    }
  }
};
