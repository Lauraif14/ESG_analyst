import Fastify from "fastify";
import cors from "@fastify/cors";
import { z } from "zod";

const idSchema = z.string().min(1);

const companySchema = z.object({
  id: idSchema,
  name: z.string().min(1),
  ticker: z.string().min(1),
  commodity: z.string().min(1),
  country: z.string().min(1)
});

const indicatorSchema = z.object({
  id: idSchema,
  code: z.string().min(1),
  name: z.string().min(1),
  dimension: z.enum(["E", "S", "G"]),
  unit: z.string().nullable()
});

const esgRecordSchema = z.object({
  id: idSchema,
  companyId: idSchema,
  indicatorId: idSchema,
  period: z.string().regex(/^\d{4}$/, "period must use YYYY format"),
  numericValue: z.number().finite().nullable(),
  textValue: z.string().nullable(),
  unit: z.string().nullable(),
  dataStatus: z.enum(["REPORTED", "NOT_DISCLOSED", "NOT_APPLICABLE", "PENDING_REVIEW"]),
  sourceDocument: z.string().min(1).nullable()
});

type Company = z.infer<typeof companySchema>;
type Indicator = z.infer<typeof indicatorSchema>;
type EsgRecord = z.infer<typeof esgRecordSchema>;

const companies: Company[] = [
  { id: "company-vale", name: "PT Vale Indonesia Tbk", ticker: "INCO", commodity: "Nickel", country: "Indonesia" },
  { id: "company-antam", name: "PT Aneka Tambang Tbk", ticker: "ANTM", commodity: "Nickel and Gold", country: "Indonesia" },
  { id: "company-ptba", name: "PT Bukit Asam Tbk", ticker: "PTBA", commodity: "Coal", country: "Indonesia" }
];

const indicators: Indicator[] = [
  { id: "indicator-e01", code: "E01", name: "Scope 1 GHG emissions", dimension: "E", unit: "tCO2e" },
  { id: "indicator-e02", code: "E02", name: "Energy consumption", dimension: "E", unit: "GJ" },
  { id: "indicator-e03", code: "E03", name: "Water withdrawal", dimension: "E", unit: "ML" }
];

const esgRecords: EsgRecord[] = [];

function validationError(reply: { code: (statusCode: number) => { send: (body: unknown) => unknown } }, issues: unknown) {
  return reply.code(400).send({ error: { code: "VALIDATION_ERROR", message: "Request validation failed", details: issues } });
}

export function buildApp() {
  const app = Fastify({ logger: true });

  app.register(cors, { origin: true });

  app.get("/api/v1/health", async () => ({ status: "ok", service: "esg-mining-intelligence-system" }));

  app.get("/api/v1/companies", async () => ({ data: companies, meta: { total: companies.length } }));

  app.get<{ Params: { id: string } }>("/api/v1/companies/:id", async (request, reply) => {
    const company = companies.find((item) => item.id === request.params.id);
    if (!company) return reply.code(404).send({ error: { code: "COMPANY_NOT_FOUND", message: "Company not found" } });
    return { data: company };
  });

  app.get<{ Querystring: { dimension?: string } }>("/api/v1/indicators", async (request, reply) => {
    if (request.query.dimension && !["E", "S", "G"].includes(request.query.dimension)) {
      return reply.code(400).send({ error: { code: "INVALID_DIMENSION", message: "dimension must be E, S, or G" } });
    }
    const data = request.query.dimension
      ? indicators.filter((indicator) => indicator.dimension === request.query.dimension)
      : indicators;
    return { data, meta: { total: data.length } };
  });

  app.post<{ Body: unknown }>("/api/v1/esg-records", async (request, reply) => {
    const parsed = esgRecordSchema.safeParse(request.body);
    if (!parsed.success) return validationError(reply, parsed.error.issues);
    if (!companies.some((company) => company.id === parsed.data.companyId)) {
      return reply.code(400).send({ error: { code: "COMPANY_NOT_FOUND", message: "companyId does not exist" } });
    }
    if (!indicators.some((indicator) => indicator.id === parsed.data.indicatorId)) {
      return reply.code(400).send({ error: { code: "INDICATOR_NOT_FOUND", message: "indicatorId does not exist" } });
    }
    esgRecords.push(parsed.data);
    return reply.code(201).send({ data: parsed.data });
  });

  app.get<{ Querystring: { companyId?: string; period?: string } }>("/api/v1/esg-records", async (request) => {
    const data = esgRecords.filter((record) =>
      (!request.query.companyId || record.companyId === request.query.companyId) &&
      (!request.query.period || record.period === request.query.period)
    );
    return { data, meta: { total: data.length } };
  });

  app.get<{ Querystring: { companyId?: string; period?: string } }>("/api/v1/dashboard/summary", async (request) => {
    const filtered = esgRecords.filter((record) =>
      (!request.query.companyId || record.companyId === request.query.companyId) &&
      (!request.query.period || record.period === request.query.period)
    );
    return {
      data: {
        companies: companies.length,
        records: filtered.length,
        reportedRecords: filtered.filter((record) => record.dataStatus === "REPORTED").length,
        byDimension: indicators.reduce<Record<string, number>>((summary, indicator) => {
          summary[indicator.dimension] = (summary[indicator.dimension] ?? 0) + filtered.filter((record) => record.indicatorId === indicator.id).length;
          return summary;
        }, {})
      }
    };
  });

  return app;
}
