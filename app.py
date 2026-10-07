import base64, csv, hashlib, hmac, html, io, json, os, time
from pathlib import Path
from urllib.parse import urlencode, urlsplit
import streamlit as st
import streamlit.components.v1 as components
from tokens import create_token, verify_token
from storage import Store

ROOT=Path(__file__).parent
st.set_page_config(page_title='Hyperlands · Tu invitación',page_icon='💎',layout='centered')
def secret(name):
    if os.environ.get(name):return os.environ[name]
    try:return str(st.secrets.get(name,''))
    except Exception:return ''
def asset(name):
    f=ROOT/'assets'/name
    if not f.exists():return ''
    return 'data:'+('image/png' if f.suffix=='.png' else 'image/jpeg')+';base64,'+base64.b64encode(f.read_bytes()).decode()
def esc(value):return html.escape(str(value))

st.markdown("""<style>
.stApp{background:#090d18;color:#f3efe6}[data-testid="stHeader"]{background:transparent}
.block-container{padding-top:1.2rem;max-width:980px}.stButton>button{border:1px solid #c9a860;background:#211a33;color:#f9e9b8;border-radius:14px;min-height:48px}
</style>""",unsafe_allow_html=True)
KEY=secret('INVITE_SIGNING_KEY');ADMIN=secret('ADMIN_PASSWORD');BASE=secret('PUBLIC_BASE_URL')
DB_PATH=secret('RESPONSES_DB_PATH') or str(ROOT/'data/respuestas.sqlite3')

def store():return Store(DB_PATH)

def admin():
    st.title('💎 Taller de invitaciones')
    if len(KEY)<32 or len(ADMIN)<12:
        st.error('Configura las claves en Secrets: INVITE_SIGNING_KEY (32 caracteres mínimo) y ADMIN_PASSWORD (12 mínimo).');st.stop()
    if not st.session_state.get('admin_ok'):
        with st.form('login'):
            password=st.text_input('Contraseña',type='password');submit=st.form_submit_button('Entrar')
        if submit:
            if time.time()<st.session_state.get('login_after',0):st.error('Espera unos segundos antes de volver a intentarlo.')
            elif hmac.compare_digest(password.encode(),ADMIN.encode()):st.session_state.admin_ok=True;st.rerun()
            else:st.session_state.login_after=time.time()+3;st.error('Contraseña incorrecta.')
        st.stop()
    if st.button('Cerrar sesión'):st.session_state.admin_ok=False;st.rerun()
    create,answers=st.tabs(['Forjar invitación','Respuestas'])
    with create:
        base=st.text_input('Dirección pública de la app',value=BASE,placeholder='https://tu-app.streamlit.app')
        with st.form('invitation'):
            name=st.text_input('Nombre de Minecraft',max_chars=32)
            message=st.text_area('Mensaje personal de DevilJho',value='Quiero que seas parte de esta nueva aventura. Tu lugar en Hyperlands ya está reservado.',max_chars=1000)
            role=st.selectbox('Distinción decorativa',['Habitante fundador','Explorador de la isla','Constructor de historias','Guardián del cristal'])
            days=st.number_input('Caducidad en días (0 = sin caducidad)',0,365,0)
            make=st.form_submit_button('Forjar invitación ✨')
        if make:
            url=urlsplit(base.strip())
            if not name.strip():st.error('Escribe el nombre.')
            elif url.scheme not in ('http','https') or not url.netloc or url.query or url.fragment:st.error('Introduce una dirección http/https sin parámetros.')
            else:
                data={'name':name.strip(),'message':message.strip(),'role':role,'expires':int(time.time()+days*86400) if days else 0}
                token=create_token(data,KEY)
                try:store().register(token,data)
                except Exception:st.error('No se pudo registrar la invitación. Comprueba permisos de la base de datos.');st.stop()
                st.session_state.generated={'link':base.strip().rstrip('/')+'/?'+urlencode({'invite':token}),**data}
        if st.session_state.get('generated'):
            g=st.session_state.generated;st.success('Invitación creada. Guarda el enlace.');st.code(g['link'],language=None)
            st.download_button('Descargar enlace y mensaje',json.dumps(g,ensure_ascii=False,indent=2),file_name='invitacion_hyperlands.json',mime='application/json')
    with answers:
        st.caption('Las respuestas se guardan en SQLite en este equipo. Quien posea un enlace puede responder; no se verifica identidad.')
        st.warning('En Streamlit Community Cloud los archivos locales pueden perderse. Para producción usa almacenamiento persistente o una base de datos externa. Descarga copias de las respuestas.')
        st.button('Actualizar respuestas')
        try:rows=store().all()
        except Exception:st.error('No se pudo abrir la base de datos.');st.stop()
        a,b,c=st.columns(3)
        a.metric('Aceptadas',sum(r['status']=='aceptada' for r in rows));b.metric('Declinadas',sum(r['status']=='declinada' for r in rows));c.metric('Pendientes',sum(r['status']=='pendiente' for r in rows))
        view=[{'Nombre':r['name'],'Distinción':r['role'],'Respuesta':r['status'],'Actualizada (UTC)':r['updated_at']} for r in rows]
        st.dataframe(view,use_container_width=True,hide_index=True)
        buff=io.StringIO();writer=csv.DictWriter(buff,fieldnames=['Nombre','Distinción','Respuesta','Actualizada (UTC)']);writer.writeheader();writer.writerows(view)
        st.download_button('Exportar respuestas CSV',buff.getvalue().encode('utf-8-sig'),file_name='respuestas_hyperlands.csv',mime='text/csv')
    st.stop()

