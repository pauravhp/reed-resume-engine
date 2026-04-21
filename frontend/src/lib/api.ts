const BASE = import.meta.env.VITE_API_URL

function authHeaders(): HeadersInit {
  const token = localStorage.getItem("access_token") ?? ""
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  }
}

function handle401(status: number) {
  if (status === 401 || status === 403) {
    localStorage.removeItem("access_token")
    window.location.href = "/login"
  }
}

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { headers: authHeaders() })
  handle401(res.status)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function apiPost<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: authHeaders(),
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })
  handle401(res.status)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function apiPut<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "PUT",
    headers: authHeaders(),
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })
  handle401(res.status)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function apiPatch<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "PATCH",
    headers: authHeaders(),
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })
  handle401(res.status)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function apiDelete(path: string): Promise<void> {
  const res = await fetch(`${BASE}${path}`, {
    method: "DELETE",
    headers: authHeaders(),
  })
  handle401(res.status)
  if (!res.ok) throw new Error(await res.text())
}
