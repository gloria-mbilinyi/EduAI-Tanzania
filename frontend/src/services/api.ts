export type Row = Record<string, any>
export const token = () => sessionStorage.getItem('eduai-token')
export async function api<T = any>(path: string, options: RequestInit = {}): Promise<T> {
  const headers: Record<string,string> = {...(token() ? {Authorization:`Bearer ${token()}`} : {}), ...(options.body && !(options.body instanceof FormData) ? {'Content-Type':'application/json'} : {})}
  const response = await fetch(`/api${path}`, {...options, headers:{...headers,...options.headers}})
  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    const message = typeof error.detail === 'string' ? error.detail : Array.isArray(error.detail) ? error.detail.map((x:Row)=>`${x.loc.slice(1).join('.')}: ${x.msg}`).join('; ') : 'Service unavailable. Please try again.'
    throw new Error(message)
  }
  if (response.status === 204) return undefined as T
  return response.headers.get('content-type')?.includes('application/json') ? response.json() : response.text() as T
}
export const post = (path:string, body:unknown = {}) => api(path,{method:'POST',body:JSON.stringify(body)})
export const patch = (path:string, body:unknown) => api(path,{method:'PATCH',body:JSON.stringify(body)})
export function refresh(){window.dispatchEvent(new Event('eduai-refresh'))}
export async function download(path:string, name:string){
  const response=await fetch(`/api${path}`,{headers:{Authorization:`Bearer ${token()}`}})
  if(!response.ok)throw new Error('Download unavailable or access denied')
  const url=URL.createObjectURL(await response.blob());const a=document.createElement('a');a.href=url;a.download=name;a.click();URL.revokeObjectURL(url)
}
