import { Hono } from 'hono'
import {serveStatic} from 'hono/cloudflare-workers' // @ts-ignore
import manifest from '__STATIC_CONTENT_MANIFEST'
import {Index} from "./page/index.tsx"
import {Basic} from "./page/basic.tsx"
const app = new Hono()

// app.use("*", serveStatic({manifest: manifest, root: "./"}));
app.get('/', (c) => {
  const name = 'John Doe';
  const count = 10;
  return c.html(
    <html>
      <body>
      <Basic />
      <Index />
      </body>
    </html>
  );
});


export default app
