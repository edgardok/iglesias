type Runtime = import('@astrojs/cloudflare').Runtime<{ DB: D1Database; TURNSTILE_SECRET_KEY: string; AGENTE_TOKEN: string }>;
declare namespace App { interface Locals extends Runtime {} }
