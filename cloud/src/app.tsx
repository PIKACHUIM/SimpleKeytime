import {Hono} from 'hono'
import {serveStatic} from 'hono/cloudflare-workers' // @ts-ignore
import manifest from '__STATIC_CONTENT_MANIFEST'
import {Index} from "./page"
import {Heads} from "./page/heads"
import {Tails} from "./page/tails"
import {Panel} from "./dash/panel"
import * as saves from './user/saves'

// 绑定数据 ###############################################################################
export type Bindings = {
    app_name: string
}
// 绑定数据 ###############################################################################
const app = new Hono<{ Bindings: Bindings }>()
app.use("*", serveStatic({manifest: manifest, root: "./"}));

app.get('/', (c) => {
    return c.html(
        <html>
        <body className="bg-gray-50 text-gray-800">
        <Heads c={c}/>
        <Index c={c}/>
        </body>
        <Tails c={c}/>
        </html>
    );
});

app.get('/panel', (c) => {
    return c.html(
        <html>
        <body className="bg-gray-50 text-gray-800">
        <Heads c={c}/>
        <Index c={c}/>
        </body>
        <Tails c={c}/>
        </html>
    );
});

export default app
