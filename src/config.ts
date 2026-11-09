import { z } from "zod";

const configSchema = z.object({
  PORT: z.coerce.number().int().positive().default(3000),
  HOST: z.string().default("0.0.0.0"),
  DATABASE_URL: z.string().url().optional()
});

export const config = configSchema.parse({
  PORT: process.env.PORT,
  HOST: process.env.HOST,
  DATABASE_URL: process.env.DATABASE_URL
});
