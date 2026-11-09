import type { Pool } from "pg";

export type Database = Pool | null;

export async function createDatabase(): Promise<Database> {
  if (!process.env.DATABASE_URL) return null;

  const { Pool: PgPool } = await import("pg");
  return new PgPool({ connectionString: process.env.DATABASE_URL });
}
