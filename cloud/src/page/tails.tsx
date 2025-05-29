import {Context} from "hono";// @ts-ignore
import {FC} from "hono/dist/types/jsx";


export const Tails: FC<{ c: Context }> = (props: any): any => {
    return (
        <div>
            <footer class="bg-white py-6 mt-12">
                <div class="container mx-auto px-4 text-center text-gray-500">
                    <p>&copy; {new Date().getFullYear()} {props.c.env.app_name}. 保留所有权利.</p>
                </div>
            </footer>
            <script src="https://cdn.jsdmirror.com/npm/alpinejs@3.4.2/dist/cdn.min.js" defer></script>
        </div>
    )
}