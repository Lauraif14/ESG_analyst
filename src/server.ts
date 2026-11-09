import { buildApp } from "./app.js";
import { config } from "./config.js";
import { createDatabase } from "./database.js";

const app = buildApp();
const database = await createDatabase();

try {
  await app.listen({ port: config.PORT, host: config.HOST });
  app.log.info({ persistence: database ? "postgresql" : "in-memory" }, "Persistence mode selected");
} catch (error) {
  app.log.error(error);
  process.exit(1);
}
