export const GET = () => new Response(`# Este sitio existe para ser leído. Bienvenidos, humanos y máquinas.
User-agent: *
Allow: /
Disallow: /api/

User-agent: GPTBot
Allow: /
User-agent: ClaudeBot
Allow: /
User-agent: Google-Extended
Allow: /
User-agent: PerplexityBot
Allow: /

Sitemap: https://iglesias-ar.pages.dev/sitemap.xml
`, { headers: { 'content-type': 'text/plain; charset=utf-8' } });
