import {useCallback,useEffect,useState} from 'react'
import {api} from '../services/api'
export function useLoad<T=any>(path:string|null){
  const [data,setData]=useState<T|null>(null),[error,setError]=useState(''),[loading,setLoading]=useState(true),[version,setVersion]=useState(0)
  const reload=useCallback(()=>setVersion(x=>x+1),[])
  useEffect(()=>{window.addEventListener('eduai-refresh',reload);return()=>window.removeEventListener('eduai-refresh',reload)},[reload])
  useEffect(()=>{let live=true;setError('');setLoading(true);if(!path){setData(null);setLoading(false);return}
    api<T>(path).then(x=>{if(live)setData(x)}).catch(e=>{if(live)setError(e.message)}).finally(()=>{if(live)setLoading(false)})
    return()=>{live=false}
  },[path,version])
  return {data,error,loading,reload}
}
