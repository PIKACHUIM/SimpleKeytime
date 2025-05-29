import { Hono } from 'hono'

const app = new Hono()

// app.get('/', (c) => {
//   return c.text('Hello Hono!')
// })
app.get('/', (c) => {
  const name = 'John Doe';
  const count = 10;

  return c.html(
    <html>
      <body>
        <h1>Hello, {name}!</h1>
        <p>Count: {count}</p>
      </body>
    </html>
  );
});

export default app
