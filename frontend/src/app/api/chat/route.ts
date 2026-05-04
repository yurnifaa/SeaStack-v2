import { GoogleGenerativeAI } from "@google/generative-ai";
import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";

const MAX_RULES_BYTES = 12_000;
const MAX_EXAMPLES_PER_QUERY = 3;
const MAX_EXAMPLES_BYTES = 20_000;

function loadRules(): string {
  try {
    const rulesPath = path.join(process.cwd(), "..", "seastack-llm.md");
    const buffer = Buffer.alloc(MAX_RULES_BYTES);
    const fd = fs.openSync(rulesPath, "r");
    const bytesRead = fs.readSync(fd, buffer, 0, MAX_RULES_BYTES, 0);
    fs.closeSync(fd);
    return buffer.slice(0, bytesRead).toString("utf8");
  } catch {
    return "(seastack-llm.md not found — using built-in knowledge only)";
  }
}

type Example = { num: string; title: string; code: string };

// Parses CSV with quoted multi-line fields and "" escapes
function parseCsv(raw: string): string[][] {
  const rows: string[][] = [];
  let cur: string[] = [];
  let field = "";
  let inQuotes = false;
  for (let i = 0; i < raw.length; i++) {
    const c = raw[i];
    if (inQuotes) {
      if (c === '"' && raw[i + 1] === '"') { field += '"'; i++; }
      else if (c === '"') inQuotes = false;
      else field += c;
    } else {
      if (c === '"') inQuotes = true;
      else if (c === ",") { cur.push(field); field = ""; }
      else if (c === "\n") { cur.push(field); rows.push(cur); cur = []; field = ""; }
      else if (c === "\r") { /* skip */ }
      else field += c;
    }
  }
  if (field.length || cur.length) { cur.push(field); rows.push(cur); }
  return rows;
}

function loadExamples(): Example[] {
  try {
    const csvPath = path.join(process.cwd(), "..", "program.csv");
    const raw = fs.readFileSync(csvPath, "utf8");
    const rows = parseCsv(raw);
    const out: Example[] = [];
    for (const row of rows) {
      if (row.length < 3) continue;
      const num = row[0].trim();
      const title = row[1].trim();
      const code = row[2].trim();
      if (!/^\d+$/.test(num) || !title || !code) continue;
      out.push({ num, title, code });
    }
    return out;
  } catch {
    return [];
  }
}

const RULES_CONTENT = loadRules();
const EXAMPLES = loadExamples();

function findRelevantExamples(query: string, n: number): Example[] {
  if (EXAMPLES.length === 0) return [];
  const q = query.toLowerCase();
  const terms = Array.from(new Set(q.split(/\W+/).filter((t) => t.length > 2)));
  const numMatch = q.match(/(?:program|example|#|number|no\.?)\s*(\d+)/);
  const askedNum = numMatch ? numMatch[1] : null;

  const scored = EXAMPLES.map((e) => {
    const hay = (e.title + " " + e.code).toLowerCase();
    let score = 0;
    for (const t of terms) if (hay.includes(t)) score++;
    if (askedNum && askedNum === e.num) score += 100;
    return { e, score };
  });

  return scored
    .filter((s) => s.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, n)
    .map((s) => s.e);
}

function buildExamplesBlock(query: string): string {
  const picks = findRelevantExamples(query, MAX_EXAMPLES_PER_QUERY);
  if (picks.length === 0) return "";
  let block = "\n\n=== RELEVANT SEASTACK EXAMPLE PROGRAMS ===\n";
  for (const e of picks) {
    const entry = `\n# Program ${e.num}: ${e.title}\n${e.code}\n`;
    if (block.length + entry.length > MAX_EXAMPLES_BYTES) break;
    block += entry;
  }
  block += "\n=== END EXAMPLES ===";
  return block;
}

const BASE_SYSTEM_PROMPT = `You are a helpful AI assistant secretly embedded inside the SeaStack IDE. SeaStack is a custom programming language with the full specification provided below. Answer questions about SeaStack accurately using the spec. Be concise and conversational — the chat panel is small, so keep responses short unless the user needs detail.

=== SEASTACK LANGUAGE SPECIFICATION ===
${RULES_CONTENT}
=== END OF SPECIFICATION ===`;

export async function POST(req: NextRequest) {
  if (!process.env.GEMINI_API_KEY) {
    return NextResponse.json(
      { error: "GEMINI_API_KEY is not set in .env.local" },
      { status: 500 }
    );
  }

  try {
    const { messages } = await req.json();

    const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
    const lastMessage = messages[messages.length - 1];
    const systemInstruction = BASE_SYSTEM_PROMPT + buildExamplesBlock(lastMessage?.content ?? "");

    const model = genAI.getGenerativeModel({
      model: "gemini-2.5-flash",
      systemInstruction,
    });

    // Convert messages to Gemini format — role "assistant" becomes "model"
    const history = messages.slice(0, -1).map((m: { role: string; content: string }) => ({
      role: m.role === "assistant" ? "model" : "user",
      parts: [{ text: m.content }],
    }));

    const chat = model.startChat({ history });
    const result = await chat.sendMessage(lastMessage.content);
    const content = result.response.text();

    return NextResponse.json({ content });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : "Unknown error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