if st.query_params.get('admin')=='1':admin()
token=st.query_params.get('invite','')
if token:
    if len(KEY)<32:st.error('El administrador debe configurar la clave de invitaciones.');st.stop()
    try:data=verify_token(token,KEY)
    except Exception:st.error('Invitación inválida o caducada. Contacta con DevilJho.');st.stop()
    try:db=store();tid=db.register(token,data);response=db.get(tid)
    except Exception:st.error('No se puede guardar tu respuesta. Contacta con DevilJho.');st.stop()
else:
    data={'name':'Explorador','message':'Esta es una demostración. Las invitaciones reales llegan de forma individual.','role':'Vista previa'}
    tid='demo';response={'status':st.session_state.get('demo_status','pendiente')}
    st.caption('Modo demostración · No guarda respuestas reales')
identity=hashlib.sha256(token.encode()).hexdigest() if token else 'demo'
if st.session_state.get('identity')!=identity:st.session_state.identity=identity;st.session_state.step=0;st.session_state.confirm_decline=False
step=st.session_state.get('step',0)
name=esc(data['name']);message=esc(data.get('message','')).replace('\n','<br>');role=esc(data.get('role','Habitante fundador'))
logo=asset('logo.png');bg=asset('isla.jpg')
brand='<img class="logo" src="'+logo+'" alt="Hyperlands">' if logo else '<div class="brand">HYPERLANDS</div>'
content=[
 '<div class="eyebrow">UNA SEÑAL DESDE LA ISLA</div><h1>Hay algo esperando<br>por ti.</h1><p>Un sobre ha cruzado el mar.<br>Solo lleva un nombre.</p><div class="envelope"><div class="seal">✦</div></div><div class="recipient">'+name+'</div>',
 '<div class="eyebrow">EL CRISTAL HA RESPONDIDO</div><div class="crystal">◆</div><h1>'+name+',<br>la isla te llama.</h1><p>No es volver a lo de antes.<br>Es empezar algo completamente nuevo.</p><div class="chips"><span>Historia</span><span>Parcelas</span><span>Una nueva aventura</span></div>',
 '<div class="eyebrow">TU INVITACIÓN A HYPERLANDS</div><h1>Tu lugar está reservado,<br>'+name+'.</h1><div class="letter">'+message+'</div><div class="badge">✦ '+role+'</div><div class="date">Aún no hay fecha confirmada,<br><strong>pero ya falta poco.</strong><br><small>Te avisaremos cuando esté todo listo.</small></div><p>Nos vemos en la isla.<br><strong>DevilJho</strong></p><div class="closed">Invitación personal · Cupos completos · Sin inscripción pública</div>'
][step]
css="""*{box-sizing:border-box}body{margin:0;background:#090d18;color:#f5efdf;font-family:Georgia,serif}.scene{position:relative;min-height:690px;border:1px solid #75653d;border-radius:26px;overflow:hidden;text-align:center;padding:32px 24px;background:linear-gradient(180deg,#080d19b0,#080b18f5),url('BG') center/cover}.inner{position:relative;animation:reveal 1s ease}.brand{font:bold clamp(26px,6vw,42px) Georgia;letter-spacing:.12em;color:#e8d19a;text-shadow:0 0 25px #bb8e3a;margin:10px 0 34px}.logo{max-width:290px;max-height:120px;object-fit:contain;margin-bottom:25px}.eyebrow{font:11px Arial;letter-spacing:3px;color:#cfb989}h1{font-size:clamp(27px,5vw,42px);line-height:1.2;font-weight:normal;margin:24px 0}p{font-size:17px;line-height:1.8;color:#d2cbdc}.envelope{width:220px;height:125px;background:linear-gradient(135deg,#d8c292,#9d7e4c);margin:36px auto 20px;border:1px solid #f6dda5;border-radius:7px;position:relative;box-shadow:0 12px 60px #0009}.envelope:before{content:'';position:absolute;inset:0;clip-path:polygon(0 0,100% 0,50% 65%);background:#ead5a6}.seal{position:absolute;top:54px;left:89px;background:#5e326c;color:#f3d5ff;width:43px;height:43px;border-radius:50%;display:grid;place-items:center}.recipient{font-size:22px;color:#e9cf9c}.crystal{font-size:105px;color:#bf8cfa;text-shadow:0 0 35px #a159ed;animation:pulse 3s infinite}.chips{display:flex;gap:9px;justify-content:center;flex-wrap:wrap;margin:25px}.chips span{font:12px Arial;border:1px solid #806c99;padding:11px;border-radius:20px}.letter{max-width:580px;margin:24px auto;padding:24px;background:#efe0bc0d;border:1px solid #a0885a50;border-radius:14px;font-size:18px;line-height:1.8;overflow-wrap:anywhere}.badge{color:#e6c47f;border:1px solid #9d824c;border-radius:20px;padding:9px 18px;display:inline-block;font:12px Arial}.date{margin:26px auto 12px;line-height:1.7;color:#e4d6f6;font-size:17px}.date small{font:12px Arial;color:#aaa0b6}.closed{font:11px Arial;color:#aaa0b6}.motes{position:absolute;inset:0;pointer-events:none}.motes i{position:absolute;width:3px;height:3px;background:#e3c582;border-radius:50%;animation:float 8s infinite;box-shadow:0 0 8px #f9da96}@keyframes float{0%{transform:translateY(80px);opacity:0}40%{opacity:.8}100%{transform:translateY(-140px);opacity:0}}@keyframes reveal{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}@keyframes pulse{50%{transform:scale(1.06)}}@media(prefers-reduced-motion:reduce){*{animation:none!important}}""".replace('BG',bg)
motes=''.join('<i style="left:'+str((i*37)%100)+'%;top:'+str((i*23)%100)+'%;animation-delay:-'+str(i%8)+'s"></i>' for i in range(24))
scene='<!doctype html><html lang="es"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style></head><body><section class="scene"><div class="motes">'+motes+'</div><div class="inner">'+brand+content+'</div></section></body></html>'
# Compatibility with the new iframe API, retaining the old fallback for older versions.
if hasattr(st, "iframe"):
    st.iframe(scene, height="content")
