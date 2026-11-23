import {ReactNode,useState,FormEvent} from 'react'
import {useI18n} from '../i18n'
import {refresh} from '../services/api'
export function Badge({children}:{children:ReactNode}){return <span className={`badge ${String(children).replaceAll(' ','-')}`}>{children}</span>}
export function Panel({title,children,action}:{title?:string;children:ReactNode;action?:ReactNode}){return <section className="panel">{title&&<div className="panel-heading"><h2>{title}</h2>{action}</div>}{children}</section>}
export function Notice({children,error=false}:{children:ReactNode;error?:boolean}){return children?<div className={`notice ${error?'error':''}`} role={error?'alert':'status'}>{children}</div>:null}
export function Empty(){const {t}=useI18n();return <p className="empty">{t('No records yet.')}</p>}
export function Field({label,children}:{label:string;children:ReactNode}){const {t}=useI18n();return <label className="field"><span>{t(label)}</span>{children}</label>}
export function ActionForm({children,onSubmit,label='Submit',className=''}:{children:ReactNode;onSubmit:(form:FormData)=>Promise<unknown>;label?:string;className?:string}){
  const {t}=useI18n(),[busy,setBusy]=useState(false),[message,setMessage]=useState(''),[error,setError]=useState(false)
  async function submit(e:FormEvent<HTMLFormElement>){e.preventDefault();const data=new FormData(e.currentTarget);setBusy(true);setMessage('');try{await onSubmit(data);setError(false);setMessage(t('Save changes')+' ✓');refresh()}catch(e){setError(true);setMessage((e as Error).message)}finally{setBusy(false)}}
  return <form onSubmit={submit} className={`form-stack ${className}`}>{children}<Notice error={error}>{message}</Notice><button className="button" disabled={busy}>{busy?'…':t(label)}</button></form>
}
export function ActionButton({children,onClick,className='button secondary'}:{children:ReactNode;onClick:()=>Promise<unknown>;className?:string}){
 const [busy,setBusy]=useState(false),[error,setError]=useState('');return <><button className={className} disabled={busy} onClick={async()=>{setBusy(true);setError('');try{await onClick();refresh()}catch(e){setError((e as Error).message)}finally{setBusy(false)}}}>{busy?'…':children}</button>{error&&<Notice error>{error}</Notice>}</>
}
