import { NextResponse } from "next/server";

// BACKEND_URL is set for server-side (Docker internal network: http://backend:8000)
// Falls back to localhost for running outside Docker
const BACKEND_URL = process.env.BACKEND_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/**
 * POST /api/trigger-ingestion
 * Calls the FastAPI backend which publishes a job to RabbitMQ.
 * The frontend calls this route so it never talks to the backend directly
 * from the browser for admin actions.
 */
export async function POST(request: Request) {
  try {
    const authHeader = request.headers.get("Authorization");

    const res = await fetch(`${BACKEND_URL}/trigger-ingestion`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(authHeader ? { Authorization: authHeader } : {}),
      },
    });

    const data = await res.json();

    if (!res.ok) {
      return NextResponse.json(data, { status: res.status });
    }

    return NextResponse.json(data);
  } catch (err) {
    return NextResponse.json(
      { error: "Failed to reach backend", detail: String(err) },
      { status: 502 }
    );
  }
}
