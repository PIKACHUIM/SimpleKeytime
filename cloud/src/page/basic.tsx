export const Basic = () => {
    return (
        <div>
            <head>
                <meta charSet="UTF-8"/>
                <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
                <title>title</title>
                <link href="https://cdn.jsdmirror.com/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet"/>
                <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"
                      rel="stylesheet"/>
                <link href="/static/css/styles.css" rel="stylesheet"/>
                <link rel="shortcut icon" href="/static/favicon.ico"/>
                extra_css
            </head>
            <body class="bg-gray-50 text-gray-800">
            content

            <footer class="bg-white py-6 mt-12">
                <div class="container mx-auto px-4 text-center text-gray-500">
                    <p>&copy; current_year app_name. 保留所有权利.</p>
                </div>
            </footer>

            <script src="https://cdn.jsdmirror.com/npm/alpinejs@3.4.2/dist/cdn.min.js" defer></script>
            extra_js
            </body>
        </div>
    )
}