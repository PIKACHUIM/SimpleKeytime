import {Context} from "hono";// @ts-ignore
import {FC} from "hono/dist/types/jsx";


export const Heads: FC<{ c: Context }> = (props: any): any => {
    return (
        <head>
            <meta charSet="UTF-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
            <title>{props.c.env.app_name}</title>
            <link href="https://cdn.jsdmirror.com/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet"/>
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"
                  rel="stylesheet"/>
            <link href="/static/css/styles.css" rel="stylesheet"/>
            <link rel="shortcut icon" href="/static/favicon.ico"/>
        </head>
    )
}