else:
    components.html(
        scene,
        height=720 if step < 2 else 1100,
        scrolling=True,
    )

def save(status):
    if token:
        try:db.respond(tid,status)
        except Exception:st.error('No se pudo guardar. Tu respuesta no ha sido registrada.');return
    else:st.session_state.demo_status=status
    st.session_state.confirm_decline=False;st.rerun()

if step<2:
    if st.button(['Romper el sello ✦','Revelar mi invitación ◆'][step],use_container_width=True):st.session_state.step=step+1;st.rerun()
else:
    status=response['status']
    if status=='aceptada':st.success('¡Invitación aceptada! Tu respuesta ha quedado registrada.' if token else 'Demostración: invitación aceptada.')
    elif status=='declinada':st.info('Has declinado la invitación. Gracias por responder.' if token else 'Demostración: invitación declinada.')
    else:st.write('**¿Te unes a esta aventura?**')
    if status!='pendiente':st.caption('Puedes cambiar tu respuesta desde este mismo enlace. No se envía ninguna notificación automática.')
    a,b=st.columns(2)
    with a:
        if st.button('✨ Aceptar invitación',disabled=status=='aceptada',use_container_width=True):save('aceptada')
    with b:
        if st.button('Declinar invitación',disabled=status=='declinada',use_container_width=True):st.session_state.confirm_decline=True
    if st.session_state.get('confirm_decline'):
        st.warning('¿Seguro que quieres declinar? Puedes cambiar tu respuesta más adelante.')
        a,b=st.columns(2)
        with a:
            if st.button('Sí, declinar'):save('declinada')
        with b:
            if st.button('Volver'):st.session_state.confirm_decline=False;st.rerun()
    st.download_button('Guardar mi invitación','HYPERLANDS\n\nPara: '+data['name']+'\n'+data.get('message','')+'\n\nAún no hay fecha confirmada, pero ya falta poco.\nFirmado: DevilJho',file_name='Mi_invitacion_Hyperlands.txt')
    if st.button('Volver a abrirla'):st.session_state.step=0;st.rerun()
track=ROOT/'assets/tema.ogg'
if track.exists():
    with st.expander('♫ El corazón de Hyperlands'):st.audio(track.read_bytes(),format='audio/ogg')
