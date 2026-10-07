"""Personalised invitation: existing background + typography. No external services."""
import hashlib, io
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT=Path(__file__).parent
OPENINGS=[
 'Hay lugares que no se encuentran en un mapa, sino en las personas que deciden quedarse.',
 'No todas las luces nacen del cielo. Algunas empiezan cuando alguien se atreve a construir.',
 'Una isla puede estar rodeada de mar y, aun así, convertirse en el lugar donde dejas de sentirte lejos.',
 'Las historias más grandes no comienzan con una corona, sino con alguien que da el primer paso.',
 'Incluso cuando la tierra tiembla, hay algo que ninguna sombra puede llevarse: lo que construimos juntos.',
 'Hay puertas que no llevan a otro lugar, sino a una versión de nosotros que todavía no conocemos.',
 'El mundo puede guardar secretos bajo sus piedras. Nosotros guardaremos recuerdos sobre ellas.',
 'Volver a empezar no es borrar el pasado. Es darle un lugar desde el que seguir creciendo.'
]
MIDDLES=[
 'Aquí, tu nombre no será una visita: será parte de la memoria de la isla.',
 'Entre cristales, caminos y noches compartidas, habrá un rincón que solo tú podrás convertir en hogar.',
 'Lo que hoy parece un pequeño comienzo puede convertirse en el recuerdo al que siempre quieras volver.',
 'Cada paso que des dejará algo más que una huella: abrirá un camino para quienes vengan contigo.',
 'No sabemos qué despertará bajo la isla, pero sí quiénes queremos tener a nuestro lado cuando ocurra.',
 'No necesitas llegar con todas las respuestas. Basta con traer las ganas de descubrirlas con nosotros.',
 'Tu parcela será un comienzo. Las personas que encuentres harán que signifique mucho más.',
 'El valor de este mundo no estará en sus tesoros, sino en las historias que vivamos dentro de él.'
]
ENDINGS=[
 'Cuando el cristal vuelva a brillar, habrá un lugar esperando por ti.',
 'Que esta invitación sea el primer recuerdo de una aventura que merezca quedarse.',
 'La isla todavía está despertando. Su próxima historia también llevará tu nombre.',
 'Si la oscuridad llama a nuestra puerta, que nos encuentre construyendo juntos.',
 'No vienes a ocupar un espacio. Vienes a darle significado.',
 'El horizonte aún guarda silencio. Nosotros ya estamos preparando tu llegada.',
 'Donde otros ven bloques, nosotros queremos encontrar un hogar.',
 'Nos vemos donde terminan los mapas y empiezan las historias.'
]
def story(data):
    # Different names always produce different full texts, even if fragments coincide.
    name=str(data['name'])
    h=hashlib.sha256(name.casefold().encode()).digest()
    return OPENINGS[h[0]%8]+'\n\n'+name+', '+MIDDLES[h[1]%8][0].lower()+MIDDLES[h[1]%8][1:]+'\n\n'+ENDINGS[h[2]%8]

def font(size,bold=False):
    return ImageFont.truetype(str(ROOT/'assets/fonts'/('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf')),size)

def lines(text,draw,f,width):
    out=[]
    for para in text.split('\n'):
        if not para:out.append('');continue
        line=''
        for word in para.split():
            candidate=(line+' '+word).strip()
            if draw.textbbox((0,0),candidate,font=f)[2]>width and line:out.append(line);line=word
            else:line=candidate
        if line:out.append(line)
    return out

def make_card(data):
    W,H=1600,1000
    bg=ROOT/'assets/isla.jpg'
    im=ImageOps.fit(Image.open(bg).convert('RGB'),(W,H),method=Image.Resampling.LANCZOS).convert('RGBA') if bg.exists() else Image.new('RGBA',(W,H),'#090d18')
    # Darken the existing photo for readable typography; never generate a new background.
    overlay=Image.new('RGBA',(W,H),(6,9,22,155));im=Image.alpha_composite(im,overlay)
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((40,40,W-40,H-40),radius=28,outline=(210,181,119,220),width=3)
    d.rounded_rectangle((66,66,W-66,H-66),radius=20,outline=(180,142,91,110),width=1)
    def centered(text,y,f,fill):
        box=d.textbbox((0,0),text,font=f);width=box[2]-box[0]
        d.text(((W-width)/2,y),text,font=f,fill=fill,stroke_width=1,stroke_fill=(8,9,18,150))
    centered('HYPERLANDS REBORN',104,font(65,True),'#efd59b')
    centered('UNA HISTORIA QUE TAMBIÉN LLEVARÁ TU NOMBRE',192,font(21),'#d6c9e7')
    name=str(data['name']);size=96
    while size>20 and d.textbbox((0,0),name,font=font(size,True))[2]>W-200:size-=2
    centered(name,258,font(size,True),'#ffffff')
    d.line((490,390,1110,390),fill='#cba66b',width=2)
    text=story(data);f=font(28);wrapped=lines(text,d,f,1160)
    while len(wrapped)*41>330:
        f=font(f.size-1);wrapped=lines(text,d,f,1160)
    y=425
    for line in wrapped:
        centered(line,y,f,'#eee6f5');y+=f.size+13
    centered('Aún no hay fecha confirmada, pero ya falta poco.',822,font(24,True),'#e6c589')
    centered('Tu lugar está reservado. Nos vemos en la isla.',866,font(23),'#d7ccdf')
    centered('DEVILJHO  ·  INVITACIÓN PERSONAL',914,font(19,True),'#c7ad79')
    out=io.BytesIO();im.convert('RGB').save(out,format='PNG',optimize=True);return out.getvalue()
